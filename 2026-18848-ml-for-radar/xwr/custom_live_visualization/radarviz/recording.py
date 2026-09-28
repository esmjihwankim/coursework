"""Snapshot ring buffer and continuous raw recording, both off the hot path.

`Recorder.observe` is called for every processed frame and is cheap: it
appends to a deque and, when recording, writes the raw cube straight to disk.
Assembling an `.npz`, the metadata and the preview PNG happens on a writer
thread so a snapshot never stalls the acquisition loop.
"""

from __future__ import annotations

import json
import logging
import os
import queue
import threading
import time
from collections import deque
from typing import Any

import numpy as np

from .config import RadarConfig
from .dsp import to_db
from .pipeline import DETECTION_COLUMNS, Pipeline, Products
from .plotting import ScaleSettings, render_snapshot_preview

log = logging.getLogger(__name__)


class Recorder:
    """Snapshot ring buffer + continuous raw recorder, both off the hot path.

    The space-bar snapshot keeps a rolling window of the last few processed
    frames; when triggered it grabs those, waits for `after` more frames, then
    hands the whole batch to a writer thread. Several snapshots may be in
    flight at once (holding space down just queues more of them).

    Args:
        outdir: directory that receives `snap_*/` and `rec_*/` folders.
        before: frames kept before the trigger.
        after: frames collected after the trigger.
        save_raw: also store the int16 IIQQ frames (768 KiB each here).
        save_preview: render a PNG contact sheet next to each snapshot.
        scale: display transfer function for the preview PNGs. Pass the same
            object the live view holds and previews follow the `d` toggle.
    """

    def __init__(
        self, outdir: str, radar: RadarConfig, pipeline: Pipeline,
        before: int = 2, after: int = 2, save_raw: bool = True,
        save_preview: bool = True, scale: ScaleSettings | None = None,
    ):
        self.outdir = outdir
        self.radar = radar
        self.pipeline = pipeline
        self.before = before
        self.after = after
        self.save_raw = save_raw
        self.save_preview = save_preview
        self.scale = scale if scale is not None else ScaleSettings()

        os.makedirs(outdir, exist_ok=True)
        self.history: deque[Products] = deque(maxlen=before + 1)
        self._pending: list[dict[str, Any]] = []
        self._jobs: queue.Queue = queue.Queue()
        self._writer = threading.Thread(
            target=self._writer_loop, daemon=True, name="SnapshotWriter")
        self._writer.start()

        self.snapshots = 0
        self.recording: dict[str, Any] | None = None
        self.frames_recorded = 0

    # -- snapshots ---------------------------------------------------------

    def observe(self, product: Products) -> None:
        """Feed every processed frame in; drives both capture mechanisms."""
        self.history.append(product)

        for job in list(self._pending):
            job["frames"].append(product)
            job["remaining"] -= 1
            if job["remaining"] <= 0:
                self._pending.remove(job)
                self._jobs.put(job)

        if self.recording is not None:
            self.recording["file"].write(np.ascontiguousarray(product.raw))
            self.recording["timestamps"].append(product.timestamp)
            self.recording["indices"].append(product.index)
            self.frames_recorded += 1

    def trigger_snapshot(self) -> int:
        """Arm a snapshot around the current frame. Returns frames pending."""
        if not self.history:
            log.warning("No frames yet; snapshot ignored.")
            return 0
        self.snapshots += 1
        job = {
            "name": f"snap_{time.strftime('%Y%m%d_%H%M%S')}_"
                    f"{self.snapshots:03d}",
            "frames": list(self.history),
            "trigger_index": len(self.history) - 1,
            "remaining": self.after,
        }
        self._pending.append(job)
        log.info(
            "Snapshot armed: %d frame(s) buffered, %d to go -> %s",
            len(job["frames"]), self.after, job["name"])
        return self.after

    @property
    def pending(self) -> int:
        """Number of snapshots still collecting trailing frames."""
        return len(self._pending)

    def _writer_loop(self) -> None:
        while True:
            job = self._jobs.get()
            if job is None:
                return
            try:
                self._write_snapshot(job)
            except Exception:  # noqa: BLE001 - never kill the writer
                log.exception("Failed to write snapshot %s", job["name"])

    def _write_snapshot(self, job: dict[str, Any]) -> None:
        frames: list[Products] = job["frames"]
        path = os.path.join(self.outdir, job["name"])
        os.makedirs(path, exist_ok=True)

        indices = np.array([f.index for f in frames], dtype=np.int64)
        contiguous = bool(np.all(np.diff(indices) == 1))
        if not contiguous:
            log.warning(
                "Snapshot %s spans non-consecutive frames %s (the consumer "
                "fell behind).", job["name"], indices.tolist())

        np.savez_compressed(
            os.path.join(path, "frames.npz"), **self._arrays(frames))
        with open(os.path.join(path, "meta.json"), "w") as f:
            json.dump(self._meta(job, frames, contiguous), f, indent=2)

        if self.save_preview:
            render_snapshot_preview(
                os.path.join(path, "preview.png"), frames,
                trigger_index=job["trigger_index"], pipeline=self.pipeline,
                scale=self.scale)

        log.info("Saved %d frames -> %s", len(frames), path)

    def _arrays(self, frames: list[Products]) -> dict[str, np.ndarray]:
        """Everything that goes into a snapshot's `frames.npz`."""
        pipe = self.pipeline
        detections = np.concatenate(
            [np.column_stack([np.full(len(f.detections), i, np.float32),
                              f.detections])
             for i, f in enumerate(frames) if len(f.detections)]
            or [np.zeros((0, len(DETECTION_COLUMNS) + 1), np.float32)])

        arrays: dict[str, np.ndarray] = {
            "range_doppler_db": np.stack(
                [to_db(f.range_doppler) for f in frames]),
            "range_azimuth_db": np.stack(
                [to_db(f.range_azimuth) for f in frames]),
            "cfar_mask": np.stack([f.cfar_mask for f in frames]),
            "cfar_snr_db": np.stack([to_db(f.cfar_snr) for f in frames]),
            "detections": detections,
            "frame_index": np.array(
                [f.index for f in frames], dtype=np.int64),
            "timestamp": np.array([f.timestamp for f in frames]),
            "dropped_bytes": np.array(
                [f.dropped_bytes for f in frames], dtype=np.int64),
            "range_axis_m": pipe.range_axis.astype(np.float32),
            "velocity_axis_mps": pipe.velocity_axis.astype(np.float32),
            "azimuth_axis_deg": np.degrees(pipe.azimuth_axis).astype(
                np.float32),
            "elevation_axis_deg": np.degrees(pipe.elevation_axis).astype(
                np.float32),
        }
        if self.save_raw:
            arrays["iq_raw_iiqq"] = np.stack([f.raw for f in frames])
        return arrays

    def _meta(
        self, job: dict[str, Any], frames: list[Products], contiguous: bool,
    ) -> dict[str, Any]:
        """Everything that goes into a snapshot's `meta.json`."""
        pipe = self.pipeline
        return {
            "created": time.strftime("%Y-%m-%d %H:%M:%S"),
            "frames": len(frames),
            "trigger_index": job["trigger_index"],
            "frames_before": job["trigger_index"],
            "frames_after": len(frames) - job["trigger_index"] - 1,
            "frames_consecutive": contiguous,
            "frame_index": [f.index for f in frames],
            "detection_columns": ["frame"] + DETECTION_COLUMNS,
            "coordinate_frame":
                "x = right, y = forward (boresight), z = up; metres",
            "radar_config": {
                k: getattr(self.radar, k)
                for k in self.radar.__dataclass_fields__},
            "derived": {
                "range_resolution_m": self.radar.range_resolution,
                "max_range_m": self.radar.max_range,
                "doppler_resolution_mps": self.radar.doppler_resolution,
                "max_doppler_mps": self.radar.max_doppler,
                "bandwidth_mhz": self.radar.bandwidth,
                "center_frequency_ghz": self.radar.center_frequency,
                "wavelength_m": self.radar.wavelength,
            },
            "processing": {
                "array": pipe.array,
                "azimuth_bins": pipe.n_azimuth,
                "elevation_bins": pipe.n_elevation,
                "range_window": pipe.range_window,
                "doppler_window": pipe.doppler_window,
                "tdm_compensation": pipe.tdm_compensation,
                "doppler_sign": pipe.doppler_sign,
                "clutter_removal": pipe.clutter_removal,
                "display_scale": self.scale.scale,
                "cfar": {
                    "guard": [pipe.cfar.guard_r, pipe.cfar.guard_d],
                    "train": [pipe.cfar.train_r, pipe.cfar.train_d],
                    "pfa": pipe.cfar.pfa,
                    "snr_db": pipe.cfar.snr_db,
                    "min_range_bin": pipe.cfar.min_range_bin,
                    "zero_doppler_guard": pipe.cfar.zero_doppler_guard,
                    "peak_grouping": pipe.cfar.group_peaks,
                    "noise_floor_fraction": pipe.cfar.noise_floor_fraction,
                },
            },
            "raw_layout": {
                "included": self.save_raw,
                "shape": list(self.radar.raw_shape),
                "dtype": "int16",
                "order": "IIQQ interleaved; see iq_from_iiqq()",
            },
        }

    # -- continuous recording ---------------------------------------------

    def toggle_recording(self) -> bool:
        """Start or stop continuous raw recording. Returns the new state."""
        if self.recording is None:
            name = f"rec_{time.strftime('%Y%m%d_%H%M%S')}"
            path = os.path.join(self.outdir, name)
            os.makedirs(path, exist_ok=True)
            self.recording = {
                "path": path,
                "file": open(os.path.join(path, "raw.bin"), "wb"),
                "timestamps": [],
                "indices": [],
                "started": time.time(),
            }
            self.frames_recorded = 0
            log.info("Recording -> %s", path)
            return True

        rec = self.recording
        self.recording = None
        rec["file"].close()
        np.save(
            os.path.join(rec["path"], "timestamps.npy"),
            np.array(rec["timestamps"]))
        np.save(
            os.path.join(rec["path"], "frame_index.npy"),
            np.array(rec["indices"], dtype=np.int64))
        with open(os.path.join(rec["path"], "meta.json"), "w") as f:
            json.dump({
                "frames": len(rec["timestamps"]),
                "duration_s": time.time() - rec["started"],
                "raw_shape_per_frame": list(self.radar.raw_shape),
                "dtype": "int16",
                "order": "IIQQ interleaved; see iq_from_iiqq()",
                "radar_config": {
                    k: getattr(self.radar, k)
                    for k in self.radar.__dataclass_fields__},
            }, f, indent=2)
        log.info(
            "Recording stopped: %d frames -> %s",
            len(rec["timestamps"]), rec["path"])
        return False

    def close(self, timeout: float = 120.0) -> None:
        """Flush any in-flight snapshot and close an open recording.

        Snapshots still waiting for trailing frames are written with whatever
        they have; the writer thread is then drained via a sentinel so nothing
        is lost when the process exits.
        """
        if self.recording is not None:
            self.toggle_recording()
        for job in self._pending:
            if job["frames"]:
                log.warning(
                    "Snapshot %s only got %d frame(s) before shutdown.",
                    job["name"], len(job["frames"]))
                self._jobs.put(job)
        self._pending.clear()

        self._jobs.put(None)
        self._writer.join(timeout=timeout)
        if self._writer.is_alive():
            log.error("Snapshot writer did not finish within %.0fs.", timeout)
