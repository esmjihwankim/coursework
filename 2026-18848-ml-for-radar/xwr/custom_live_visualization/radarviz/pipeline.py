"""Per-frame processing chain: range/Doppler FFTs, beamforming, detection.

`Pipeline` owns the per-configuration state (windows, steering matrices,
physical axes, the TDM phase correction) and turns one raw IIQQ frame into a
`Products` bundle that the display, the recorder and the previews all read.
"""

from __future__ import annotations

import numpy as np
from dataclasses import dataclass

from .cfar import CFAR
from .config import RadarConfig
from .dsp import (
    ARRAY_LAYOUTS, angle_grid, hann, iq_from_iiqq, steering_matrix)


@dataclass
class Products:
    """Everything the pipeline derives from one radar frame.

    Attributes:
        index: monotonically increasing frame counter.
        timestamp: wall-clock time of the first packet of the frame.
        dropped_bytes: bytes zero-filled in this frame due to packet loss.
        raw: the int16 IIQQ frame, reshaped but otherwise untouched.
        range_doppler: (range, doppler) power, non-coherently integrated.
        range_azimuth: (range, azimuth) power.
        cfar_mask: (range, doppler) boolean detection mask after peak grouping.
        cfar_snr: (range, doppler) linear signal-to-noise-floor ratio.
        detections: structured detection table (see `DETECTION_COLUMNS`).
    """

    index: int
    timestamp: float
    dropped_bytes: int
    raw: np.ndarray
    range_doppler: np.ndarray
    range_azimuth: np.ndarray
    cfar_mask: np.ndarray
    cfar_snr: np.ndarray
    detections: np.ndarray


DETECTION_COLUMNS = [
    "range_bin", "doppler_bin", "azimuth_bin", "elevation_bin",
    "range_m", "velocity_mps", "azimuth_deg", "elevation_deg",
    "snr_db", "x_right_m", "y_forward_m", "z_up_m",
]
"""Column names of the `Products.detections` table."""


