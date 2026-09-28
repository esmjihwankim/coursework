"""Snapshot capture: the npz payload, the metadata, and the preview sheet."""

from __future__ import annotations

import json

import numpy as np
import pytest

from radarviz.config import RadarConfig
from radarviz.pipeline import DETECTION_COLUMNS, Pipeline
from radarviz.plotting import ScaleSettings
from radarviz.recording import Recorder
from radarviz.sources import SimulatedSource


@pytest.fixture
def snapshot(tmp_path, radar_cfg: RadarConfig, pipeline: Pipeline):
    """Trigger one 3-frame snapshot and return its directory."""
    recorder = Recorder(
        str(tmp_path), radar_cfg, pipeline, before=1, after=1,
        scale=ScaleSettings())
    source = SimulatedSource(radar_cfg, noise=40.0, realtime=False)
    try:
        for i in range(4):
            frame = source.get(0)
            assert frame is not None
            recorder.observe(pipeline.process(frame.data, i, float(i)))
            if i == 1:
                recorder.trigger_snapshot()
    finally:
        recorder.close(timeout=120.0)

    snaps = sorted(tmp_path.glob("snap_*"))
    assert len(snaps) == 1
    return snaps[0]


def test_snapshot_writes_all_three_files(snapshot) -> None:
    assert (snapshot / "frames.npz").exists()
    assert (snapshot / "meta.json").exists()
    assert (snapshot / "preview.png").exists()


def test_snapshot_spans_the_frames_around_the_trigger(snapshot) -> None:
    meta = json.loads((snapshot / "meta.json").read_text())
    assert meta["frames"] == 3
    assert meta["frames_before"] == 1
    assert meta["frames_after"] == 1
    assert meta["frames_consecutive"] is True
    assert meta["frame_index"] == [0, 1, 2]


def test_npz_carries_every_product_and_axis(snapshot) -> None:
    data = np.load(snapshot / "frames.npz")
    for key in ("range_doppler_db", "range_azimuth_db", "cfar_mask",
                "cfar_snr_db", "detections", "frame_index", "timestamp",
                "dropped_bytes", "range_axis_m", "velocity_axis_mps",
                "azimuth_axis_deg", "elevation_axis_deg", "iq_raw_iiqq"):
        assert key in data.files, f"{key} missing from frames.npz"
    assert data["range_doppler_db"].shape[0] == 3
    # The detection table gains a leading frame column.
    assert data["detections"].shape[1] == len(DETECTION_COLUMNS) + 1


def test_metadata_records_the_processing_settings(snapshot) -> None:
    meta = json.loads((snapshot / "meta.json").read_text())
    assert meta["detection_columns"][0] == "frame"
    assert meta["detection_columns"][1:] == DETECTION_COLUMNS
    assert meta["processing"]["array"] == "aop"
    assert meta["processing"]["range_window"] is False
    assert meta["processing"]["doppler_window"] is False
    assert meta["processing"]["cfar"]["guard"] == [2, 2]
    assert meta["radar_config"]["adc_samples"] == 128
    assert meta["derived"]["range_resolution_m"] > 0
    assert meta["raw_layout"]["included"] is True


def test_no_save_raw_omits_the_iq_cube(
    tmp_path, radar_cfg: RadarConfig, pipeline: Pipeline,
) -> None:
    recorder = Recorder(str(tmp_path), radar_cfg, pipeline, before=0, after=0,
                        save_raw=False, save_preview=False)
    source = SimulatedSource(radar_cfg, noise=40.0, realtime=False)
    frame = source.get(0)
    assert frame is not None
    try:
        recorder.observe(pipeline.process(frame.data, 0, 0.0))
        recorder.trigger_snapshot()
        recorder.observe(pipeline.process(frame.data, 1, 1.0))
    finally:
        recorder.close(timeout=120.0)

    snap = sorted(tmp_path.glob("snap_*"))[0]
    data = np.load(snap / "frames.npz")
    assert "iq_raw_iiqq" not in data.files
    assert not (snap / "preview.png").exists()
    meta = json.loads((snap / "meta.json").read_text())
    assert meta["raw_layout"]["included"] is False


