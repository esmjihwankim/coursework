"""Four-panel live matplotlib view with keyboard control."""

from __future__ import annotations

import queue

import numpy as np

from .pipeline import DETECTION_COLUMNS, Pipeline, Products
from .plotting import ScaleSettings, label_angle_axis


class Display:
    """Four-panel live matplotlib view with keyboard control.

    Args:
        pipeline: supplies the physical axes.
        scale: display transfer function; see `ScaleSettings`. The `d` key
            toggles it in place, so anything else holding the same object
            (the snapshot previews) follows along.
    """

    HELP = ("space: 5-frame snapshot   t: record   m: clutter   "
            "d: dB/amplitude   q: quit")

    def __init__(
        self, pipeline: Pipeline, scale: ScaleSettings | None = None
    ):
        import matplotlib.pyplot as plt

        self.plt = plt
        self.pipeline = pipeline
        self.scale = scale if scale is not None else ScaleSettings()
        self.closed = False
        self.key_queue: queue.Queue[str] = queue.Queue()

        # Free up the keys we want; matplotlib grabs some by default.
        for param in ("keymap.save", "keymap.home", "keymap.yscale"):
            plt.rcParams[param] = [
                k for k in plt.rcParams[param] if k not in ("s", "r", "l")]

        plt.ion()
        self.fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))
        self.fig.canvas.manager.set_window_title(  # type: ignore[union-attr]
            "AWR1843AOP live")
        (ax_rd, ax_ra), (ax_cfar, ax_pc) = axes
        self.ax_rd, self.ax_ra = ax_rd, ax_ra

        r0, r1 = pipeline.range_axis[0], pipeline.range_axis[-1]
        v0, v1 = pipeline.velocity_axis[0], pipeline.velocity_axis[-1]
        rd_extent = [v0, v1, r0, r1]
        blank_rd = np.zeros(
            (pipeline.n_range, pipeline.n_doppler), dtype=np.float32)
        blank_ra = np.zeros(
            (pipeline.n_range, pipeline.n_azimuth), dtype=np.float32)

        self.im_rd = ax_rd.imshow(
            blank_rd, origin="lower", aspect="auto", cmap="viridis",
            extent=rd_extent)
        ax_rd.set_title(f"range-Doppler ({self.scale.label})")
        ax_rd.set_xlabel("velocity (m/s)")
        ax_rd.set_ylabel("range (m)")

        self.im_ra = ax_ra.imshow(
            blank_ra, origin="lower", aspect="auto", cmap="viridis",
            extent=[0, pipeline.n_azimuth, r0, r1])
        ax_ra.set_title(f"range-azimuth ({self.scale.label})")
        ax_ra.set_xlabel("azimuth (deg)")
        ax_ra.set_ylabel("range (m)")
        label_angle_axis(ax_ra, pipeline.azimuth_axis)

        self.im_cfar = ax_cfar.imshow(
            blank_rd, origin="lower", aspect="auto", cmap="gray",
            extent=rd_extent)
        self.sc_cfar, = ax_cfar.plot(
            [], [], linestyle="none", marker="o", markersize=6,
            markerfacecolor="none", markeredgecolor="#ff3b3b",
            markeredgewidth=1.1)
        ax_cfar.set_title("CA-CFAR detections")
        ax_cfar.set_xlabel("velocity (m/s)")
        ax_cfar.set_ylabel("range (m)")

        vmax = max(abs(v0), abs(v1))
        self.sc_pc = ax_pc.scatter(
            [], [], c=[], s=26, cmap="coolwarm", vmin=-vmax, vmax=vmax)
        ax_pc.set_xlim(-r1, r1)
        ax_pc.set_ylim(0, r1)
        ax_pc.set_aspect("equal")
        ax_pc.grid(alpha=0.25)
        ax_pc.set_title("point cloud (bird's eye)")
        ax_pc.set_xlabel("x: right (m)")
        ax_pc.set_ylabel("y: forward (m)")
        self.fig.colorbar(self.sc_pc, ax=ax_pc, label="velocity (m/s)")

        self.status = self.fig.suptitle("starting...", fontsize=11)
        self.fig.tight_layout(rect=(0, 0, 1, 0.95))

        self.fig.canvas.mpl_connect("key_press_event", self._on_key)
        self.fig.canvas.mpl_connect("close_event", self._on_close)

    def _on_key(self, event) -> None:
        if event.key:
            self.key_queue.put(event.key)

    def _on_close(self, _event) -> None:
        self.closed = True

    def poll_keys(self) -> list[str]:
        """Drain and return the keys pressed since the last call."""
        keys = []
        while True:
            try:
                keys.append(self.key_queue.get_nowait())
            except queue.Empty:
                return keys

    def update(self, product: Products, status: str) -> None:
        """Redraw all four panels from one frame's products."""
        rd = self.scale.map(product.range_doppler)
        ra = self.scale.map(product.range_azimuth)

        self.im_rd.set_data(rd)
        self.im_rd.set_clim(*self.scale.clim(rd))
        self.im_ra.set_data(ra)
        self.im_ra.set_clim(*self.scale.clim(ra))
        self.im_cfar.set_data(rd)
        self.im_cfar.set_clim(*self.scale.clim(rd))
        self.ax_rd.set_title(f"range-Doppler ({self.scale.label})")
        self.ax_ra.set_title(f"range-azimuth ({self.scale.label})")

        det = product.detections
        if len(det):
            col = DETECTION_COLUMNS.index
            self.sc_cfar.set_data(
                det[:, col("velocity_mps")], det[:, col("range_m")])
            self.sc_pc.set_offsets(
                np.column_stack([det[:, col("x_right_m")],
                                 det[:, col("y_forward_m")]]))
            self.sc_pc.set_array(det[:, col("velocity_mps")])
        else:
            self.sc_cfar.set_data([], [])
            self.sc_pc.set_offsets(np.zeros((0, 2)))
            self.sc_pc.set_array(np.zeros(0))

        self.status.set_text(f"{status}\n{self.HELP}")
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def pump(self) -> None:
        """Service GUI events without redrawing data."""
        self.fig.canvas.flush_events()

    def close(self) -> None:
        """Tear down the figure."""
        try:
            self.plt.close(self.fig)
        except Exception:  # noqa: BLE001 - best-effort teardown
            pass
