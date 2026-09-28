"""The acquisition loop: pull frames, process, record, draw, handle keys.

The other high-level half, beside `cli.py`: once a session is built this is
the whole of what the program does, frame after frame. Everything it calls
into lives in the `radarviz` package.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Iterable

from radarviz.display import Display
from radarviz.pipeline import Pipeline
from radarviz.plotting import ScaleSettings
from radarviz.recording import Recorder

log = logging.getLogger(__name__)

IDLE_WARN_SECONDS = 5.0
"""How long to wait with no frames before complaining about the wiring."""

MIN_REDRAW_INTERVAL = 0.25
"""Seconds between forced redraws when the consumer is behind."""


def handle_keys(
    display: Display | None, recorder: Recorder, pipeline: Pipeline,
    scale: ScaleSettings,
) -> None:
    """Act on keypresses; safe to call even when no frames are arriving."""
    if display is None:
        return
    for key in display.poll_keys():
        if key == " ":
            recorder.trigger_snapshot()
        elif key == "t":
            recorder.toggle_recording()
        elif key == "m":
            pipeline.clutter_removal = not pipeline.clutter_removal
            log.info("Clutter removal %s.",
                     "on" if pipeline.clutter_removal else "off")
        elif key == "d":
            log.info("Display scale -> %s.", scale.toggle())
        elif key in ("q", "escape"):
            log.info("Quit requested.")
            display.closed = True


def status_line(
    frame_index: int, fps: float, detections: int, backlog: int,
    dropped: int, pipeline: Pipeline, recorder: Recorder,
) -> str:
    """One-line summary drawn above the live panels."""
    rec = ("REC %d" % recorder.frames_recorded
           if recorder.recording else "idle")
    pending = (f"  snapshot pending ({recorder.pending})"
               if recorder.pending else "")
    return (
        f"frame {frame_index}   {fps:4.1f} fps   "
        f"{detections} detections   "
        f"backlog {backlog}   dropped {dropped}   "
        f"clutter-removal {'on' if pipeline.clutter_removal else 'off'}"
        f"   {rec}   snapshots {recorder.snapshots}{pending}")


def run(
    source: Any, pipeline: Pipeline, recorder: Recorder,
    display: Display | None, scale: ScaleSettings, *,
    max_detections: int = 512, max_frames: int | None = None,
    snapshot_at: Iterable[int] = (), sys_ip: str = "",
) -> int:
    """Drive one source until it stops, the window closes, or Ctrl-C.

    Args:
        source: anything with `start`/`get`/`backlog`/`stop`.
        pipeline: per-frame processing.
        recorder: snapshot ring buffer and raw recorder.
        display: live view, or None when headless.
        scale: display transfer function, shared with the previews.
        max_detections: cap on detections per frame (strongest kept).
        max_frames: stop after this many processed frames.
        snapshot_at: frame indices that trigger a snapshot unattended.
        sys_ip: shown in the "no frames" error to point at the wiring.

    Returns:
        The number of frames processed.
    """
    trigger_frames = set(snapshot_at)
    processed = 0
    last_report = time.perf_counter()
    last_draw = 0.0
    fps_window = 0
    fps = 0.0
    idle_since: float | None = None

    try:
        source.start()
        log.info("Streaming. %s", Display.HELP)

        while True:
            if display is not None and display.closed:
                log.info("Window closed.")
                break
            if max_frames is not None and processed >= max_frames:
                log.info("Reached --frames %d.", max_frames)
                break

            frame = source.get(timeout=0.2)
            if frame is None:
                if display is not None:
                    display.pump()
                    handle_keys(display, recorder, pipeline, scale)
                if idle_since is None:
                    idle_since = time.perf_counter()
                elif time.perf_counter() - idle_since > IDLE_WARN_SECONDS:
                    log.error(
                        "No frames for %.0f s. Is the radar chirping and the "
                        "capture card wired to %s?", IDLE_WARN_SECONDS, sys_ip)
                    idle_since = time.perf_counter()
                continue
            idle_since = None

            product = pipeline.process(
                frame.data, frame.index, frame.timestamp,
                dropped_bytes=frame.dropped_bytes,
                max_detections=max_detections)
            recorder.observe(product)
            processed += 1
            fps_window += 1

            if frame.index in trigger_frames:
                recorder.trigger_snapshot()
            handle_keys(display, recorder, pipeline, scale)

            now = time.perf_counter()
            if now - last_report >= 2.0:
                fps = fps_window / (now - last_report)
                fps_window = 0
                last_report = now

            backlog = source.backlog()
            if display is not None and (
                    backlog == 0 or now - last_draw > MIN_REDRAW_INTERVAL):
                last_draw = now
                display.update(product, status_line(
                    frame.index, fps, len(product.detections), backlog,
                    source.dropped_frames, pipeline, recorder))

    except KeyboardInterrupt:
        log.info("Interrupted.")
    finally:
        source.stop()
        recorder.close()
        if display is not None:
            display.close()

    log.info(
        "Processed %d frames; %d frames dropped before processing; "
        "%d snapshots written.",
        processed, getattr(source, "dropped_frames", 0), recorder.snapshots)
    return processed
