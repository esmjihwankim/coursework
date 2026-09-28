"""The per-frame chain: FFTs, beamforming shortcuts and the detection table."""

from __future__ import annotations

import numpy as np
import pytest

from radarviz.cfar import CFAR
from radarviz.config import RadarConfig
from radarviz.dsp import ARRAY_LAYOUTS
from radarviz.pipeline import DETECTION_COLUMNS, Pipeline, Products

from conftest import TARGET


@pytest.fixture
def random_cube(small_cfg: RadarConfig) -> np.ndarray:
    rng = np.random.default_rng(0)
    return (rng.normal(size=small_cfg.cube_shape)
            + 1j * rng.normal(size=small_cfg.cube_shape)).astype(np.complex64)


@pytest.mark.parametrize("layout", sorted(ARRAY_LAYOUTS))
def test_covariance_range_azimuth_equals_direct_beamforming(
    small_cfg: RadarConfig, random_cube: np.ndarray, layout: str,
) -> None:
    pipe = Pipeline(small_cfg, azimuth_bins=32, elevation_bins=16, array=layout)
    mimo = pipe.virtual_array(random_cube)
    fast = pipe.range_azimuth_power(mimo)
    beam = np.einsum("ka,dean->dken", pipe.az_steer, mimo, optimize=True)
    slow = (np.abs(beam) ** 2).sum(axis=(0, 2)).T
    assert np.abs(fast - slow).max() / slow.max() < 1e-4


@pytest.mark.parametrize("layout", sorted(ARRAY_LAYOUTS))
def test_antenna_power_sum_equals_the_mean_over_angle_bins(
    small_cfg: RadarConfig, random_cube: np.ndarray, layout: str,
) -> None:
    """Parseval: this is the quantity xwr's demo.py plots, layout-independent."""
    pipe = Pipeline(small_cfg, azimuth_bins=32, elevation_bins=16, array=layout)
    mimo = pipe.virtual_array(random_cube)
    angle = np.einsum("ka,dean->dken", pipe.az_steer, mimo, optimize=True)
    angle = np.einsum("dken,je->dkjn", angle, pipe.el_steer, optimize=True)
    rms = np.sqrt(np.mean(np.abs(angle) ** 2, axis=(1, 2))).T
    ours = np.sqrt(pipe.range_doppler_power(random_cube))
    assert np.abs(rms - ours).max() / ours.max() < 1e-4


def test_unknown_array_layout_is_rejected(small_cfg: RadarConfig) -> None:
    with pytest.raises(ValueError, match="Unknown array layout"):
        Pipeline(small_cfg, array="nonesuch")


