"""Real-time visualization + capture for the TI AWR1843AOPEVM + DCA1000EVM.

Standalone: this package does **not** import `xwr`. Everything (radar serial
control, DCA1000EVM UDP capture, range-Doppler-azimuth-elevation processing,
CFAR detection, point cloud, plotting, recording) is implemented here so it
can be read and modified without touching the library.

Written for 18-848 Lab 1 (https://radarml.github.io/18848/lab1/).

Modules
-------
    config      chirp/capture dataclasses, YAML loading, constraint checks
    radar       AWR1843(AOP) serial CLI driver
    capture     DCA1000EVM control + UDP frame reassembly
    dsp         sample packing, windows, steering matrices, array layouts
    cfar        2D cell-averaging CFAR detector
    pipeline    per-frame chain: FFTs -> beamforming -> detections
    sources     live hardware capture and the synthetic stand-in
    plotting    display scaling, axis labels, snapshot preview sheets
    display     the live four-panel window
    recording   snapshot ring buffer and continuous raw recording
    selftest    numerical checks on the DSP kernels

The high-level layer sits one directory up, beside the entry script:
`cli.py` defines the arguments and assembles a session, `session.py` runs
the acquisition loop. Everything below that level is here.

Live panels
-----------
    1. range-Doppler heatmap       (dB, non-coherently integrated over the
                                    12 virtual antennas)
    2. range-azimuth heatmap       (dB, Bartlett beamformer == zero-padded
                                    azimuth FFT)
    3. CFAR detections             (CA-CFAR mask over the range-Doppler map)
    4. Cartesian point cloud       (bird's eye, colored by radial velocity)

Keyboard
--------
    space   save a 5-frame snapshot: the 2 frames *before* the keypress, the
            current frame, and the 2 frames *after* it. The preview PNG has
            one row per frame and the same four panels as the live view.
    t       toggle continuous raw recording to disk.
    m       toggle static-clutter (zero-Doppler) removal.
    d       toggle the heatmap scale between linear amplitude and dB.
    q       quit (also stops the radar cleanly).

Offline / no-hardware modes
---------------------------
    --selftest    numerical checks on the DSP kernels; no hardware, no GUI.
    --simulate    synthesize frames with point targets and run the full
                  pipeline; useful to exercise the UI and the save path.

Signal-processing conventions (see the notes in `dsp.py`):
    cube axes are (doppler, tx, rx, range); the AWR1843AOP virtual array is
    elevation = rx (4 elements), azimuth = tx (3 elements).

Comparing against xwr's demo.py
-------------------------------
Defaults here match `xwr`'s `demo/demo.py`: no Hann windows, azimuth padded to
128, and heatmaps drawn as linear amplitude over `[min, max]`. The plotted
quantity is the same to within float32 -- by Parseval, our sum of `|X|^2` over
the 12 virtual antennas equals the mean of `|angle FFT|^2` over the angle bins,
for any array layout (`--selftest` checks this).

!!! warning "`--rsp AWR1843Boost` is not valid on AOP hardware"

    `demo.py` defaults to the BOOST virtual array, which assumes TX1/TX3 feed
    a contiguous 8-element *horizontal* row. On the AOPEVM the RX index runs
    along elevation instead, so that layout mixes the two angle axes. Measured
    against known targets, it reports the correct azimuth only at boresight,
    compresses +/-20 deg to +/-7 deg, and inverts the sign beyond +/-40 deg,
    while looking 2-3x sharper than the true 49.5 deg beamwidth of the AOP's
    3-element azimuth aperture. Use `--rsp AWR1843AOP` with xwr; `--array
    boost` here reproduces the incorrect layout for A/B comparison only.
"""

from __future__ import annotations

DESCRIPTION = __doc__
"""Program overview; argparse prints this for `--help`."""

from .capture import CaptureError, DCA1000EVM, FrameReceiver
from .cfar import CFAR
from .config import (
    SPEED_OF_LIGHT, CaptureConfig, RadarConfig, check_constraints,
    default_config_path, load_config)
from .display import Display
from .dsp import (
    ARRAY_LAYOUTS, angle_grid, hann, iiqq_from_iq, iq_from_iiqq,
    steering_matrix, to_db, virtual_array_aop, virtual_array_boost)
from .pipeline import DETECTION_COLUMNS, Pipeline, Products
from .plotting import ScaleSettings, label_angle_axis, render_snapshot_preview
from .radar import AWR1843AOP, RadarError
from .recording import Recorder
from .sources import HardwareSource, RawFrame, SimulatedSource

__all__ = [
    "ARRAY_LAYOUTS", "AWR1843AOP", "CFAR", "CaptureConfig", "CaptureError",
    "DCA1000EVM", "DESCRIPTION", "DETECTION_COLUMNS", "Display",
    "FrameReceiver", "HardwareSource", "Pipeline", "Products", "RadarConfig",
    "RadarError", "RawFrame", "Recorder", "SPEED_OF_LIGHT", "ScaleSettings",
    "SimulatedSource", "angle_grid", "check_constraints",
    "default_config_path", "hann", "iiqq_from_iq", "iq_from_iiqq",
    "label_angle_axis", "load_config", "render_snapshot_preview",
    "steering_matrix", "to_db", "virtual_array_aop", "virtual_array_boost",
]
