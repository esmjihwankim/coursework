"""2D cell-averaging CFAR detection on the range-Doppler power map."""

from __future__ import annotations

import numpy as np


class CFAR:
    """2D cell-averaging CFAR on the range-Doppler power map.

    ## Why this design

    CFAR ("constant false alarm rate") replaces a fixed detection threshold
    with one that tracks the *local* noise/clutter level, so a target is
    reported when it stands out from its own neighbourhood rather than from
    some global number. That matters here because the range-Doppler map of a
    77 GHz radar is wildly non-stationary: near bins are dominated by TX-RX
    leakage, the zero-Doppler column is packed with static clutter, and the
    noise floor falls off with range.

    Layout for a cell under test (CUT), per axis:

        <-train-><-guard-><CUT><-guard-><-train->

    The estimate of the local noise is the mean of the training cells; the
    guard band keeps the target's own energy (spread by the FFT windows) out
    of that estimate.

    ## Implementation choices

    * **Square-law, non-coherently integrated input.** The detector runs on
      `sum over tx,rx |X|^2` rather than on a single antenna, which buys ~10
      dB of integration gain before any thresholding happens.
    * **Summed-area table.** Both the window sum and the guard sum are
      rectangles, so a single integral image gives every cell's training sum
      in O(1) regardless of window size -- the whole map costs two cumsums.
      That is what keeps CFAR at ~1 ms/frame in pure NumPy.
    * **Circular Doppler, clipped range.** Velocity wraps, so the Doppler axis
      is wrapped before the integral image is built. Range does not wrap, so
      cells near 0 m and near max range simply average over fewer training
      cells; the per-cell training count is tracked and the threshold scaled
      accordingly.
    * **Threshold.** For a square-law detector in exponential (Rayleigh
      envelope) clutter with `N` training cells, `P_fa = (1 + a/N)^-N`, so
      `a = N (P_fa^(-1/N) - 1)`. Because we non-coherently integrate 12
      channels the true statistic is Gamma(12), not exponential, so the
      realized false-alarm rate is *lower* than the nominal `pfa`: treat it as
      a well-behaved monotone sensitivity knob, not a calibrated probability.
      `snr_db` overrides it with a flat "X dB above the local mean" rule.
    * **Peak grouping.** A single target lights up a blob of cells. Only cells
      that are a local maximum of the SNR map in their 3x3 neighbourhood
      survive, which turns each blob into one detection.

    Args:
        guard: guard cells per side, `(range, doppler)`.
        train: training cells per side beyond the guard, `(range, doppler)`.
        pfa: nominal per-cell false alarm probability.
        snr_db: if set, use a fixed threshold this many dB above the local
            mean instead of the `pfa` rule.
        min_range_bin: ignore range bins below this (TX-RX leakage / DC).
        max_range_bin: ignore range bins at or above this (None = all).
        zero_doppler_guard: also suppress detections within this many bins of
            zero velocity (static clutter).
        group_peaks: keep only 3x3 local maxima.
        noise_floor_fraction: the local noise estimate is floored at this
            fraction of the frame's mean power, so blanked or noiseless
            neighbourhoods cannot produce an unbounded SNR.
    """

    def __init__(
        self, guard: tuple[int, int] = (2, 2), train: tuple[int, int] = (8, 4),
        pfa: float = 1e-3, snr_db: float | None = None,
        min_range_bin: int = 2, max_range_bin: int | None = None,
        zero_doppler_guard: int = 0, group_peaks: bool = True,
        noise_floor_fraction: float = 1e-4,
    ):
        self.guard_r, self.guard_d = guard
        self.train_r, self.train_d = train
        if self.train_r <= 0 and self.train_d <= 0:
            raise ValueError("CFAR needs at least one training cell.")
        self.pfa = pfa
        self.snr_db = snr_db
        self.min_range_bin = min_range_bin
        self.max_range_bin = max_range_bin
        self.zero_doppler_guard = zero_doppler_guard
        self.group_peaks = group_peaks
        self.noise_floor_fraction = noise_floor_fraction
        self._cache: dict[tuple[int, int], tuple[np.ndarray, ...]] = {}

    def _geometry(self, n_range: int, n_doppler: int):
        """Precompute (and cache) the integral-image index arrays."""
        key = (n_range, n_doppler)
        if key in self._cache:
            return self._cache[key]

        wr = self.guard_r + self.train_r
        wd = self.guard_d + self.train_d
        i = np.arange(n_range)[:, None]
        j = np.arange(n_doppler)[None, :]

        # Range: clipped at the edges (rows of the integral image).
        win_r0 = np.clip(i - wr, 0, n_range)
        win_r1 = np.clip(i + wr + 1, 0, n_range)
        grd_r0 = np.clip(i - self.guard_r, 0, n_range)
        grd_r1 = np.clip(i + self.guard_r + 1, 0, n_range)

        # Doppler: the map is circularly padded by wd, so after the shift
        # every window is fully in bounds and the counts are constant.
        win_c0 = j
        win_c1 = j + 2 * wd + 1
        grd_c0 = j + wd - self.guard_d
        grd_c1 = j + wd + self.guard_d + 1

        n_train = (
            (win_r1 - win_r0) * (win_c1 - win_c0)
            - (grd_r1 - grd_r0) * (grd_c1 - grd_c0)).astype(np.float32)
        n_train = np.maximum(n_train, 1.0)

        if self.snr_db is None:
            alpha = n_train * (self.pfa ** (-1.0 / n_train) - 1.0)
        else:
            alpha = np.full_like(n_train, 10.0 ** (self.snr_db / 10.0))

        geometry = (
            wd, win_r0, win_r1, win_c0, win_c1,
            grd_r0, grd_r1, grd_c0, grd_c1, n_train, alpha.astype(np.float32))
        self._cache[key] = geometry
        return geometry

    def __call__(self, power: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Detect on a `(range, doppler)` power map.

        Returns:
            `(mask, snr)`: boolean detections and the linear ratio of each
                cell to its local noise estimate.
        """
        n_range, n_doppler = power.shape
        (wd, win_r0, win_r1, win_c0, win_c1,
         grd_r0, grd_r1, grd_c0, grd_c1, n_train, alpha) = self._geometry(
            n_range, n_doppler)

        # Circular pad along Doppler, then build the summed-area table.
        if wd > 0:
            padded = np.concatenate(
                [power[:, n_doppler - wd:], power, power[:, :wd]], axis=1)
        else:
            padded = power
        integral = np.zeros(
            (n_range + 1, padded.shape[1] + 1), dtype=np.float64)
        np.cumsum(padded, axis=0, out=integral[1:, 1:])
        np.cumsum(integral[1:, 1:], axis=1, out=integral[1:, 1:])

        def box(r0, r1, c0, c1):
            return (integral[r1, c1] - integral[r0, c1]
                    - integral[r1, c0] + integral[r0, c0])

        train_sum = (
            box(win_r0, win_r1, win_c0, win_c1)
            - box(grd_r0, grd_r1, grd_c0, grd_c1))

        # Floor the local estimate against a fraction of the frame's mean
        # power. Without this, a neighbourhood whose power is ~0 -- blanked
        # Doppler bins after clutter removal, or noiseless synthetic data --
        # divides into an essentially infinite SNR and every adjacent cell
        # "detects".
        floor = max(float(power.mean()) * self.noise_floor_fraction, 1e-12)
        noise = np.maximum(train_sum / n_train, floor).astype(np.float32)

        snr = power / noise
        mask = snr > alpha

        if self.group_peaks:
            mask &= self._local_maxima(snr)

        # Blank the bins we never want to report from.
        mask[:self.min_range_bin] = False
        if self.max_range_bin is not None:
            mask[self.max_range_bin:] = False
        if self.zero_doppler_guard > 0:
            zero = n_doppler // 2
            lo = max(0, zero - self.zero_doppler_guard)
            hi = min(n_doppler, zero + self.zero_doppler_guard + 1)
            mask[:, lo:hi] = False

        return mask, snr

    @staticmethod
    def _local_maxima(x: np.ndarray) -> np.ndarray:
        """3x3 local-maximum mask; Doppler wraps, range is edge-clamped."""
        padded = np.pad(x, ((1, 1), (0, 0)), mode="edge")
        padded = np.pad(padded, ((0, 0), (1, 1)), mode="wrap")
        peak = np.ones_like(x, dtype=bool)
        for di in (0, 1, 2):
            for dj in (0, 1, 2):
                if di == 1 and dj == 1:
                    continue
                neighbour = padded[
                    di:di + x.shape[0], dj:dj + x.shape[1]]
                peak &= x >= neighbour
        return peak
