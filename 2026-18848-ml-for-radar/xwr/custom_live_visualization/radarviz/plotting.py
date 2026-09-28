"""Shared plotting: the display transfer function, axis labels, previews.

Everything the live window and the saved snapshot contact sheets have in
common lives here, so the two stay in step: they share one `ScaleSettings`
object, so pressing `d` retunes both.

matplotlib is imported inside the functions that need it, which keeps
`--selftest` and headless recording free of a GUI dependency.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

import numpy as np

from .dsp import to_db
from .pipeline import DETECTION_COLUMNS, Products

if TYPE_CHECKING:
    from .pipeline import Pipeline


@dataclass
class ScaleSettings:
    """How a power map is turned into pixels; shared by the view and previews.

    Two transfer functions, because they answer different questions:

    - `"amplitude"`: `sqrt(power)` on a linear scale spanning `[min, max]`.
      This is what `xwr`'s `demo.py` plots, and it is aggressively
      peak-relative: a return 20 dB below the frame peak lands at 10% of the
      colormap and one 40 dB down at 1%, i.e. effectively black. The result is
      a clean picture of *the strongest thing in the room* -- wave a phone in
      front of the radar and you see the phone, not your arm.
    - `"db"`: `10*log10(power)`, windowed from the noise floor up. The log
      axis expands the bottom, so the same 40 dB-down return sits at ~59% of
      the colormap. Far more informative -- every real reflector and the noise
      texture are visible -- but it looks crowded.

    The noise floor for `"db"` is the median, not the peak: over 90% of a
    range-Doppler map is noise, so the median is robust, whereas the peak is
    TX->RX antenna coupling 70-85 dB up and would clamp everything else flat.

    Attributes:
        scale: active transfer function.
        dynamic_range: `"db"` only -- dB above the noise floor to display.
        min_range_bin: exclude the first bins from the *limit* computation
            (they still render). Antenna coupling at range bin 0-1 is often
            the strongest cell in the frame, and in `"amplitude"` mode it
            would otherwise set `vmax` and crush the real scene to black.
            The default covers coupling spread across bins 0-2 (bin 3 is
            12 cm, so no real target is lost). Set to 0 for bit-exact `xwr`
            behaviour.
        headroom: `"db"` only -- dB shown below the floor, so speckle is not
            clipped.
    """

    scale: Literal["amplitude", "db"] = "amplitude"
    dynamic_range: float = 55.0
    min_range_bin: int = 3
    headroom: float = 3.0

    def map(self, power: np.ndarray) -> np.ndarray:
        """Power map -> display units (amplitude or dB)."""
        if self.scale == "db":
            return to_db(power)
        return np.sqrt(np.maximum(power, 0.0)).astype(np.float32)

    def clim(self, shown: np.ndarray) -> tuple[float, float]:
        """Colour limits for a mapped `(range, x)` image."""
        region = shown
        if 0 < self.min_range_bin < shown.shape[0]:
            region = shown[self.min_range_bin:]
        if self.scale == "db":
            floor = float(np.percentile(region, 50.0))
            return floor - self.headroom, floor + self.dynamic_range
        return float(region.min()), float(region.max())

    def toggle(self) -> str:
        """Switch to the other transfer function; returns the new one."""
        self.scale = "db" if self.scale == "amplitude" else "amplitude"
        return self.scale

    @property
    def label(self) -> str:
        """Short description for the status line."""
        if self.scale == "db":
            return f"dB (floor +{self.dynamic_range:.0f})"
        return "linear amplitude"


def label_angle_axis(ax, angles: np.ndarray, ticks=(-60, -30, 0, 30, 60)):
    """Put degree labels on an axis whose bins are uniform in sin(theta)."""
    n = len(angles)
    spacing = 0.5
    sign = 1.0 if angles[-1] >= angles[0] else -1.0
    positions, labels = [], []
    for deg in ticks:
        pos = n // 2 + sign * np.sin(np.radians(deg)) * n * spacing
        if 0 <= pos <= n:
            positions.append(pos)
            labels.append(f"{deg:g}")
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, fontsize=8)


def render_snapshot_preview(
    path: str, frames: list[Products], trigger_index: int,
    pipeline: "Pipeline", scale: ScaleSettings,
) -> None:
    """Render a snapshot contact sheet: one row per frame, four columns.

    The columns mirror the live display: range-Doppler, range-azimuth, CFAR
    detections over the range-Doppler map, and the same detections as a
    bird's-eye point cloud (x right, y forward, colored by radial velocity
    with one colorbar shared down the column).

    Args:
        path: PNG to write.
        frames: the snapshot's frames, in time order.
        trigger_index: which row was the key press.
        pipeline: supplies the physical axes.
        scale: display transfer function, shared with the live view.
    """
    from matplotlib.figure import Figure

    pipe = pipeline
    n = len(frames)
    col = DETECTION_COLUMNS.index
    r0, r1 = pipe.range_axis[0], pipe.range_axis[-1]
    v0, v1 = pipe.velocity_axis[0], pipe.velocity_axis[-1]
    vmax = max(abs(v0), abs(v1))
    rd_extent = [v0, v1, r0, r1]

    fig = Figure(figsize=(15, 2.6 * n), dpi=110, layout="constrained")
    grid = fig.add_gridspec(n, 4, width_ratios=[1, 1, 1, 1.4])
    pc_axes: list[Any] = []
    pc_scatter = None

    for row, frame in enumerate(frames):
        tag = " <- trigger" if row == trigger_index else ""
        rd = scale.map(frame.range_doppler)
        ra = scale.map(frame.range_azimuth)
        rd_lo, rd_hi = scale.clim(rd)
        ra_lo, ra_hi = scale.clim(ra)
        det = frame.detections

        ax = fig.add_subplot(grid[row, 0])
        ax.imshow(rd, origin="lower", aspect="auto", cmap="viridis",
                  extent=rd_extent, vmin=rd_lo, vmax=rd_hi)
        ax.set_ylabel(f"#{frame.index}{tag}\nrange (m)", fontsize=8)
        if row == 0:
            ax.set_title(f"range-Doppler ({scale.label})", fontsize=9)
        if row == n - 1:
            ax.set_xlabel("velocity (m/s)", fontsize=8)

        ax = fig.add_subplot(grid[row, 1])
        ax.imshow(ra, origin="lower", aspect="auto", cmap="viridis",
                  extent=[0, pipe.n_azimuth, r0, r1],
                  vmin=ra_lo, vmax=ra_hi)
        label_angle_axis(ax, pipe.azimuth_axis)
        if row == 0:
            ax.set_title(f"range-azimuth ({scale.label})", fontsize=9)
        if row == n - 1:
            ax.set_xlabel("azimuth (deg)", fontsize=8)

        ax = fig.add_subplot(grid[row, 2])
        ax.imshow(rd, origin="lower", aspect="auto", cmap="gray",
                  extent=rd_extent, vmin=rd_lo, vmax=rd_hi)
        if len(det):
            ax.scatter(
                det[:, col("velocity_mps")], det[:, col("range_m")],
                s=14, facecolors="none", edgecolors="#ff3b3b",
                linewidths=0.9)
        if row == 0:
            ax.set_title("CFAR detections", fontsize=9)
        if row == n - 1:
            ax.set_xlabel("velocity (m/s)", fontsize=8)
        ax.text(0.02, 0.95, f"{len(det)} pts",
                transform=ax.transAxes, va="top", fontsize=8,
                color="#ff3b3b")

        # Bird's eye: the same CFAR detections in Cartesian coordinates,
        # drawn exactly like the fourth live panel. A thin dark edge keeps
        # near-zero-velocity points (pale in "coolwarm") visible on white.
        ax = fig.add_subplot(grid[row, 3])
        if len(det):
            xs, ys, vs = (det[:, col("x_right_m")],
                          det[:, col("y_forward_m")],
                          det[:, col("velocity_mps")])
        else:
            xs = ys = vs = np.zeros(0, dtype=np.float32)
        pc_scatter = ax.scatter(
            xs, ys, c=vs, s=18, cmap="coolwarm", vmin=-vmax, vmax=vmax,
            edgecolors="black", linewidths=0.3)
        ax.set_xlim(-r1, r1)
        ax.set_ylim(0, r1)
        ax.set_aspect("equal")
        ax.grid(alpha=0.25)
        ax.set_ylabel("y: forward (m)", fontsize=8)
        if row == 0:
            ax.set_title("CFAR point cloud (bird's eye)", fontsize=9)
        if row == n - 1:
            ax.set_xlabel("x: right (m)", fontsize=8)
        pc_axes.append(ax)

    cbar = fig.colorbar(pc_scatter, ax=pc_axes, pad=0.02,
                        shrink=0.5 if n > 1 else 1.0)
    cbar.set_label("velocity (m/s)", fontsize=8)
    cbar.ax.tick_params(labelsize=8)
    fig.savefig(path)
