"""Signal-processing kernels: sample packing, windows, beamforming, layouts.

Small, pure NumPy functions with no radar state of their own. `pipeline.py`
composes them into the per-frame chain.

Axis conventions used throughout the package:

    raw    (doppler, tx, rx, 2 * range)   int16, IIQQ interleaved
    cube   (doppler, tx, rx, range)       complex64, after range+doppler FFT
    mimo   (doppler, elevation, azimuth, range)   virtual array

The AWR1843AOP virtual array is elevation = rx (4 elements), azimuth = tx
(3 elements), both on a lambda/2 grid, in "image order" (increasing index =
down / right):

    TX1-RX1  TX2-RX1  TX3-RX1     ^
    TX1-RX2  TX2-RX2  TX3-RX2     | up
    TX1-RX3  TX2-RX3  TX3-RX3
    TX1-RX4  TX2-RX4  TX3-RX4

The AOP therefore has a *3-element* azimuth aperture: azimuth resolution is
intrinsically coarse (~30 deg 3 dB beamwidth) no matter how much the angle
FFT is zero-padded. Zero-padding only interpolates the beam pattern.
"""

from __future__ import annotations

from typing import Callable

import numpy as np


def to_db(power: np.ndarray, floor: float = 1e-12) -> np.ndarray:
    """Power (not amplitude) to dB, with a floor to keep log10 finite."""
    return (10.0 * np.log10(np.maximum(power, floor))).astype(np.float32)


def iq_from_iiqq(iiqq: np.ndarray) -> np.ndarray:
    """De-interleave the capture card's IIQQ byte order into complex64.

    The two LVDS lanes each carry `Q[n] I[n]` little-endian pairs and the card
    interleaves the lanes, so the int16 stream reads `Q0 Q1 I0 I1 Q2 Q3 ...`.

    Args:
        iiqq: int16 array with `2 * n` values on the last axis.

    Returns:
        complex64 array with `n` values on the last axis.
    """
    out = np.empty((*iiqq.shape[:-1], iiqq.shape[-1] // 2), dtype=np.complex64)
    out[..., 0::2] = iiqq[..., 2::4] + 1j * iiqq[..., 0::4]
    out[..., 1::2] = iiqq[..., 3::4] + 1j * iiqq[..., 1::4]
    return out


def iiqq_from_iq(iq: np.ndarray) -> np.ndarray:
    """Inverse of `iq_from_iiqq`; used by the simulator and the self-test."""
    out = np.empty((*iq.shape[:-1], iq.shape[-1] * 2), dtype=np.int16)
    out[..., 0::4] = np.round(iq[..., 0::2].imag)
    out[..., 2::4] = np.round(iq[..., 0::2].real)
    out[..., 1::4] = np.round(iq[..., 1::2].imag)
    out[..., 3::4] = np.round(iq[..., 1::2].real)
    return out


def hann(n: int) -> np.ndarray:
    """Unit-mean Hann window of length `n` (endpoints excluded)."""
    w = np.hanning(n + 2).astype(np.float32)[1:-1]
    return w / w.mean()


def steering_matrix(elements: int, bins: int) -> np.ndarray:
    """DFT/Bartlett steering matrix for a small uniform linear array.

    Multiplying an `elements`-long aperture by this matrix is *identical* to
    `np.fft.fftshift(np.fft.fft(x, n=bins))` -- zero-padding a length-3 or
    length-4 FFT out to 32/64/128 bins is just dropping the zero columns of
    the DFT matrix. Doing it as a matmul is much cheaper than padding and
    FFT-ing a large cube, and it makes the bin <-> angle mapping explicit.

    Args:
        elements: number of physical (virtual) antenna elements.
        bins: number of output angle bins (the "zero-padded FFT size").

    Returns:
        `(bins, elements)` complex64 matrix, fftshifted so bin 0 is the most
            negative spatial frequency.
    """
    k = np.arange(bins)[:, None]
    m = np.arange(elements)[None, :]
    w = np.exp(-2j * np.pi * k * m / bins).astype(np.complex64)
    return np.fft.fftshift(w, axes=0)


def angle_grid(bins: int, spacing: float = 0.5) -> np.ndarray:
    """Angles (radians) of each beamformed bin for a `spacing`-lambda array.

    Bin `k` corresponds to spatial frequency `(k - bins/2) / bins` cycles per
    element, hence `sin(theta) = (k - bins/2) / (bins * spacing)`.
    """
    sin_theta = (np.arange(bins) - bins // 2) / (bins * spacing)
    return np.arcsin(np.clip(sin_theta, -1.0, 1.0))


def virtual_array_aop(rd: np.ndarray) -> np.ndarray:
    """AWR1843AOP MIMO virtual array: `(doppler, tx, rx, range)` -> el/az.

    Elevation is the RX axis (4 elements), azimuth the TX axis (3), both on a
    lambda/2 grid in "image order" (increasing index = down / right). This is
    the physically correct layout for the AOPEVM. Returns a transposed view,
    so it costs nothing.
    """
    return np.transpose(rd, (0, 2, 1, 3))


def virtual_array_boost(rd: np.ndarray) -> np.ndarray:
    """AWR1843Boost MIMO virtual array: a 2x8 grid with 4 empty slots.

    !!! warning

        This is the layout of the *BOOST* board, where TX1/TX3 feed a
        contiguous 8-element horizontal row and TX2 sits half a wavelength
        above its centre. On AOP hardware the RX index runs along
        **elevation**, not azimuth, so this layout scrambles the two
        axes: it reports the correct azimuth only at boresight,
        compresses +/-20 deg to +/-7 deg, and inverts the sign beyond
        +/-40 deg. Provided only for A/B comparison against `xwr`'s
        `demo.py --rsp AWR1843Boost`.
    """
    n_doppler, n_tx, n_rx, n_range = rd.shape
    if (n_tx, n_rx) != (3, 4):
        raise ValueError(f"Boost layout needs 3tx x 4rx, got {n_tx}x{n_rx}.")
    mimo = np.zeros((n_doppler, 2, 8, n_range), dtype=np.complex64)
    mimo[:, 0, 2:6] = rd[:, 1]
    mimo[:, 1, 0:4] = rd[:, 0]
    mimo[:, 1, 4:8] = rd[:, 2]
    return mimo


_Layout = Callable[[np.ndarray], np.ndarray]

ARRAY_LAYOUTS: dict[str, tuple[_Layout, int, int]] = {
    "aop": (virtual_array_aop, 4, 3),
    "boost": (virtual_array_boost, 2, 8),
}
"""Layouts, as `(builder, elevation elements, azimuth elements)`."""