def test_axes_have_the_expected_lengths_and_ordering(
    radar_cfg: RadarConfig,
) -> None:
    pipe = Pipeline(radar_cfg, azimuth_bins=64, elevation_bins=32)
    assert len(pipe.range_axis) == radar_cfg.adc_samples
    assert len(pipe.velocity_axis) == radar_cfg.frame_length
    assert len(pipe.azimuth_axis) == 64
    assert len(pipe.elevation_axis) == 32
    assert pipe.range_axis[0] == 0.0
    assert pipe.velocity_axis[radar_cfg.frame_length // 2] == 0.0


def test_window_flags_are_reported_for_the_snapshot_metadata(
    small_cfg: RadarConfig,
) -> None:
    assert Pipeline(small_cfg).range_window is False
    assert Pipeline(small_cfg).doppler_window is False
    windowed = Pipeline(small_cfg, range_window=True, doppler_window=True)
    assert windowed.range_window is True
    assert windowed.doppler_window is True


def test_a_synthetic_target_lands_in_the_bins_it_was_injected_into(
    pipeline: Pipeline, one_target_frame, radar_cfg: RadarConfig,
) -> None:
    product = pipeline.process(one_target_frame.data, 0, 0.0)
    assert len(product.detections), "the target should be detected"

    col = DETECTION_COLUMNS.index
    best = product.detections[np.argmax(product.detections[:, col("snr_db")])]
    want_r, want_v, want_az, want_el, _ = TARGET
    assert best[col("range_m")] == pytest.approx(
        want_r, abs=2 * radar_cfg.range_resolution)
    assert best[col("velocity_mps")] == pytest.approx(
        want_v, abs=2 * radar_cfg.doppler_resolution)
    assert best[col("azimuth_deg")] == pytest.approx(want_az, abs=8.0)
    assert best[col("elevation_deg")] == pytest.approx(want_el, abs=8.0)


def test_cartesian_columns_agree_with_the_spherical_ones(
    pipeline: Pipeline, one_target_frame,
) -> None:
    det = pipeline.process(one_target_frame.data, 0, 0.0).detections
    col = DETECTION_COLUMNS.index
    r = det[:, col("range_m")]
    az = np.radians(det[:, col("azimuth_deg")])
    el = np.radians(det[:, col("elevation_deg")])
    ground = r * np.cos(el)
    assert det[:, col("x_right_m")] == pytest.approx(
        ground * np.sin(az), abs=1e-5)
    assert det[:, col("y_forward_m")] == pytest.approx(
        ground * np.cos(az), abs=1e-5)
    assert det[:, col("z_up_m")] == pytest.approx(r * np.sin(el), abs=1e-5)


def test_products_shapes_are_consistent(
    pipeline: Pipeline, one_target_frame, radar_cfg: RadarConfig,
) -> None:
    product = pipeline.process(one_target_frame.data, 7, 1.5, dropped_bytes=4)
    assert isinstance(product, Products)
    assert product.index == 7
    assert product.timestamp == 1.5
    assert product.dropped_bytes == 4
    assert product.range_doppler.shape == (
        radar_cfg.adc_samples, radar_cfg.frame_length)
    assert product.range_azimuth.shape == (radar_cfg.adc_samples, 64)
    assert product.cfar_mask.shape == product.range_doppler.shape
    assert product.detections.shape[1] == len(DETECTION_COLUMNS)
    assert product.cfar_mask.sum() == len(product.detections)


def test_max_detections_keeps_the_strongest_and_prunes_the_mask(
    radar_cfg: RadarConfig, one_target_frame,
) -> None:
    pipe = Pipeline(radar_cfg, azimuth_bins=32, elevation_bins=16,
                    cfar=CFAR(snr_db=0.0, min_range_bin=0))
    many = pipe.process(one_target_frame.data, 0, 0.0, max_detections=10_000)
    capped = pipe.process(one_target_frame.data, 0, 0.0, max_detections=5)
    assert len(many.detections) > 5
    assert len(capped.detections) == 5
    assert capped.cfar_mask.sum() == 5
    col = DETECTION_COLUMNS.index
    assert capped.detections[:, col("snr_db")].min() >= np.sort(
        many.detections[:, col("snr_db")])[-5]


def test_a_frame_with_no_detections_yields_an_empty_table(
    radar_cfg: RadarConfig, one_target_frame,
) -> None:
    pipe = Pipeline(radar_cfg, azimuth_bins=32, elevation_bins=16,
                    cfar=CFAR(snr_db=500.0))
    product = pipe.process(one_target_frame.data, 0, 0.0)
    assert product.detections.shape == (0, len(DETECTION_COLUMNS))
    assert not product.cfar_mask.any()


def test_clutter_removal_blanks_the_zero_doppler_column(
    radar_cfg: RadarConfig,
) -> None:
    from radarviz.sources import SimulatedSource

    static_target = [(2.0, 0.0, 0.0, 0.0, 1500.0)]
    frame = SimulatedSource(
        radar_cfg, targets=static_target, noise=40.0, realtime=False).get(0)
    assert frame is not None
    pipe = Pipeline(radar_cfg, azimuth_bins=32, elevation_bins=16)
    zero = radar_cfg.frame_length // 2

    before = pipe.process(frame.data, 0, 0.0).range_doppler[:, zero].sum()
    pipe.clutter_removal = True
    after = pipe.process(frame.data, 0, 0.0).range_doppler[:, zero].sum()
    assert after == 0.0
    assert before > 0.0
