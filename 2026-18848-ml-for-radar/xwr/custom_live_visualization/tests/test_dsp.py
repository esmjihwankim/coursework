"""The signal-processing kernels: sample packing, steering, array layouts."""

from __future__ import annotations

import numpy as np
import pytest

from radarviz.dsp import (
    ARRAY_LAYOUTS, angle_grid, hann, iiqq_from_iq, iq_from_iiqq,
    steering_matrix, to_db, virtual_array_aop, virtual_array_boost)


@pytest.mark.parametrize("elements,bins", [(3, 64), (4, 32), (4, 33), (12, 128)])
def test_steering_matmul_equals_a_zero_padded_shifted_fft(
    elements: int, bins: int,
) -> None:
    rng = np.random.default_rng(0)
    x = (rng.normal(size=elements)
         + 1j * rng.normal(size=elements)).astype(np.complex64)
    got = steering_matrix(elements, bins) @ x
    want = np.fft.fftshift(np.fft.fft(x, n=bins))
    assert np.abs(got - want).max() < 1e-3


def test_iiqq_round_trip_is_lossless_for_integer_samples() -> None:
    rng = np.random.default_rng(1)
    iq = (rng.integers(-2000, 2000, (2, 8))
          + 1j * rng.integers(-2000, 2000, (2, 8))).astype(np.complex64)
    assert np.array_equal(iq_from_iiqq(iiqq_from_iq(iq)), iq)


def test_iq_from_iiqq_de_interleaves_the_two_lvds_lanes() -> None:
    # One chirp of 2 complex samples: the card sends Q0 Q1 I0 I1.
    raw = np.array([[10, 20, 1, 2]], dtype=np.int16)
    assert np.array_equal(iq_from_iiqq(raw), np.array([[1 + 10j, 2 + 20j]]))


def test_hann_window_has_unit_mean_and_no_zero_endpoints() -> None:
    w = hann(64)
    assert w.mean() == pytest.approx(1.0, rel=1e-6)
    assert w[0] > 0 and w[-1] > 0


def test_angle_grid_spans_the_unambiguous_field_of_view() -> None:
    angles = np.degrees(angle_grid(64))
    assert angles[0] == pytest.approx(-90.0, abs=1e-6)
    assert angles[len(angles) // 2] == pytest.approx(0.0, abs=1e-6)
    assert np.all(np.diff(angles) > 0), "grid must be monotonically increasing"


def test_aop_layout_swaps_the_tx_and_rx_axes() -> None:
    rd = np.zeros((2, 3, 4, 5), dtype=np.complex64)
    mimo = virtual_array_aop(rd)
    # (doppler, tx, rx, range) -> (doppler, elevation=rx, azimuth=tx, range)
    assert mimo.shape == (2, 4, 3, 5)


def test_boost_layout_places_tx2_above_the_row_centre() -> None:
    rd = np.zeros((1, 3, 4, 1), dtype=np.complex64)
    rd[:, 0] = 1.0        # TX1
    rd[:, 1] = 2.0        # TX2
    rd[:, 2] = 3.0        # TX3
    mimo = virtual_array_boost(rd)
    assert mimo.shape == (1, 2, 8, 1)
    assert np.all(mimo[0, 0, 2:6, 0] == 2.0), "TX2 fills the upper row centre"
    assert np.all(mimo[0, 1, 0:4, 0] == 1.0)
    assert np.all(mimo[0, 1, 4:8, 0] == 3.0)
    assert np.all(mimo[0, 0, 0:2, 0] == 0.0), "corners stay empty"


def test_boost_layout_rejects_a_non_3x4_array() -> None:
    with pytest.raises(ValueError, match="3tx x 4rx"):
        virtual_array_boost(np.zeros((1, 2, 4, 1), dtype=np.complex64))


def test_array_layouts_report_their_element_counts() -> None:
    assert ARRAY_LAYOUTS["aop"][1:] == (4, 3)      # 4 elevation, 3 azimuth
    assert ARRAY_LAYOUTS["boost"][1:] == (2, 8)


def test_to_db_floors_zero_instead_of_returning_negative_infinity() -> None:
    out = to_db(np.array([0.0, 1.0, 100.0], dtype=np.float32))
    assert np.isfinite(out).all()
    assert out[1] == pytest.approx(0.0)
    assert out[2] == pytest.approx(20.0)
