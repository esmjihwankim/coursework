"""Numerical checks on the DSP kernels; no hardware and no GUI.

Run with `--selftest`. Each check is a property that must hold independently
of the hardware -- an identity between two ways of computing the same thing,
a round trip, or a synthetic target landing in the bin it was injected into.
"""

from __future__ import annotations

import time

import numpy as np

from .cfar import CFAR
from .config import RadarConfig
from .dsp import ARRAY_LAYOUTS, iiqq_from_iq, iq_from_iiqq, steering_matrix
from .pipeline import DETECTION_COLUMNS, Pipeline
from .sources import SimulatedSource


def selftest() -> int:
    """Numerically verify the DSP kernels. Returns a process exit code."""
    failures = []

    def check(name: str, ok: bool, detail: str = "") -> None:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
              + (f"  {detail}" if detail else ""))
        if not ok:
            failures.append(name)

    print("DSP self-test")

    # 1. The steering matmul is exactly a zero-padded, shifted FFT.
    rng = np.random.default_rng(0)
    for elements, bins in ((3, 64), (4, 32), (4, 33), (12, 128)):
        x = (rng.normal(size=elements)
             + 1j * rng.normal(size=elements)).astype(np.complex64)
        got = steering_matrix(elements, bins) @ x
        want = np.fft.fftshift(np.fft.fft(x, n=bins))
        err = np.abs(got - want).max()
        check(f"steering_matrix({elements}->{bins}) == fftshift(fft)",
              err < 1e-3, f"max err {err:.2e}")

    # 2. IIQQ round trip.
    iq = (rng.integers(-2000, 2000, (2, 8))
          + 1j * rng.integers(-2000, 2000, (2, 8))).astype(np.complex64)
    check("iq_from_iiqq(iiqq_from_iq(x)) == x",
          np.array_equal(iq_from_iiqq(iiqq_from_iq(iq)), iq))

    # 3. Covariance range-azimuth == direct beamforming, for both layouts.
    cfg = RadarConfig(adc_samples=32, frame_length=16)
    cube = (rng.normal(size=cfg.cube_shape)
            + 1j * rng.normal(size=cfg.cube_shape)).astype(np.complex64)
    for layout in sorted(ARRAY_LAYOUTS):
        pipe = Pipeline(cfg, azimuth_bins=32, elevation_bins=16, array=layout)
        mimo = pipe.virtual_array(cube)
        fast = pipe.range_azimuth_power(mimo)
        beam = np.einsum(
            "ka,dean->dken", pipe.az_steer, mimo, optimize=True)
        slow = (np.abs(beam) ** 2).sum(axis=(0, 2)).T
        rel = np.abs(fast - slow).max() / slow.max()
        check(f"covariance range-azimuth == direct beamforming [{layout}]",
              rel < 1e-4, f"max rel err {rel:.2e}")

    # 4. Parseval: our antenna power sum == the mean over angle-FFT bins,
    #    which is what xwr's demo.py plots. Layout-independent.
    for layout in sorted(ARRAY_LAYOUTS):
        pipe = Pipeline(cfg, azimuth_bins=32, elevation_bins=16, array=layout)
        mimo = pipe.virtual_array(cube)
        angle = np.einsum(
            "ka,dean->dken", pipe.az_steer, mimo, optimize=True)
        angle = np.einsum(
            "dken,je->dkjn", angle, pipe.el_steer, optimize=True)
        rms = np.sqrt(np.mean(np.abs(angle) ** 2, axis=(1, 2))).T
        ours = np.sqrt(pipe.range_doppler_power(cube))
        rel = np.abs(rms - ours).max() / ours.max()
        check(f"sqrt(mean |angle FFT|^2) == sqrt(our power) [{layout}]",
              rel < 1e-4, f"max rel err {rel:.2e}")

    # 5. Integral-image CFAR training sums == brute force.
    detector = CFAR(guard=(1, 1), train=(2, 2), snr_db=0.0,
                    min_range_bin=0, group_peaks=False)
    power = rng.random((12, 10)).astype(np.float32) + 0.5
    _, snr = detector(power)
    noise = power / snr
    n_r, n_d = power.shape
    wr, wd = 1 + 2, 1 + 2
    brute = np.zeros_like(power)
    for i in range(n_r):
        for j in range(n_d):
            total, count = 0.0, 0
            for a in range(i - wr, i + wr + 1):
                if not 0 <= a < n_r:
                    continue
                for b in range(j - wd, j + wd + 1):
                    if abs(a - i) <= 1 and abs(b - j) <= 1:
                        continue
                    total += power[a, b % n_d]
                    count += 1
            brute[i, j] = total / count
    err = np.abs(noise - brute).max()
    check("CFAR summed-area noise == brute force", err < 1e-4,
          f"max err {err:.2e}")

    # 6. End-to-end: a synthetic target lands in the expected bins.
    cfg = RadarConfig()
    pipe = Pipeline(cfg, azimuth_bins=64, elevation_bins=32,
                    cfar=CFAR(pfa=1e-4, min_range_bin=2))
    target = (2.0, 0.4, 20.0, 10.0, 1500.0)
    source = SimulatedSource(
        cfg, targets=[target], noise=40.0, realtime=False)
    frame = source.get(0)
    assert frame is not None
    product = pipe.process(frame.data, 0, 0.0)
    col = DETECTION_COLUMNS.index
    if not len(product.detections):
        check("synthetic target detected", False, "no detections")
    else:
        best = product.detections[
            np.argmax(product.detections[:, col("snr_db")])]
        want_r, want_v, want_az, want_el, _ = target
        errors = {
            "range": (best[col("range_m")], want_r, 2 * cfg.range_resolution),
            "velocity": (best[col("velocity_mps")], want_v,
                         2 * cfg.doppler_resolution),
            "azimuth": (best[col("azimuth_deg")], want_az, 8.0),
            "elevation": (best[col("elevation_deg")], want_el, 8.0),
        }
        for name, (got, want, tol) in errors.items():
            check(f"synthetic target {name}", abs(got - want) <= tol,
                  f"got {got:+.3f}, want {want:+.3f} (tol {tol:.3f})")

    # 7. Throughput.
    start = time.perf_counter()
    for _ in range(10):
        pipe.process(frame.data, 0, 0.0)
    per_frame = (time.perf_counter() - start) / 10
    check(f"pipeline keeps up with {1000 / cfg.frame_period:.0f} fps",
          per_frame < cfg.frame_period / 1000,
          f"{per_frame * 1000:.1f} ms/frame")

    print(f"\n{'all checks passed' if not failures else 'FAILED: ' + ', '.join(failures)}")
    return 1 if failures else 0
