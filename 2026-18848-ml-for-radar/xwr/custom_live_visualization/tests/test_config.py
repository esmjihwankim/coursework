"""Derived radar parameters, YAML loading and the hardware constraint checks."""

from __future__ import annotations

import os

import pytest

from radarviz.config import (
    SPEED_OF_LIGHT, CaptureConfig, RadarConfig, check_constraints,
    default_config_path, load_config)


def test_cube_and_raw_shapes_agree(radar_cfg: RadarConfig) -> None:
    n_d, n_tx, n_rx, n_s = radar_cfg.cube_shape
    assert (n_d, n_tx, n_rx) == (128, 3, 4)
    assert n_s == radar_cfg.adc_samples
    # The raw frame carries two int16 per complex sample.
    assert radar_cfg.raw_shape[-1] == n_s * 2
    assert radar_cfg.frame_size == n_d * n_tx * n_rx * n_s * 4


def test_range_resolution_matches_the_textbook_formula(
    radar_cfg: RadarConfig,
) -> None:
    expected = SPEED_OF_LIGHT / (2 * radar_cfg.bandwidth * 1e6)
    assert radar_cfg.range_resolution == pytest.approx(expected)
    assert radar_cfg.max_range == pytest.approx(
        radar_cfg.range_resolution * radar_cfg.adc_samples)
    # Lab 1 asks for ~4 cm bins over ~5 m.
    assert 0.03 < radar_cfg.range_resolution < 0.05
    assert 4.0 < radar_cfg.max_range < 6.0


def test_doppler_axis_is_symmetric_about_zero(radar_cfg: RadarConfig) -> None:
    assert radar_cfg.max_doppler == pytest.approx(
        radar_cfg.doppler_resolution * radar_cfg.frame_length / 2)


def test_center_frequency_sits_inside_the_sampled_sweep(
    radar_cfg: RadarConfig,
) -> None:
    start = radar_cfg.frequency
    end = start + radar_cfg.freq_slope * radar_cfg.ramp_end_time / 1e3
    assert start < radar_cfg.center_frequency < end


def test_summary_mentions_every_headline_number(radar_cfg: RadarConfig) -> None:
    text = radar_cfg.summary()
    for needle in ("AWR1843AOPEVM", "range res / max", "doppler res / max",
                   "frame size"):
        assert needle in text


def test_default_configuration_passes_every_constraint(
    radar_cfg: RadarConfig,
) -> None:
    results = check_constraints(radar_cfg, CaptureConfig())
    failed = [name for name, ok, _ in results if not ok]
    assert not failed, f"default config should be valid, failed: {failed}"


def test_constraints_catch_a_non_power_of_two_frame_length() -> None:
    results = check_constraints(RadarConfig(frame_length=100), CaptureConfig())
    by_name = {name: ok for name, ok, _ in results}
    assert by_name["FrameLengthPowerOfTwo"] is False


def test_constraints_catch_an_overlong_adc_window() -> None:
    # 128 samples at 2000 ksps is a 64 us dwell, longer than a 40 us ramp.
    results = check_constraints(RadarConfig(ramp_end_time=40.0), CaptureConfig())
    by_name = {name: ok for name, ok, _ in results}
    assert by_name["ExcessRampTime"] is False


def test_load_config_without_a_path_returns_defaults() -> None:
    radar, capture = load_config(None)
    assert radar == RadarConfig()
    assert capture == CaptureConfig()


def test_load_config_reads_both_blocks_and_skips_unknown_keys(tmp_path) -> None:
    path = tmp_path / "cfg.yaml"
    path.write_text(
        "radar:\n"
        "  device: AWR1843AOPEVM\n"
        "  adc_samples: 64\n"
        "  not_a_real_key: 7\n"
        "capture:\n"
        "  sys_ip: 10.0.0.1\n")
    radar, capture = load_config(str(path))
    assert radar.adc_samples == 64
    assert capture.sys_ip == "10.0.0.1"
    assert not hasattr(radar, "not_a_real_key")
    assert not hasattr(radar, "device")


def test_default_config_path_finds_the_lab_yaml() -> None:
    found = default_config_path()
    assert found is not None, "demo/config_awr1843aop.yaml should be found"
    assert os.path.exists(found)
    assert found.endswith(os.path.join("demo", "config_awr1843aop.yaml"))


def test_default_config_path_gives_up_outside_the_checkout(tmp_path) -> None:
    assert default_config_path(str(tmp_path)) is None
