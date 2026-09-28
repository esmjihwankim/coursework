"""Command line: argument definitions and the wiring that builds a session.

The high-level half of the program, kept beside the entry script: what the
user can ask for, and which objects that turns into. The parts it assembles
-- radar control, capture, DSP, CFAR, plotting -- live in the `radarviz`
package, and so does every low-level detail.
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any

from radarviz import DESCRIPTION
from radarviz.cfar import CFAR
from radarviz.config import (
    check_constraints, default_config_path, load_config)
from radarviz.display import Display
from radarviz.dsp import ARRAY_LAYOUTS
from radarviz.pipeline import Pipeline
from radarviz.plotting import ScaleSettings
from radarviz.recording import Recorder
from radarviz.selftest import selftest
from radarviz.sources import HardwareSource, SimulatedSource
from session import run

log = logging.getLogger(__name__)


def build_parser() -> argparse.ArgumentParser:
    """CLI definition."""
    default_config = default_config_path()

    p = argparse.ArgumentParser(
        description=DESCRIPTION,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    g = p.add_argument_group("configuration")
    g.add_argument("--config", default=default_config,
                   help="radar/capture YAML (default: %(default)s)")
    g.add_argument("--port", default=None,
                   help="radar control serial port (default: auto-detect)")
    g.add_argument("--outdir", default="captures",
                   help="where snapshots and recordings go")
    g.add_argument("--strict", action="store_true",
                   help="refuse to start if a config constraint fails")

    g = p.add_argument_group("processing")
    g.add_argument("--array", choices=sorted(ARRAY_LAYOUTS), default="aop",
                   help="MIMO virtual array layout. 'aop' is correct for the "
                        "AWR1843AOPEVM. 'boost' reproduces xwr's "
                        "'demo.py --rsp AWR1843Boost' for A/B comparison, but "
                        "on AOP hardware it scrambles azimuth and elevation: "
                        "correct only at boresight, +/-20 deg compressed to "
                        "+/-7 deg, sign inverted beyond +/-40 deg")
    g.add_argument("--azimuth-bins", type=int, default=128,
                   help="zero-padded azimuth FFT size (lab requires >= 32)")
    g.add_argument("--elevation-bins", type=int, default=32,
                   help="zero-padded elevation FFT size")
    g.add_argument("--range-window", action="store_true",
                   help="apply a Hann window to the range FFT: -59 dB instead "
                        "of -32.7 dB sidelobes, at 1.36x the mainlobe width")
    g.add_argument("--doppler-window", action="store_true",
                   help="apply a Hann window to the Doppler FFT: removes the "
                        "sidelobe streak across velocity through a strong "
                        "target, at 1.45x the mainlobe width")
    g.add_argument("--no-tdm-comp", action="store_true",
                   help="skip TDM-MIMO Doppler phase compensation")
    g.add_argument("--doppler-sign", type=int, choices=(1, -1), default=1,
                   help="flip the velocity axis")
    g.add_argument("--azimuth-sign", type=int, choices=(1, -1), default=1,
                   help="flip the azimuth axis")
    g.add_argument("--elevation-sign", type=int, choices=(1, -1), default=-1,
                   help="flip the elevation axis")
    g.add_argument("--clutter-removal", action="store_true",
                   help="start with zero-Doppler clutter removal enabled")

    g = p.add_argument_group("CFAR")
    g.add_argument("--cfar-guard", type=int, nargs=2, default=(2, 2),
                   metavar=("RANGE", "DOPPLER"), help="guard cells per side")
    g.add_argument("--cfar-train", type=int, nargs=2, default=(8, 4),
                   metavar=("RANGE", "DOPPLER"), help="training cells per side")
    g.add_argument("--cfar-snr-db", type=float, default=15.0,
                   help="detection threshold, dB over the local noise mean. "
                        "The default rejects the -32.7 dB sidelobes that "
                        "unwindowed FFTs leave around strong targets")
    g.add_argument("--cfar-pfa", type=float, default=None,
                   help="use a nominal per-cell false alarm probability "
                        "instead of --cfar-snr-db (e.g. 1e-3). Only sensible "
                        "with --range-window --doppler-window")
    g.add_argument("--cfar-min-range-bin", type=int, default=2,
                   help="ignore range bins below this")
    g.add_argument("--cfar-max-range-bin", type=int, default=None,
                   help="ignore range bins at or above this")
    g.add_argument("--cfar-zero-doppler-guard", type=int, default=0,
                   help="also suppress this many bins around zero velocity")
    g.add_argument("--cfar-noise-floor", type=float, default=1e-4,
                   help="floor the local noise at this fraction of the frame "
                        "mean power")
    g.add_argument("--no-peak-grouping", action="store_true",
                   help="report every cell over threshold, not just peaks")
    g.add_argument("--max-detections", type=int, default=512,
                   help="cap on detections per frame (strongest kept)")

    g = p.add_argument_group("capture")
    g.add_argument("--snapshot-before", type=int, default=2,
                   help="frames kept before a space-bar trigger")
    g.add_argument("--snapshot-after", type=int, default=2,
                   help="frames collected after a space-bar trigger")
    g.add_argument("--no-save-raw", action="store_true",
                   help="omit the int16 IIQQ cube from snapshots")
    g.add_argument("--no-preview", action="store_true",
                   help="skip the snapshot preview PNG")
    g.add_argument("--record", action="store_true",
                   help="begin continuous raw recording immediately")

    g = p.add_argument_group("display")
    g.add_argument("--scale", choices=("amplitude", "db"), default="amplitude",
                   help="heatmap transfer function; 'd' toggles it live. "
                        "'amplitude' is sqrt(power) over [min, max], matching "
                        "xwr's demo.py: only the strongest returns show. "
                        "'db' is log power windowed up from the noise floor: "
                        "every reflector and the noise texture show")
    g.add_argument("--dynamic-range", type=float, default=55.0,
                   help="--scale db only: dB above the noise floor shown; "
                        "stronger returns (e.g. TX-RX leakage) saturate")
    g.add_argument("--clim-min-range-bin", type=int, default=3,
                   help="exclude the first N range bins when computing the "
                        "colour limits (they still render). Antenna coupling "
                        "at bin 0-1 is often the strongest cell and would "
                        "otherwise crush the scene. 0 = bit-exact xwr")
    g.add_argument("--no-display", action="store_true",
                   help="run headless (for testing or pure recording)")

    g = p.add_argument_group("offline / testing")
    g.add_argument("--selftest", action="store_true",
                   help="verify the DSP kernels and exit")
    g.add_argument("--simulate", action="store_true",
                   help="synthesize frames instead of using hardware")
    g.add_argument("--frames", type=int, default=None,
                   help="stop after this many frames")
    g.add_argument("--snapshot-at", type=int, action="append", default=None,
                   metavar="N", help="trigger a snapshot at frame N (repeatable)")
    g.add_argument("-v", "--verbose", action="count", default=0,
                   help="-v for debug logging")

    return p


def build_pipeline(args: argparse.Namespace, radar_cfg) -> Pipeline:
    """Assemble the CFAR detector and processing chain from parsed arguments."""
    detector = CFAR(
        guard=tuple(args.cfar_guard), train=tuple(args.cfar_train),
        pfa=args.cfar_pfa if args.cfar_pfa is not None else 1e-3,
        snr_db=None if args.cfar_pfa is not None else args.cfar_snr_db,
        min_range_bin=args.cfar_min_range_bin,
        max_range_bin=args.cfar_max_range_bin,
        zero_doppler_guard=args.cfar_zero_doppler_guard,
        group_peaks=not args.no_peak_grouping,
        noise_floor_fraction=args.cfar_noise_floor)

    pipeline = Pipeline(
        radar_cfg,
        azimuth_bins=args.azimuth_bins, elevation_bins=args.elevation_bins,
        range_window=args.range_window,
        doppler_window=args.doppler_window,
        tdm_compensation=not args.no_tdm_comp,
        doppler_sign=args.doppler_sign, azimuth_sign=args.azimuth_sign,
        elevation_sign=args.elevation_sign, cfar=detector,
        array=args.array)
    pipeline.clutter_removal = args.clutter_removal

    if args.array != "aop":
        log.warning(
            "Using the %r virtual array on AOP hardware: azimuth and "
            "elevation are scrambled (correct only at boresight, sign "
            "inverted beyond +/-40 deg). For A/B comparison against xwr "
            "only -- do not treat saved angles as measurements.", args.array)
    if not (args.range_window or args.doppler_window):
        log.info(
            "Hann windows off (xwr parity): sharpest mainlobe (1.0 range bin "
            "vs 1.36), at -32.7 dB sidelobes instead of -59 dB. CFAR is "
            "thresholded at %.0f dB over noise to reject them.",
            args.cfar_snr_db if args.cfar_pfa is None else float("nan"))
        if args.cfar_pfa is not None:
            log.warning(
                "--cfar-pfa with the windows off: expect ~100 sidelobe "
                "detections per frame around strong targets. Add "
                "--range-window --doppler-window, or drop --cfar-pfa.")
    return pipeline


def main(argv: list[str] | None = None) -> int:
    """Entry point."""
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S")
    logging.getLogger("matplotlib").setLevel(logging.WARNING)

    if args.selftest:
        return selftest()

    radar_cfg, capture_cfg = load_config(args.config)
    if args.port is not None:
        radar_cfg.port = args.port

    print("\nRadar configuration"
          + (f" (from {args.config})" if args.config else " (defaults)"))
    print(radar_cfg.summary())
    print()

    failed = False
    for name, ok, detail in check_constraints(radar_cfg, capture_cfg):
        log.log(logging.INFO if ok else logging.WARNING,
                "%-22s %s  %s", name, "ok  " if ok else "FAIL", detail)
        failed |= not ok
    if failed and args.strict:
        log.error("Configuration constraints failed and --strict is set.")
        return 1

    pipeline = build_pipeline(args, radar_cfg)
    scale = ScaleSettings(
        scale=args.scale, dynamic_range=args.dynamic_range,
        min_range_bin=args.clim_min_range_bin)

    recorder = Recorder(
        args.outdir, radar_cfg, pipeline,
        before=args.snapshot_before, after=args.snapshot_after,
        save_raw=not args.no_save_raw, save_preview=not args.no_preview,
        scale=scale)

    source: Any
    if args.simulate:
        log.warning("SIMULATION MODE: frames are synthetic, not from hardware.")
        source = SimulatedSource(radar_cfg, realtime=not args.no_display)
    else:
        source = HardwareSource(radar_cfg, capture_cfg)

    display = None if args.no_display else Display(pipeline, scale=scale)

    if args.record:
        recorder.toggle_recording()

    run(source, pipeline, recorder, display, scale,
        max_detections=args.max_detections, max_frames=args.frames,
        snapshot_at=args.snapshot_at or (), sys_ip=capture_cfg.sys_ip)
    return 0


if __name__ == "__main__":
    sys.exit(main())
