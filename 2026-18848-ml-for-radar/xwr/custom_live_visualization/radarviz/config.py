"""Radar and capture-card configuration, and the parameters derived from it.

Nothing here talks to hardware: these are plain dataclasses plus the YAML
loader and the constraint checks, so they can be imported and exercised
without a radar attached.
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from typing import Any

import numpy as np

SPEED_OF_LIGHT = 299_792_458.0
"""Speed of light, m/s."""

CONFIG_BASENAME = os.path.join("demo", "config_awr1843aop.yaml")
"""Lab config shipped with the `xwr` checkout, relative to the repo root."""

log = logging.getLogger(__name__)


@dataclass
class RadarConfig:
    """AWR1843(AOP) chirp configuration and the parameters derived from it.

    Field names/units match the `radar:` block of the lab config YAML so the
    same file can be used by this script and by `xwr`.

    Attributes:
        frequency: chirp start frequency, GHz (76.0 or 77.0).
        idle_time: inter-chirp idle time, us.
        adc_start_time: ADC start offset within the ramp, us.
        ramp_end_time: ramp duration, us.
        tx_start_time: TX turn-on offset, us.
        freq_slope: chirp slope, MHz/us.
        adc_samples: ADC samples per chirp (power of two) -> range bins.
        sample_rate: ADC sample rate, ksps.
        frame_length: chirp loops per frame (power of two) -> Doppler bins.
        frame_period: frame periodicity, ms.
        port: control serial port, or None to auto-detect.
    """

    frequency: float = 77.0
    idle_time: float = 181.0
    adc_start_time: float = 4.0
    ramp_end_time: float = 69.0
    tx_start_time: float = 1.0
    freq_slope: float = 57.25
    adc_samples: int = 128
    sample_rate: int = 2000
    frame_length: int = 128
    frame_period: float = 100.0
    port: str | None = None

    # AWR1843AOPEVM: 3 TX, 4 RX, complex (I+Q) 16-bit samples.
    num_tx: int = 3
    num_rx: int = 4
    bytes_per_sample: int = 4

    # -- derived ----------------------------------------------------------

    @property
    def cube_shape(self) -> tuple[int, int, int, int]:
        """Complex data cube shape: (doppler, tx, rx, range)."""
        return (self.frame_length, self.num_tx, self.num_rx, self.adc_samples)

    @property
    def raw_shape(self) -> tuple[int, int, int, int]:
        """Raw int16 IIQQ shape; the last axis holds 2 int16 per sample."""
        return (
            self.frame_length, self.num_tx, self.num_rx,
            self.adc_samples * self.bytes_per_sample // 2)

    @property
    def frame_size(self) -> int:
        """Bytes in one radar frame, as sent by the capture card."""
        return int(np.prod(self.raw_shape)) * 2

    @property
    def chirp_time(self) -> float:
        """Per-loop time T_c (one chirp per TX antenna), us."""
        return (self.idle_time + self.ramp_end_time) * self.num_tx

    @property
    def frame_time(self) -> float:
        """Active frame time, ms."""
        return self.chirp_time * self.frame_length / 1e3

    @property
    def sample_time(self) -> float:
        """ADC dwell T_s, us."""
        return self.adc_samples / self.sample_rate * 1e3

    @property
    def bandwidth(self) -> float:
        """Effective (sampled) bandwidth, MHz."""
        return self.freq_slope * self.sample_time

    @property
    def range_resolution(self) -> float:
        """Range resolution, m."""
        return SPEED_OF_LIGHT / (2 * self.bandwidth * 1e6)

    @property
    def max_range(self) -> float:
        """Maximum unambiguous range, m (complex sampling -> all N bins)."""
        return self.range_resolution * self.adc_samples

    @property
    def wavelength(self) -> float:
        """Wavelength at the center of the sampled sweep, m."""
        return SPEED_OF_LIGHT / (self.center_frequency * 1e9)

    @property
    def center_frequency(self) -> float:
        """Center frequency of the *sampled* part of the chirp, GHz."""
        offset = self.adc_start_time + self.sample_time / 2
        return self.frequency + self.freq_slope * offset / 1e3

    @property
    def doppler_resolution(self) -> float:
        """Doppler (velocity) resolution, m/s."""
        return self.wavelength / (
            2 * self.frame_length * self.chirp_time * 1e-6)

    @property
    def max_doppler(self) -> float:
        """Maximum unambiguous |velocity|, m/s."""
        return self.wavelength / (4 * self.chirp_time * 1e-6)

    @property
    def throughput(self) -> float:
        """Average LVDS/ethernet payload rate, bits/s."""
        return self.frame_size * 8 / self.frame_period * 1e3

    def summary(self) -> str:
        """Human readable derived-parameter table."""
        return "\n".join([
            f"  device            AWR1843AOPEVM ({self.num_tx}tx x "
            f"{self.num_rx}rx, complex 16-bit)",
            f"  T_s (ADC dwell)   {self.sample_time:.2f} us  "
            f"(excess ramp {self.excess_ramp_time:+.2f} us)",
            f"  RF sweep          {self.freq_slope * self.ramp_end_time:.0f}"
            f" MHz  ({self.frequency:.2f} -> "
            f"{self.frequency + self.freq_slope * self.ramp_end_time / 1e3:.2f}"
            " GHz)",
            f"  eff. bandwidth    {self.bandwidth:.0f} MHz",
            f"  range res / max   {self.range_resolution * 100:.2f} cm / "
            f"{self.max_range:.2f} m  ({self.adc_samples} bins)",
            f"  doppler res / max {self.doppler_resolution:.4f} m/s / "
            f"+/-{self.max_doppler:.2f} m/s  ({self.frame_length} bins)",
            f"  T_c / frame time  {self.chirp_time:.0f} us / "
            f"{self.frame_time:.1f} ms  "
            f"({100 * self.frame_time / self.frame_period:.0f}% duty)",
            f"  frame size        {self.frame_size / 1024:.0f} KiB  -> "
            f"{self.throughput / 1e6:.0f} Mbps at "
            f"{1000 / self.frame_period:.1f} fps",
        ])

    @property
    def excess_ramp_time(self) -> float:
        """Ramp time left over after the ADC window closes, us."""
        return self.ramp_end_time - self.adc_start_time - self.sample_time


@dataclass
class CaptureConfig:
    """DCA1000EVM capture card configuration (matches the YAML `capture:`)."""

    sys_ip: str = "192.168.33.30"
    fpga_ip: str = "192.168.33.180"
    data_port: int = 4098
    config_port: int = 4096
    timeout: float = 1.0
    socket_buffer: int = 6_291_456
    delay: float = 5.0

    @property
    def throughput(self) -> float:
        """Theoretical capture-card payload rate given the packet delay."""
        packet_time = 1466 * 8 / 1e9 + self.delay / 1e6
        return 1466 * 8 / packet_time


def default_config_path(start: str | None = None) -> str | None:
    """Find the lab's `demo/config_awr1843aop.yaml` above this package.

    The entry script lives a couple of directories below the `xwr` checkout
    that carries the YAML, and may be run from anywhere, so the path is found
    by walking upward rather than assumed to sit next to the script.

    Args:
        start: directory to search upward from; defaults to this file's.

    Returns:
        The config path, or None if no checkout was found.
    """
    here = start if start is not None else os.path.dirname(
        os.path.abspath(__file__))
    for _ in range(5):
        candidate = os.path.join(here, CONFIG_BASENAME)
        if os.path.exists(candidate):
            return candidate
        parent = os.path.dirname(here)
        if parent == here:
            break
        here = parent
    return None


def load_config(path: str | None) -> tuple[RadarConfig, CaptureConfig]:
    """Load radar/capture config from a YAML file, falling back to defaults.

    Unknown keys are ignored with a warning so the same YAML that `xwr` uses
    (which carries e.g. a `device:` field) can be reused verbatim.
    """
    radar_kw: dict[str, Any] = {}
    capture_kw: dict[str, Any] = {}

    if path is not None:
        try:
            import yaml
        except ImportError:
            log.warning("pyyaml not installed; using built-in defaults.")
        else:
            with open(path) as f:
                cfg = yaml.safe_load(f) or {}
            radar_kw = dict(cfg.get("radar", {}))
            capture_kw = dict(cfg.get("capture", {}))
            device = radar_kw.pop("device", None)
            if device is not None and "AWR1843" not in str(device):
                log.warning(
                    "Config declares device=%s; this script only implements "
                    "the AWR1843 (AOP) command set.", device)

    def _filter(kw: dict, cls: type) -> dict:
        valid = set(cls.__dataclass_fields__)
        out = {}
        for k, v in kw.items():
            if k in valid:
                out[k] = v
            else:
                log.warning("Ignoring unknown %s key: %s", cls.__name__, k)
        return out

    return (
        RadarConfig(**_filter(radar_kw, RadarConfig)),
        CaptureConfig(**_filter(capture_kw, CaptureConfig)),
    )


def check_constraints(
    radar: RadarConfig, capture: CaptureConfig
) -> list[tuple[str, bool, str]]:
    """Sanity-check a configuration against known AWR1843 hardware limits.

    Returns:
        `(name, passed, detail)` for each check; nothing is raised, the caller
        decides what to do about failures.
    """
    frame_duty = 100 * radar.frame_time / radar.frame_period
    rf_duty = 100 * (
        radar.ramp_end_time * radar.num_tx * radar.frame_length
        / (radar.frame_period * 1e3))
    end_freq = radar.frequency + radar.freq_slope * radar.ramp_end_time / 1e3
    net_util = 100 * radar.throughput / capture.throughput
    buf_frames = capture.socket_buffer / radar.frame_size

    def pow2(n: int) -> bool:
        return n > 0 and (n & (n - 1)) == 0

    return [
        ("FrameDutyCycle", frame_duty < 99,
         f"{frame_duty:.1f}% of the frame period (< 99%)"),
        ("RFDutyCycle", rf_duty < 50,
         f"{rf_duty:.1f}% RF on-time (< 50%)"),
        ("ExcessRampTime", radar.excess_ramp_time >= 0,
         f"{radar.excess_ramp_time:+.2f} us left after the ADC window (>= 0)"),
        ("CubeSizeLimit", radar.frame_size <= 1024 * 1024,
         f"{radar.frame_size // 1024} KiB / 1024 KiB L3"),
        ("FrameLengthPowerOfTwo", pow2(radar.frame_length),
         f"frame_length = {radar.frame_length}"),
        ("AdcSamplesPowerOfTwo", pow2(radar.adc_samples),
         f"adc_samples = {radar.adc_samples}"),
        ("SampleRate", 2000 <= radar.sample_rate <= 25000,
         f"{radar.sample_rate} ksps (2000-25000)"),
        ("FrequencyRange", 76.0 <= radar.frequency and end_freq <= 81.0,
         f"{radar.frequency:.2f}-{end_freq:.2f} GHz (76-81)"),
        ("MaxBandwidth", radar.bandwidth <= 4000.0,
         f"{radar.bandwidth:.0f} MHz sampled (<= 4000)"),
        ("NetworkUtilization", net_util < 80,
         f"{net_util:.1f}% of the capture card (< 80%)"),
        ("ReceiveBuffer", buf_frames >= 2,
         f"socket buffer holds {buf_frames:.1f} frames (>= 2)"),
    ]