def test_trigger_without_any_frames_is_ignored(
    tmp_path, radar_cfg: RadarConfig, pipeline: Pipeline,
) -> None:
    recorder = Recorder(str(tmp_path), radar_cfg, pipeline)
    try:
        assert recorder.trigger_snapshot() == 0
        assert recorder.snapshots == 0
    finally:
        recorder.close(timeout=30.0)
    assert not list(tmp_path.glob("snap_*"))


def test_continuous_recording_round_trips_the_raw_frames(
    tmp_path, radar_cfg: RadarConfig, pipeline: Pipeline,
) -> None:
    recorder = Recorder(str(tmp_path), radar_cfg, pipeline,
                        save_preview=False)
    source = SimulatedSource(radar_cfg, noise=40.0, realtime=False)
    written = []
    try:
        assert recorder.toggle_recording() is True
        for i in range(3):
            frame = source.get(0)
            assert frame is not None
            written.append(frame.data)
            recorder.observe(pipeline.process(frame.data, i, float(i)))
        assert recorder.toggle_recording() is False
    finally:
        recorder.close(timeout=60.0)

    rec = sorted(tmp_path.glob("rec_*"))[0]
    meta = json.loads((rec / "meta.json").read_text())
    assert meta["frames"] == 3
    raw = np.fromfile(rec / "raw.bin", dtype=np.int16).reshape(
        (3, *radar_cfg.raw_shape))
    assert np.array_equal(raw, np.stack(written))
    assert np.array_equal(
        np.load(rec / "frame_index.npy"), np.array([0, 1, 2]))


def test_preview_has_one_row_per_frame_and_four_columns(tmp_path) -> None:
    """The bird's-eye CFAR panel is the fourth column of every row."""
    from matplotlib.figure import Figure

    from radarviz.plotting import render_snapshot_preview

    captured: dict[str, Figure] = {}
    original = Figure.savefig

    def spy(self, *args, **kwargs):
        captured["fig"] = self
        return original(self, *args, **kwargs)

    Figure.savefig = spy
    try:
        cfg = RadarConfig(adc_samples=32, frame_length=16)
        pipe = Pipeline(cfg, azimuth_bins=32, elevation_bins=16)
        source = SimulatedSource(cfg, noise=40.0, realtime=False)
        frames = []
        for i in range(3):
            frame = source.get(0)
            assert frame is not None
            frames.append(pipe.process(frame.data, i, float(i)))
        render_snapshot_preview(
            str(tmp_path / "preview.png"), frames, trigger_index=1,
            pipeline=pipe, scale=ScaleSettings())
    finally:
        Figure.savefig = original

    fig = captured["fig"]
    titles = [ax.get_title() for ax in fig.axes if ax.get_title()]
    assert titles == [
        "range-Doppler (linear amplitude)",
        "range-azimuth (linear amplitude)",
        "CFAR detections",
        "CFAR point cloud (bird's eye)",
    ], "each column is titled once, on the first row"
    # 3 rows x 4 panels, plus the shared point-cloud colorbar.
    assert len(fig.axes) == 3 * 4 + 1


def test_scale_settings_toggle_between_amplitude_and_db() -> None:
    scale = ScaleSettings()
    assert scale.label == "linear amplitude"
    assert scale.toggle() == "db"
    assert "dB" in scale.label
    assert scale.toggle() == "amplitude"


def test_db_scale_windows_up_from_the_median_noise_floor() -> None:
    power = np.full((64, 64), 1.0, dtype=np.float32)
    power[32, 32] = 1e9
    db = ScaleSettings(scale="db", dynamic_range=40.0, headroom=3.0)
    lo, hi = db.clim(db.map(power))
    assert lo == pytest.approx(-3.0, abs=0.1)     # median power is 0 dB
    assert hi == pytest.approx(40.0, abs=0.1)


def test_amplitude_scale_ignores_the_first_range_bins_for_its_limits() -> None:
    power = np.ones((64, 64), dtype=np.float32)
    power[0] = 1e6                                # antenna coupling
    scale = ScaleSettings(scale="amplitude", min_range_bin=3)
    _, hi = scale.clim(scale.map(power))
    assert hi == pytest.approx(1.0)
