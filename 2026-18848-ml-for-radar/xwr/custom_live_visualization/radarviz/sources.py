"""Frame sources: live hardware capture and a synthetic stand-in.

Both expose the same four methods -- `start`, `get`, `backlog`, `stop` -- so
the main loop does not care which one it is driving.
"""

from __future__ import annotations

import logging
import queue
import time
from dataclasses import dataclass

import numpy as np

from .capture import DCA1000EVM, FrameReceiver
from .config import CaptureConfig, RadarConfig
from .dsp import iiqq_from_iq
from .radar import AWR1843AOP

log = logging.getLogger(__name__)


@dataclass
class RawFrame:
    """One raw frame handed from a source to the main loop."""

    index: int
    timestamp: float
    dropped_bytes: int
    data: np.ndarray


class HardwareSource:
    """Live AWR1843AOPEVM + DCA1000EVM capture.

    Startup order matters: the capture card must be recording *before* the
    radar starts chirping, otherwise the running byte count used for frame
    alignment is offset.
    """

    def __init__(
        self, radar_cfg: RadarConfig, capture_cfg: CaptureConfig,
        queue_size: int = 32,
    ):
        self.radar_cfg = radar_cfg
        self.queue: queue.Queue[RawFrame] = queue.Queue(maxsize=queue_size)
        self.received = 0
        self.dropped_frames = 0

        self.dca = DCA1000EVM(capture_cfg)
        self.dca.setup()
        self.radar = AWR1843AOP(port=radar_cfg.port)
        self.receiver: FrameReceiver | None = None

    def start(self) -> None:
        """Reset, arm the capture card, configure and start the radar.

        The receiver thread is started *last*: pushing ~30 CLI commands over a
        115200 baud UART takes seconds, and the receiver treats a second of
        silence as end-of-stream. Nothing is missed by waiting, because no
        data exists until `sensorStart` returns.
        """
        self.dca.stop()
        self.dca.reset_radar()
        self.dca.flush()
        self.dca.start()

        self.radar.configure(self.radar_cfg)
        self.radar.start()

        self.receiver = FrameReceiver(
            self.dca.data, self.radar_cfg.frame_size, self._on_frame,
            timeout=self.dca.cfg.timeout)
        self.receiver.start()

    def _on_frame(self, data: bytes, timestamp: float, dropped: int) -> None:
        array = np.frombuffer(data, dtype=np.int16).reshape(
            self.radar_cfg.raw_shape)
        frame = RawFrame(self.received, timestamp, dropped, array)
        self.received += 1
        try:
            self.queue.put_nowait(frame)
        except queue.Full:
            try:                     # make room by discarding the oldest
                self.queue.get_nowait()
                self.dropped_frames += 1
            except queue.Empty:
                pass
            try:
                self.queue.put_nowait(frame)
            except queue.Full:
                self.dropped_frames += 1

    def get(self, timeout: float) -> RawFrame | None:
        """Block for the next frame, or None on timeout."""
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def backlog(self) -> int:
        """Frames waiting to be processed."""
        return self.queue.qsize()

    def stop(self) -> None:
        """Stop the radar and the capture card; safe to call twice."""
        log.info("Shutting down radar and capture card...")
        if self.receiver is not None:
            self.receiver.stop()
        try:
            self.dca.stop()
            self.dca.reset_radar()
        except Exception as exc:  # noqa: BLE001 - always finish teardown
            log.error("Capture card shutdown: %s", exc)
        try:
            self.radar.close()
        finally:
            self.dca.close()


class SimulatedSource:
    """Synthesizes IIQQ frames with point targets; no hardware required.

    Targets are injected using exactly the phase model the pipeline inverts,
    so this validates the pipeline's internal consistency (bin indexing, TDM
    compensation, array geometry) -- it cannot validate hardware-dependent
    sign conventions.

    Args:
        cfg: radar configuration.
        targets: `(range_m, velocity_mps, azimuth_deg, elevation_deg,
            amplitude)` tuples.
        noise: standard deviation of the additive complex noise, in LSB.
        realtime: sleep to emulate the true frame period.
    """

    def __init__(
        self, cfg: RadarConfig,
        targets: list[tuple[float, float, float, float, float]] | None = None,
        noise: float = 60.0, realtime: bool = True, seed: int = 0,
    ):
        self.cfg = cfg
        self.noise = noise
        self.realtime = realtime
        self.rng = np.random.default_rng(seed)
        self.received = 0
        self.dropped_frames = 0
        self._next = time.time()
        self.targets = targets if targets is not None else [
            (1.2, 0.0, -25.0, 0.0, 1400.0),
            (2.4, 0.35, 10.0, 5.0, 1100.0),
            (3.6, -0.5, 30.0, -5.0, 900.0),
        ]

    def start(self) -> None:
        """No-op; present so both sources share an interface."""

    def _synthesize(self) -> np.ndarray:
        cfg = self.cfg
        n_d, n_tx, n_rx, n_s = cfg.cube_shape
        iq = np.zeros((n_d, n_tx, n_rx, n_s), dtype=np.complex64)

        d = np.arange(n_d)[:, None, None, None]
        tx = np.arange(n_tx)[None, :, None, None]
        rx = np.arange(n_rx)[None, None, :, None]
        s = np.arange(n_s)[None, None, None, :]
        drift = self.received * cfg.frame_period / 1000.0

        for rng_m, vel, az_deg, el_deg, amp in self.targets:
            rng_bin = (rng_m + vel * drift) / cfg.range_resolution
            dop_bin = vel / cfg.doppler_resolution
            sin_az = np.sin(np.radians(az_deg))
            # Elevation rows run downward (image order), hence the sign flip.
            sin_el = -np.sin(np.radians(el_deg))

            phase = (
                2j * np.pi * (
                    rng_bin * s / n_s
                    + dop_bin * (d + tx / n_tx) / n_d
                    + 0.5 * tx * sin_az
                    + 0.5 * rx * sin_el))
            iq += (amp * np.exp(phase)).astype(np.complex64)

        if self.noise > 0:
            iq += (self.rng.normal(0, self.noise, iq.shape)
                   + 1j * self.rng.normal(0, self.noise, iq.shape))
        return iiqq_from_iq(np.clip(iq.view(np.float32), -32768, 32767)
                            .view(np.complex64))

    def get(self, timeout: float) -> RawFrame | None:
        """Produce the next synthetic frame (optionally paced in real time)."""
        if self.realtime:
            delay = self._next - time.time()
            if delay > 0:
                time.sleep(min(delay, timeout))
            self._next += self.cfg.frame_period / 1000.0
        frame = RawFrame(self.received, time.time(), 0, self._synthesize())
        self.received += 1
        return frame

    def backlog(self) -> int:
        """Always zero; the simulator is generated on demand."""
        return 0

    def stop(self) -> None:
        """No-op."""
