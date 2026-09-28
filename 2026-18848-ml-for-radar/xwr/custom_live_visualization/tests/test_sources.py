"""Frame sources: UDP reassembly and the synthetic generator."""

from __future__ import annotations

import socket

import numpy as np

from radarviz.capture import FrameReceiver
from radarviz.config import RadarConfig
from radarviz.sources import SimulatedSource


class FakeSocket:
    """Replays a canned list of packets, then behaves like an idle socket."""

    def __init__(self, packets: list[bytes]):
        self.packets = list(packets)

    def recv_into(self, view) -> int:
        if not self.packets:
            raise socket.timeout()
        packet = self.packets.pop(0)
        view[:len(packet)] = packet
        return len(packet)


def packet(byte_count: int, payload: bytes, sequence: int = 0) -> bytes:
    """A DCA1000EVM data packet: 4-byte sequence, 6-byte running byte count."""
    return (sequence.to_bytes(4, "little")
            + byte_count.to_bytes(6, "little") + payload)


def collect(packets: list[bytes], frame_size: int):
    """Run a `FrameReceiver` over canned packets and return the frames."""
    frames: list[tuple[bytes, int]] = []
    receiver = FrameReceiver(
        FakeSocket(packets), frame_size,
        lambda data, ts, dropped: frames.append((data, dropped)))
    receiver.run()                      # synchronous: no thread needed
    return frames, receiver


def test_contiguous_packets_reassemble_into_frames() -> None:
    payload = bytes(range(10))
    packets = [packet(i * 10, payload) for i in range(4)]
    frames, receiver = collect(packets, frame_size=20)
    assert [d for _, d in frames] == [0, 0]
    assert frames[0][0] == payload * 2
    assert receiver.dropped_bytes == 0


def test_a_missing_packet_is_zero_filled_and_reported() -> None:
    payload = bytes([7]) * 10
    # Byte counts 0, 10, then a jump to 30: ten bytes never arrived.
    packets = [packet(0, payload), packet(10, payload), packet(30, payload)]
    frames, receiver = collect(packets, frame_size=10)
    assert receiver.dropped_bytes == 10
    assert sum(d for _, d in frames) == 10
    assert frames[2][0] == bytes(10), "the gap is zero-filled"


def test_an_out_of_order_packet_is_dropped_not_misplaced() -> None:
    payload = bytes([3]) * 10
    packets = [packet(20, payload), packet(30, payload),
               packet(10, payload),           # arrives late, already passed
               packet(40, payload)]
    frames, receiver = collect(packets, frame_size=10)
    assert receiver.out_of_order == 1
    assert len(frames) == 3


def test_alignment_snaps_to_a_frame_boundary() -> None:
    """A capture joined mid-stream starts at the next whole frame."""
    payload = bytes([1]) * 10
    packets = [packet(25, payload), packet(35, payload), packet(45, payload)]
    frames, receiver = collect(packets, frame_size=20)
    # Aligns to byte 20, so bytes 20-24 count as dropped.
    assert receiver.dropped_bytes == 5
    assert len(frames) == 1


def test_receiver_stops_when_asked() -> None:
    payload = bytes(10)
    packets = [packet(i * 10, payload) for i in range(100)]
    receiver = FrameReceiver(
        FakeSocket(packets), 10, lambda *a: None)
    receiver.stop()
    receiver.run()
    assert receiver.packets == 0


def test_simulated_source_produces_correctly_shaped_frames(
    radar_cfg: RadarConfig,
) -> None:
    source = SimulatedSource(radar_cfg, noise=0.0, realtime=False)
    source.start()
    frame = source.get(0)
    assert frame is not None
    assert frame.data.shape == radar_cfg.raw_shape
    assert frame.data.dtype == np.int16
    assert frame.index == 0
    assert frame.dropped_bytes == 0
    assert source.backlog() == 0
    assert source.get(0).index == 1
    source.stop()


def test_simulated_source_is_reproducible_for_a_given_seed(
    radar_cfg: RadarConfig,
) -> None:
    a = SimulatedSource(radar_cfg, realtime=False, seed=7).get(0)
    b = SimulatedSource(radar_cfg, realtime=False, seed=7).get(0)
    assert a is not None and b is not None
    assert np.array_equal(a.data, b.data)


def test_simulated_targets_drift_with_their_velocity(
    radar_cfg: RadarConfig,
) -> None:
    source = SimulatedSource(
        radar_cfg, targets=[(1.0, 1.0, 0.0, 0.0, 1000.0)], noise=0.0,
        realtime=False)
    first = source.get(0)
    for _ in range(20):
        last = source.get(0)
    assert first is not None and last is not None
    assert not np.array_equal(first.data, last.data)
