"""The CA-CFAR detector: noise estimate, thresholding and the blanking rules."""

from __future__ import annotations

import numpy as np
import pytest

from radarviz.cfar import CFAR


def brute_force_noise(
    power: np.ndarray, guard: int, train: int,
) -> np.ndarray:
    """Training-cell mean computed the obvious way, for cross-checking.

    Range is edge-clamped and Doppler wraps, matching `CFAR`.
    """
    n_r, n_d = power.shape
    w = guard + train
    out = np.zeros_like(power)
    for i in range(n_r):
        for j in range(n_d):
            total, count = 0.0, 0
            for a in range(i - w, i + w + 1):
                if not 0 <= a < n_r:
                    continue
                for b in range(j - w, j + w + 1):
                    if abs(a - i) <= guard and abs(b - j) <= guard:
                        continue
                    total += power[a, b % n_d]
                    count += 1
            out[i, j] = total / count
    return out


def test_summed_area_noise_estimate_matches_brute_force() -> None:
    rng = np.random.default_rng(0)
    power = rng.random((12, 10)).astype(np.float32) + 0.5
    detector = CFAR(guard=(1, 1), train=(2, 2), snr_db=0.0,
                    min_range_bin=0, group_peaks=False)
    _, snr = detector(power)
    noise = power / snr
    assert np.abs(noise - brute_force_noise(power, 1, 2)).max() < 1e-4


def test_a_strong_cell_detects_and_flat_noise_does_not() -> None:
    power = np.full((40, 40), 1.0, dtype=np.float32)
    detector = CFAR(guard=(2, 2), train=(4, 4), snr_db=10.0, min_range_bin=0)
    mask, _ = detector(power)
    assert not mask.any(), "a flat map has nothing standing out"

    power[20, 20] = 1000.0
    mask, snr = detector(power)
    assert mask[20, 20]
    assert mask.sum() == 1
    assert snr[20, 20] > 100


def test_peak_grouping_collapses_a_blob_to_one_detection() -> None:
    power = np.full((40, 40), 1.0, dtype=np.float32)
    power[19:22, 19:22] = 500.0
    power[20, 20] = 900.0

    grouped, _ = CFAR(guard=(2, 2), train=(4, 4), snr_db=10.0,
                      min_range_bin=0, group_peaks=True)(power)
    ungrouped, _ = CFAR(guard=(2, 2), train=(4, 4), snr_db=10.0,
                        min_range_bin=0, group_peaks=False)(power)
    assert grouped.sum() == 1
    assert grouped[20, 20]
    assert ungrouped.sum() > grouped.sum()


def test_min_and_max_range_bins_are_blanked() -> None:
    power = np.full((40, 40), 1.0, dtype=np.float32)
    power[1, 20] = 1000.0        # below min_range_bin
    power[30, 20] = 1000.0       # at/above max_range_bin
    power[15, 20] = 1000.0       # inside the reported window
    mask, _ = CFAR(guard=(2, 2), train=(4, 4), snr_db=10.0,
                   min_range_bin=5, max_range_bin=25)(power)
    assert not mask[1, 20]
    assert not mask[30, 20]
    assert mask[15, 20]


def test_zero_doppler_guard_suppresses_static_clutter() -> None:
    power = np.full((40, 40), 1.0, dtype=np.float32)
    power[15, 20] = 1000.0       # bin 20 of 40 is zero velocity
    assert CFAR(guard=(2, 2), train=(4, 4), snr_db=10.0,
                min_range_bin=0)(power)[0][15, 20]
    mask, _ = CFAR(guard=(2, 2), train=(4, 4), snr_db=10.0, min_range_bin=0,
                   zero_doppler_guard=2)(power)
    assert not mask[15, 20]


def test_noise_floor_keeps_a_blanked_map_finite_and_quiet() -> None:
    """Clutter removal zeroes whole Doppler columns.

    Without the floor those neighbourhoods divide into an infinite SNR and
    every adjacent cell detects.
    """
    detector = CFAR(guard=(2, 2), train=(4, 4), snr_db=10.0, min_range_bin=0)

    blank = np.zeros((40, 40), dtype=np.float32)
    mask, snr = detector(blank)
    assert np.isfinite(snr).all()
    assert not mask.any()

    # One negligible sample in an otherwise empty map: its neighbours are
    # measured against the floor, not against zero, so they stay quiet.
    speck = np.zeros((40, 40), dtype=np.float32)
    speck[10, 10] = 1e-9
    mask, snr = detector(speck)
    assert np.isfinite(snr).all()
    assert mask.sum() == 1 and mask[10, 10]


def test_pfa_mode_gives_a_lower_threshold_than_a_strict_snr_rule() -> None:
    rng = np.random.default_rng(2)
    power = rng.exponential(1.0, (60, 60)).astype(np.float32)
    lenient = CFAR(pfa=1e-2, snr_db=None, min_range_bin=0)(power)[0].sum()
    strict = CFAR(pfa=1e-6, snr_db=None, min_range_bin=0)(power)[0].sum()
    assert lenient >= strict


def test_detector_needs_at_least_one_training_cell() -> None:
    with pytest.raises(ValueError, match="training cell"):
        CFAR(train=(0, 0))


def test_geometry_is_cached_per_map_shape() -> None:
    detector = CFAR(min_range_bin=0)
    power = np.ones((20, 20), dtype=np.float32)
    detector(power)
    detector(power)
    detector(np.ones((30, 30), dtype=np.float32))
    assert sorted(detector._cache) == [(20, 20), (30, 30)]