class Pipeline:
    """Range-Doppler-azimuth-elevation processing + CFAR for one radar.

    Args:
        cfg: radar configuration (supplies bin counts and resolutions).
        azimuth_bins: zero-padded azimuth FFT size (lab requires >= 32).
        elevation_bins: zero-padded elevation FFT size.
        range_window: apply a Hann window before the range FFT.
        doppler_window: apply a Hann window before the Doppler FFT.
        tdm_compensation: undo the per-TX Doppler phase ramp introduced by
            time-division multiplexing before angle estimation.
        doppler_sign: +1 or -1; flips the velocity axis (see notes in `main`).
        azimuth_sign: +1 or -1; flips the azimuth axis.
        elevation_sign: +1 or -1; -1 maps "image order" rows to up-positive.
        cfar: CFAR detector settings.
        array: virtual array layout, a key of `ARRAY_LAYOUTS`. Use `"aop"`;
            `"boost"` is for A/B comparison against `xwr` only and reports
            incorrect azimuth on AOP hardware.
    """

    def __init__(
        self, cfg: RadarConfig, azimuth_bins: int = 128,
        elevation_bins: int = 32, range_window: bool = False,
        doppler_window: bool = False, tdm_compensation: bool = True,
        doppler_sign: int = 1, azimuth_sign: int = 1,
        elevation_sign: int = -1, cfar: CFAR | None = None,
        array: str = "aop",
    ):
        self.cfg = cfg
        self.n_range = cfg.adc_samples
        self.n_doppler = cfg.frame_length
        self.n_azimuth = azimuth_bins
        self.n_elevation = elevation_bins
        self.tdm_compensation = tdm_compensation
        self.doppler_sign = doppler_sign
        self.cfar = cfar if cfar is not None else CFAR()

        self._range_window = (
            hann(self.n_range).astype(np.float32) if range_window else None)
        self._doppler_window = (
            hann(self.n_doppler).astype(np.float32)[:, None, None, None]
            if doppler_window else None)

        # Virtual array layout decides which physical axis is which angle.
        if array not in ARRAY_LAYOUTS:
            raise ValueError(
                f"Unknown array layout {array!r}; "
                f"expected one of {sorted(ARRAY_LAYOUTS)}.")
        self.array = array
        self.virtual_array, n_el_elem, n_az_elem = ARRAY_LAYOUTS[array]
        self.az_steer = steering_matrix(n_az_elem, azimuth_bins)
        self.el_steer = steering_matrix(n_el_elem, elevation_bins)

        # Axes, in physical units.
        self.range_axis = np.arange(self.n_range) * cfg.range_resolution
        self.velocity_axis = doppler_sign * (
            np.arange(self.n_doppler) - self.n_doppler // 2
        ) * cfg.doppler_resolution
        self.azimuth_axis = azimuth_sign * angle_grid(azimuth_bins)
        self.elevation_axis = elevation_sign * angle_grid(elevation_bins)

        # TDM phase correction: within one chirp loop TX k fires k/num_tx of a
        # loop period late, so a target at normalized Doppler w picks up an
        # extra phase w * k / num_tx on TX k. Undo it per Doppler bin.
        d = np.arange(self.n_doppler) - self.n_doppler // 2
        k = np.arange(cfg.num_tx)
        phase = -2j * np.pi * np.outer(d / self.n_doppler, k / cfg.num_tx)
        self._tdm = np.exp(doppler_sign * phase).astype(
            np.complex64)[:, :, None, None]

        self.clutter_removal = False
        """When True, blank the zero-Doppler bin(s) before detection."""

    @property
    def range_window(self) -> bool:
        """Whether a Hann window is applied before the range FFT."""
        return self._range_window is not None

    @property
    def doppler_window(self) -> bool:
        """Whether a Hann window is applied before the Doppler FFT."""
        return self._doppler_window is not None

    # -- stages ------------------------------------------------------------

    def range_doppler_cube(self, raw: np.ndarray) -> np.ndarray:
        """Raw IIQQ frame -> complex (doppler, tx, rx, range) cube.

        Range uses the full complex FFT (I/Q sampling makes all `adc_samples`
        bins unambiguous); Doppler is fftshifted so bin `N/2` is zero velocity.
        """
        iq = iq_from_iiqq(raw)
        if self._range_window is not None:
            iq = iq * self._range_window
        cube = np.fft.fft(iq, axis=-1)

        if self._doppler_window is not None:
            cube = cube * self._doppler_window
        cube = np.fft.fftshift(np.fft.fft(cube, axis=0), axes=0)
        return cube.astype(np.complex64)

    def _prepare(self, cube: np.ndarray) -> np.ndarray:
        """Apply TDM compensation and optional static-clutter removal."""
        if self.tdm_compensation:
            cube = cube * self._tdm
        if self.clutter_removal:
            cube = cube.copy()
            zero = self.n_doppler // 2
            lo = max(0, zero - 1)
            hi = min(self.n_doppler, zero + 2)
            cube[lo:hi] = 0
        return cube

    @staticmethod
    def range_doppler_power(cube: np.ndarray) -> np.ndarray:
        """(range, doppler) power, summed over all 12 virtual antennas."""
        power = np.einsum(
            "dtrn,dtrn->nd", cube, cube.conj(), optimize=True).real
        return power.astype(np.float32)

    def range_azimuth_power(self, mimo: np.ndarray) -> np.ndarray:
        """(range, azimuth) power, summed over Doppler and elevation.

        Computed through the spatial covariance of the azimuth axis rather
        than by beamforming the whole cube. The two are algebraically
        identical --

            sum_d sum_el |sum_a A[k,a] X[d,el,a,r]|^2
                = sum_{a,b} A[k,a] conj(A[k,b]) R[r,a,b],
            R[r,a,b] = sum_{d,el} X[d,el,a,r] conj(X[d,el,b,r])

        -- but the covariance form is ~20x cheaper and never materializes the
        (doppler, elevation, azimuth, range) angle cube. `--selftest` checks
        it against direct beamforming for both array layouts.

        Args:
            mimo: `(doppler, elevation, azimuth, range)` virtual array cube.
        """
        n_az_elem = mimo.shape[2]
        # (doppler, el, az, range) -> (range, az, doppler * el)
        x = np.transpose(mimo, (3, 2, 0, 1)).reshape(
            self.n_range, n_az_elem, -1)
        cov = np.matmul(x, x.conj().transpose(0, 2, 1))     # (range, az, az)
        tmp = np.einsum("ka,rab->rkb", self.az_steer, cov, optimize=True)
        power = np.einsum(
            "rkb,kb->rk", tmp, self.az_steer.conj(), optimize=True).real
        return power.astype(np.float32)

    def angles_at(
        self, mimo: np.ndarray, range_bins: np.ndarray,
        doppler_bins: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Estimate (azimuth bin, elevation bin) at the given detection cells.

        The full 4D angle cube is never needed: we only beamform the aperture
        of the cells that actually passed CFAR, then take the peak of the 2D
        angle spectrum.

        Args:
            mimo: `(doppler, elevation, azimuth, range)` virtual array cube.
            range_bins: range index of each detection.
            doppler_bins: Doppler index of each detection.
        """
        if range_bins.size == 0:
            empty = np.zeros(0, dtype=np.int64)
            return empty, empty

        # (K, el, az) -> azimuth beamform -> (K, azimuth bin, el)
        snapshot = mimo[doppler_bins, :, :, range_bins]
        az = np.einsum(
            "ka,mea->mke", self.az_steer, snapshot, optimize=True)
        # -> elevation beamform -> (K, azimuth bin, elevation bin)
        spectrum = np.einsum(
            "mke,je->mkj", az, self.el_steer, optimize=True)
        power = np.abs(spectrum) ** 2

        flat = power.reshape(power.shape[0], -1).argmax(axis=1)
        az_bin, el_bin = np.unravel_index(flat, power.shape[1:])
        return az_bin, el_bin

    # -- top level ---------------------------------------------------------

    def process(
        self, raw: np.ndarray, index: int, timestamp: float,
        dropped_bytes: int = 0, max_detections: int = 512,
    ) -> Products:
        """Run the whole chain on one raw frame."""
        cube = self._prepare(self.range_doppler_cube(raw))
        mimo = self.virtual_array(cube)

        rd = self.range_doppler_power(cube)
        ra = self.range_azimuth_power(mimo)
        mask, snr = self.cfar(rd)

        r_bins, d_bins = np.nonzero(mask)
        if r_bins.size > max_detections:
            order = np.argsort(snr[r_bins, d_bins])[::-1][:max_detections]
            r_bins, d_bins = r_bins[order], d_bins[order]
            mask = np.zeros_like(mask)
            mask[r_bins, d_bins] = True

        az_bins, el_bins = self.angles_at(mimo, r_bins, d_bins)

        ranges = self.range_axis[r_bins]
        velocity = self.velocity_axis[d_bins]
        azimuth = self.azimuth_axis[az_bins]
        elevation = self.elevation_axis[el_bins]
        ground = ranges * np.cos(elevation)

        detections = np.stack([
            r_bins, d_bins, az_bins, el_bins,
            ranges, velocity,
            np.degrees(azimuth), np.degrees(elevation),
            10 * np.log10(np.maximum(snr[r_bins, d_bins], 1e-12)),
            ground * np.sin(azimuth),           # x: right
            ground * np.cos(azimuth),           # y: forward (boresight)
            ranges * np.sin(elevation),         # z: up
        ], axis=-1).astype(np.float32) if r_bins.size else np.zeros(
            (0, len(DETECTION_COLUMNS)), dtype=np.float32)

        return Products(
            index=index, timestamp=timestamp, dropped_bytes=dropped_bytes,
            raw=raw, range_doppler=rd, range_azimuth=ra,
            cfar_mask=mask, cfar_snr=snr, detections=detections)
