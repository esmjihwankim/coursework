"""Shared fixtures; also puts the package's parent on `sys.path`.

The modules under test live in `custom_live_visualization/radarviz/`, one
directory up from here, and the project is not pip-installed, so the import
path is set up explicitly rather than relying on how pytest was invoked.
"""

from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from radarviz.cfar import CFAR                       # noqa: E402
from radarviz.config import RadarConfig              # noqa: E402
from radarviz.pipeline import Pipeline               # noqa: E402
from radarviz.sources import SimulatedSource         # noqa: E402

TARGET = (2.0, 0.4, 20.0, 10.0, 1500.0)
"""A single point target: range m, velocity m/s, azimuth deg, elevation deg, amplitude."""


@pytest.fixture
def radar_cfg() -> RadarConfig:
    """The default AWR1843AOPEVM lab configuration."""
    return RadarConfig()


@pytest.fixture
def small_cfg() -> RadarConfig:
    """A cut-down cube, for tests that only care about shapes and algebra."""
    return RadarConfig(adc_samples=32, frame_length=16)


@pytest.fixture
def pipeline(radar_cfg: RadarConfig) -> Pipeline:
    """Full-size pipeline with a detector sensitive enough to see `TARGET`."""
    return Pipeline(
        radar_cfg, azimuth_bins=64, elevation_bins=32,
        cfar=CFAR(pfa=1e-4, min_range_bin=2))


@pytest.fixture
def one_target_frame(radar_cfg: RadarConfig):
    """One synthetic frame containing `TARGET`, with a fixed noise seed."""
    source = SimulatedSource(
        radar_cfg, targets=[TARGET], noise=40.0, realtime=False)
    frame = source.get(0)
    assert frame is not None
    return frame
