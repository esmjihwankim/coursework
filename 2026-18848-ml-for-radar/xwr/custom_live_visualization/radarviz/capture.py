"""DCA1000EVM capture card: control channel + raw UDP frame assembly.

Two independent pieces: `DCA1000EVM` owns the sockets and the card's little
command protocol, and `FrameReceiver` turns the resulting packet stream back
into fixed-size radar frames on its own thread.
"""

from __future__ import annotations

import logging
import socket
import struct
import threading
import time
from typing import Callable

from .config import CaptureConfig

log = logging.getLogger(__name__)


class CaptureError(Exception):
    """The capture card returned a non-zero status."""


class DCA1000EVM:
    """DCA1000EVM control (UDP :4096) and raw data reception (UDP :4098).

    Control protocol (little endian): `A55A | cmd | len | payload | EEAA`.
    Data packets: 4-byte sequence number, 6-byte running byte count, then up
    to 1456 bytes of payload. The byte count is what lets us detect and
    zero-fill dropped packets without losing frame alignment.
    """

    HEADER, FOOTER = 0xA55A, 0xEEAA
    CMD_RESET_AR_DEV = 0x02
    CMD_CONFIG_FPGA = 0x03
    CMD_START_RECORD = 0x05
    CMD_STOP_RECORD = 0x06
    CMD_SYSTEM_ALIVENESS = 0x09
    CMD_CONFIG_RECORD = 0x0B
    CMD_READ_FPGA_VERSION = 0x0E
    MAX_PACKET = 2048

    def __init__(self, cfg: CaptureConfig):
        self.cfg = cfg
        self.control = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.control.bind((cfg.sys_ip, cfg.config_port))
        self.control.settimeout(cfg.timeout)

        self.data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.data.setsockopt(
            socket.SOL_SOCKET, socket.SO_RCVBUF, cfg.socket_buffer)
        self.data.bind((cfg.sys_ip, cfg.data_port))
        self.data.settimeout(cfg.timeout)

        actual = self.data.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        log.info(
            "DCA1000EVM sockets bound on %s (recv buffer %d KiB)",
            cfg.sys_ip, actual // 1024)

    # -- control channel ---------------------------------------------------

    def _request(self, cmd: int, payload: bytes = b"", desc: str = "") -> int:
        packet = struct.pack(
            f"<HHH{len(payload)}sH",
            self.HEADER, cmd, len(payload), payload, self.FOOTER)
        self.control.sendto(packet, (self.cfg.fpga_ip, self.cfg.config_port))
        raw, _ = self.control.recvfrom(self.MAX_PACKET)
        header, _code, status, footer = struct.unpack_from("<HHHH", raw)
        if header != self.HEADER or footer != self.FOOTER:
            raise CaptureError(f"Malformed response to {desc or hex(cmd)}")
        if desc and status != 0 and cmd != self.CMD_READ_FPGA_VERSION:
            raise CaptureError(f"{desc} failed (status={status})")
        return status

    def setup(self) -> None:
        """Ping, read the FPGA version, and configure record + FPGA modes."""
        self._request(self.CMD_SYSTEM_ALIVENESS, desc="aliveness check")

        version = self._request(self.CMD_READ_FPGA_VERSION)
        log.info(
            "FPGA version %d.%d (%s mode)", version & 0x7F,
            (version >> 7) & 0x7F,
            "playback" if version & 0x4000 else "record")

        # Packet delay is programmed in units of the 8 ns FPGA clock, scaled
        # by 1000; 5 us is the minimum and gives the highest throughput.
        delay = int(self.cfg.delay * 1000 / 8)
        self._request(
            self.CMD_CONFIG_RECORD, struct.pack("<HHH", 1470, delay, 0),
            desc="configure record")

        # raw mode | 2 LVDS lanes | capture | ethernet stream | 16 bit | timer
        self._request(
            self.CMD_CONFIG_FPGA, struct.pack("<BBBBBB", 1, 2, 1, 2, 3, 30),
            desc="configure FPGA")

        # The FPGA ignores requests for a moment after being configured.
        for _ in range(30):
            try:
                self._request(self.CMD_SYSTEM_ALIVENESS)
                break
            except (TimeoutError, socket.timeout):
                continue
        else:
            raise CaptureError("FPGA stopped responding after configuration.")
        log.info("Capture card configured.")

    def start(self) -> None:
        """Begin streaming raw ADC data."""
        self._request(self.CMD_START_RECORD, desc="start record")

    def stop(self) -> None:
        """Stop streaming; safe to call when already stopped."""
        try:
            self._request(self.CMD_STOP_RECORD, desc="stop record")
        except (CaptureError, TimeoutError, socket.timeout) as exc:
            log.debug("stop record: %s", exc)

    def reset_radar(self) -> None:
        """Reboot the radar via the capture card's reset line."""
        self._request(self.CMD_RESET_AR_DEV, desc="reset radar")

    def flush(self) -> None:
        """Drain anything left in the data socket from a previous run."""
        self.data.settimeout(0.0)
        discarded = 0
        try:
            while discarded < 1_000_000:      # bounded: never wedge startup
                if not self.data.recv(self.MAX_PACKET):
                    break
                discarded += 1
        except (BlockingIOError, socket.timeout, TimeoutError):
            pass
        if discarded:
            log.debug("Flushed %d stale packets.", discarded)
        self.data.settimeout(self.cfg.timeout)

    def close(self) -> None:
        """Close both sockets."""
        for sock in (self.control, self.data):
            try:
                sock.close()
            except Exception:  # noqa: BLE001 - best-effort teardown
                pass


class FrameReceiver(threading.Thread):
    """Reassembles fixed-size radar frames from the DCA1000EVM UDP stream.

    Runs in its own thread and hands each completed frame to `on_frame`
    immediately, so a slow consumer never stalls packet reception (the
    consumer is responsible for dropping frames it cannot keep up with).

    Args:
        sock: bound data socket.
        frame_size: bytes per radar frame.
        on_frame: called as `on_frame(data, timestamp, dropped_bytes)`.
        timeout: seconds of silence after which the stream is considered over.
    """

    def __init__(
        self, sock: socket.socket, frame_size: int,
        on_frame: Callable[[bytes, float, int], None], timeout: float = 1.0,
    ):
        super().__init__(daemon=True, name="FrameReceiver")
        self.sock = sock
        self.frame_size = frame_size
        self.on_frame = on_frame
        self.timeout = timeout
        self._stop = threading.Event()
        self._scratch = bytearray(DCA1000EVM.MAX_PACKET)
        self.packets = 0
        self.dropped_bytes = 0
        self.out_of_order = 0

    def stop(self) -> None:
        """Ask the thread to exit after the current recv."""
        self._stop.set()

    def run(self) -> None:  # noqa: D102 - threading.Thread
        view = memoryview(self._scratch)
        size = self.frame_size
        buf = bytearray()
        offset = 0          # global byte index of the next expected byte
        aligned = False
        dropped = 0
        timestamp = 0.0

        while not self._stop.is_set():
            try:
                n = self.sock.recv_into(view)
            except (socket.timeout, TimeoutError):
                log.info("Data stream idle for %.1fs; receiver exiting.",
                         self.timeout)
                break
            except OSError:
                break
            if n < 10:
                continue
            self.packets += 1

            count = int.from_bytes(self._scratch[4:10], "little")
            payload = bytes(view[10:n])

            if not aligned:
                # Snap to a frame boundary using the card's global byte count.
                offset = count - (count % size)
                aligned = True
                timestamp = time.time()

            gap = count - offset
            if gap < 0:
                self.out_of_order += 1
                if self.out_of_order <= 5:
                    log.warning("Out-of-order packet (%d bytes early).", -gap)
                continue
            if gap > 0:
                buf.extend(b"\x00" * gap)
                offset = count
                dropped += gap
                self.dropped_bytes += gap

            buf.extend(payload)
            offset += len(payload)

            while len(buf) >= size:
                self.on_frame(bytes(buf[:size]), timestamp, dropped)
                del buf[:size]
                dropped = 0
                timestamp = time.time()
