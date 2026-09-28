"""The command line: parser defaults, the self-test, and a headless run."""

from __future__ import annotations

import json

import numpy as np
import pytest

from cli import build_parser, main
from radarviz.selftest import selftest


def test_parser_defaults_match_the_lab_settings() -> None:
    args = build_parser().parse_args([])
    assert args.array == "aop"
    assert args.azimuth_bins == 128
    assert args.elevation_bins == 32
    assert args.scale == "amplitude"
    assert args.cfar_snr_db == 15.0
    assert args.cfar_pfa is None
    assert args.snapshot_before == 2 and args.snapshot_after == 2
    assert args.range_window is False and args.doppler_window is False


def test_parser_finds_the_lab_config_by_default() -> None:
    args = build_parser().parse_args([])
    assert args.config is not None
    assert args.config.endswith("config_awr1843aop.yaml")


def test_parser_rejects_an_unknown_array_layout() -> None:
    with pytest.raises(SystemExit):
        build_parser().parse_args(["--array", "nonesuch"])


def test_snapshot_at_is_repeatable() -> None:
    args = build_parser().parse_args(["--snapshot-at", "3", "--snapshot-at", "9"])
    assert args.snapshot_at == [3, 9]


def test_selftest_passes() -> None:
    assert selftest() == 0


def test_selftest_via_main_returns_success() -> None:
    assert main(["--selftest"]) == 0


def test_headless_simulated_run_writes_a_full_snapshot(tmp_path) -> None:
    code = main([
        "--simulate", "--no-display", "--frames", "6", "--snapshot-at", "3",
        "--outdir", str(tmp_path)])
    assert code == 0

    snaps = sorted(tmp_path.glob("snap_*"))
    assert len(snaps) == 1
    snap = snaps[0]
    assert (snap / "frames.npz").exists()
    assert (snap / "preview.png").exists()

    meta = json.loads((snap / "meta.json").read_text())
    assert meta["frames"] == 5
    assert meta["frame_index"] == [1, 2, 3, 4, 5]
    assert meta["trigger_index"] == 2

    data = np.load(snap / "frames.npz")
    assert data["range_doppler_db"].shape[0] == 5
    assert (snap / "preview.png").stat().st_size > 10_000


def test_strict_mode_refuses_an_impossible_configuration(tmp_path) -> None:
    bad = tmp_path / "bad.yaml"
    bad.write_text("radar:\n  frame_length: 100\n")     # not a power of two
    assert main(["--config", str(bad), "--strict", "--simulate",
                 "--no-display", "--frames", "1",
                 "--outdir", str(tmp_path)]) == 1


def test_live_display_builds_all_four_panels(radar_cfg) -> None:
    """Smoke test of the live window against a non-interactive backend."""
    matplotlib = pytest.importorskip("matplotlib")
    matplotlib.use("Agg", force=True)

    from radarviz.display import Display
    from radarviz.pipeline import Pipeline
    from radarviz.plotting import ScaleSettings
    from radarviz.sources import SimulatedSource

    pipe = Pipeline(radar_cfg, azimuth_bins=32, elevation_bins=16)
    scale = ScaleSettings()
    display = Display(pipe, scale=scale)
    try:
        titles = [ax.get_title() for ax in display.fig.axes if ax.get_title()]
        assert titles == [
            "range-Doppler (linear amplitude)",
            "range-azimuth (linear amplitude)",
            "CA-CFAR detections",
            "point cloud (bird's eye)",
        ]
        frame = SimulatedSource(radar_cfg, realtime=False).get(0)
        assert frame is not None
        display.update(pipe.process(frame.data, 0, 0.0), "status")
        assert "status" in display.status.get_text()
        assert display.poll_keys() == []
    finally:
        display.close()
