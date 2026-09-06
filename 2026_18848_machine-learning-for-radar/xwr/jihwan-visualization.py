#!/usr/bin/env python3
"""Real-time visualization + capture for the TI AWR1843AOPEVM + DCA1000EVM.

Standalone: this script does **not** import `xwr`. Everything (radar serial
control, DCA1000EVM UDP capture, range-Doppler-azimuth-elevation processing,
CFAR detection, point cloud, plotting, recording) is implemented here so it can
be read top to bottom and modified without touching the library.

Written for 18-848 Lab 1 (https://radarml.github.io/18848/lab1/).

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
            current frame, and the 2 frames *after* it.
    t       toggle continuous raw recording to disk.
    m       toggle static-clutter (zero-Doppler) removal.
    q       quit (also stops the radar cleanly).

Offline / no-hardware modes
---------------------------
    --selftest    numerical checks on the DSP kernels; no hardware, no GUI.
    --simulate    synthesize frames with point targets and run the full
                  pipeline; useful to exercise the UI and the save path.

Signal-processing conventions (see the module-level notes further down):
    cube axes are (doppler, tx, rx, range); the AWR1843AOP virtual array is
    elevation = rx (4 elements), azimuth = tx (3 elements).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import queue
import re
import socket
import struct
import sys
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Any, Callable

import numpy as np

SPEED_OF_LIGHT = 299_792_458.0
"""Speed of light, m/s."""

log = logging.getLogger("radarviz")


# ---------------------------------------------------------------------------
# 1. Configuration
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# 2. Radar control: the mmWave demo firmware UART CLI
# ---------------------------------------------------------------------------


class RadarError(Exception):
    """The radar returned a non-`Done` response."""


class AWR1843AOP:
    """Serial CLI driver for the TI mmWave demo firmware on an AWR1843(AOP).

    The firmware exposes an ASCII command prompt (`mmwDemo:/>`) over UART. We
    send the configuration commands in the order the demo expects, then
    `sensorStart`. Only the commands that matter for a raw LVDS capture are
    parameterized; the rest are mandatory-but-irrelevant boilerplate that the
    firmware refuses to start without.

    Args:
        port: serial device, or None to auto-detect the CP2105 "Enhanced"
            interface (AOPEVM) / XDS110 (BOOST boards).
        baudrate: control UART baudrate; the demo firmware fixes this at 115200.
    """

    PROMPT = "mmwDemo:/>"
    PORT_PATTERN = r"(?=.*CP2105)(?=.*Enhanced)|XDS110"

    def __init__(self, port: str | None = None, baudrate: int = 115200):
        import serial  # imported lazily: --simulate does not need pyserial

        if port is None:
            port = self._detect_port()
            log.info("Auto-detected radar control port: %s", port)

        self.serial = serial.Serial(port, baudrate, timeout=None)
        if hasattr(self.serial, "set_low_latency_mode"):
            try:
                self.serial.set_low_latency_mode(True)
            except (ValueError, OSError) as exc:
                log.warning("Low-latency serial mode unavailable: %s", exc)
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

    @classmethod
    def _detect_port(cls) -> str:
        from serial.tools import list_ports

        ports = sorted(list_ports.comports(), key=lambda p: p.device)
        for p in ports:
            if p.description and re.match(
                    cls.PORT_PATTERN, p.description, re.IGNORECASE):
                return p.device
        raise RadarError(
            "Could not auto-detect the radar control port. Available: "
            f"{[p.device for p in ports]}. Pass --port explicitly.")

    def _read_until_prompt(self, timeout: float) -> str:
        buf = bytearray()
        needle = self.PROMPT.encode()
        deadline = time.time() + timeout
        while not buf.endswith(needle):
            buf.extend(self.serial.read(self.serial.in_waiting))
            if time.time() > deadline:
                raise TimeoutError(
                    "Radar did not respond with a prompt. Partial buffer: "
                    f"{buf.decode('utf-8', 'replace')!r}")
            time.sleep(0.001)
        return buf.decode("utf-8", "replace")

    def send(self, command: str, timeout: float = 10.0) -> None:
        """Send one CLI command (or a multi-line block) and check the reply.

        Lines starting with `#` are treated as comments and not transmitted.
        """
        if "\n" in command:
            for line in command.split("\n"):
                line = line.strip()
                if line and not line.startswith("#"):
                    self.send(line, timeout=timeout)
            return

        log.debug("radar <- %s", command)
        self.serial.write((command + "\n").encode("ascii"))
        raw = self._read_until_prompt(timeout)
        reply = (
            raw.replace(self.PROMPT, "").replace(command, "")
            .strip(" ;\r\n\t"))
        log.debug("radar -> %s", reply)

        if reply == "Done" or "*****" in reply:
            return
        if reply.startswith(("Ignored", "Skipped", "Debug")):
            log.warning("radar: %s", reply)
            return
        raise RadarError(f"{command!r} -> {reply!r}")

    def configure(self, cfg: RadarConfig) -> None:
        """Push a full configuration; leaves the sensor stopped."""
        rx_mask = (1 << cfg.num_rx) - 1
        tx_mask = (1 << cfg.num_tx) - 1

        # TDM-MIMO: one chirp per TX antenna, fired in sequence.
        chirps = "\n".join(
            f"chirpCfg {i} {i} 0 0.0 0.0 0.0 0.0 {1 << i}"
            for i in range(cfg.num_tx))
        # 12 (real, imag) pairs = identity phase compensation per TX-RX pair.
        phase = " ".join(["0 1"] * (cfg.num_tx * cfg.num_rx))

        commands = f"""
        sensorStop
        flushCfg
        # legacy frame mode (one profile, no subframes)
        dfeDataOutputMode 1
        # 16-bit complex-1x samples, I in the MSB, non-interleaved
        adcCfg 2 1
        adcbufCfg -1 0 1 1 1
        profileCfg 0 {cfg.frequency} {cfg.idle_time} {cfg.adc_start_time} \
{cfg.ramp_end_time} 0 0 {cfg.freq_slope} {cfg.tx_start_time} \
{cfg.adc_samples} {cfg.sample_rate} 0 0 30
        channelCfg {rx_mask} {tx_mask} 0
{chirps}
        frameCfg 0 {cfg.num_tx - 1} {cfg.frame_length} 0 {cfg.frame_period} 1 0.0
        compRangeBiasAndRxChanPhase 0.0 {phase}
        # stream raw ADC over LVDS, no HSI header, hardware triggered
        lvdsStreamCfg -1 0 1 0
        lowPower 0 0
        # --- mandatory boilerplate: on-chip processing we do not use ---
        guiMonitor -1 0 0 0 0 0 0
        cfarCfg -1 0 0 4 2 3 1 15.0 1
        cfarCfg -1 1 0 4 2 3 1 15.0 1
        multiObjBeamForming -1 0 0.5
        calibDcRangeSig -1 0 -5 8 256
        clutterRemoval -1 0
        aoaFovCfg -1 -90 90 -90 90
        cfarFovCfg -1 0 0 0
        cfarFovCfg -1 1 0 0
        measureRangeBiasAndRxChanPhase 0 1.5 0.2
        extendedMaxVelocity -1 0
        CQRxSatMonitor 0 3 5 121 0
        CQSigImgMonitor 0 127 4
        analogMonitor 0 0
        calibData 0 0 0
        """
        self.send(commands)
        log.info("Radar configured.")

    def start(self) -> None:
        """Start chirping."""
        self.send("sensorStart")
        log.info("Radar started.")

    def stop(self) -> None:
        """Stop chirping (may be ignored if the frame timing is very tight)."""
        self.send("sensorStop")
        log.info("Radar stopped.")

    def close(self) -> None:
        """Close the serial port."""
        try:
            self.serial.close()
        except Exception:  # noqa: BLE001 - best-effort teardown
            pass


# ---------------------------------------------------------------------------
# 3. DCA1000EVM capture card: control channel + raw UDP frame assembly
# ---------------------------------------------------------------------------


class CaptureError(Exception):
    """The capture card returned a non-zero status."""


class DCA1000EVM:
    """DCA1000EVM control (UDP :4096) and raw data reception (UDP :4098).

    Control protocol (little endian): `A55A | cmd | len | payload | EEAA`.
    Data packets: 4-byte sequence number, 6-byte running byte count, then up
    to 1456 bytes of payload. The byte count is what lets us detect and
    zero-fill dropped packets without losing frame alignment.
    """

    HEADER, FOOTER = 0xA55A, 0xEEAA
    CMD_RESET_AR_DEV = 0x02
    CMD_CONFIG_FPGA = 0x03
    CMD_START_RECORD = 0x05
    CMD_STOP_RECORD = 0x06
    CMD_SYSTEM_ALIVENESS = 0x09
    CMD_CONFIG_RECORD = 0x0B
    CMD_READ_FPGA_VERSION = 0x0E
    MAX_PACKET = 2048

    def __init__(self, cfg: CaptureConfig):
        self.cfg = cfg
        self.control = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.control.bind((cfg.sys_ip, cfg.config_port))
        self.control.settimeout(cfg.timeout)

        self.data = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.data.setsockopt(
            socket.SOL_SOCKET, socket.SO_RCVBUF, cfg.socket_buffer)
        self.data.bind((cfg.sys_ip, cfg.data_port))
        self.data.settimeout(cfg.timeout)

        actual = self.data.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
        log.info(
            "DCA1000EVM sockets bound on %s (recv buffer %d KiB)",
            cfg.sys_ip, actual // 1024)

    # -- control channel ---------------------------------------------------

    def _request(self, cmd: int, payload: bytes = b"", desc: str = "") -> int:
        packet = struct.pack(
            f"<HHH{len(payload)}sH",
            self.HEADER, cmd, len(payload), payload, self.FOOTER)
        self.control.sendto(packet, (self.cfg.fpga_ip, self.cfg.config_port))
        raw, _ = self.control.recvfrom(self.MAX_PACKET)
        header, _code, status, footer = struct.unpack_from("<HHHH", raw)
        if header != self.HEADER or footer != self.FOOTER:
            raise CaptureError(f"Malformed response to {desc or hex(cmd)}")
        if desc and status != 0 and cmd != self.CMD_READ_FPGA_VERSION:
            raise CaptureError(f"{desc} failed (status={status})")
        return status

    def setup(self) -> None:
        """Ping, read the FPGA version, and configure record + FPGA modes."""
        self._request(self.CMD_SYSTEM_ALIVENESS, desc="aliveness check")

        version = self._request(self.CMD_READ_FPGA_VERSION)
        log.info(
            "FPGA version %d.%d (%s mode)", version & 0x7F,
            (version >> 7) & 0x7F,
            "playback" if version & 0x4000 else "record")

        # Packet delay is programmed in units of the 8 ns FPGA clock, scaled
        # by 1000; 5 us is the minimum and gives the highest throughput.
        delay = int(self.cfg.delay * 1000 / 8)
        self._request(
            self.CMD_CONFIG_RECORD, struct.pack("<HHH", 1470, delay, 0),
            desc="configure record")

        # raw mode | 2 LVDS lanes | capture | ethernet stream | 16 bit | timer
        self._request(
            self.CMD_CONFIG_FPGA, struct.pack("<BBBBBB", 1, 2, 1, 2, 3, 30),
            desc="configure FPGA")

        # The FPGA ignores requests for a moment after being configured.
        for _ in range(30):
            try:
                self._request(self.CMD_SYSTEM_ALIVENESS)
                break
            except (TimeoutError, socket.timeout):
                continue
        else:
            raise CaptureError("FPGA stopped responding after configuration.")
        log.info("Capture card configured.")

    def start(self) -> None:
        """Begin streaming raw ADC data."""
        self._request(self.CMD_START_RECORD, desc="start record")

    def stop(self) -> None:
        """Stop streaming; safe to call when already stopped."""
        try:
            self._request(self.CMD_STOP_RECORD, desc="stop record")
        except (CaptureError, TimeoutError, socket.timeout) as exc:
            log.debug("stop record: %s", exc)

    def reset_radar(self) -> None:
        """Reboot the radar via the capture card's reset line."""
        self._request(self.CMD_RESET_AR_DEV, desc="reset radar")

    def flush(self) -> None:
        """Drain anything left in the data socket from a previous run."""
        self.data.settimeout(0.0)
        discarded = 0
        try:
            while discarded < 1_000_000:      # bounded: never wedge startup
                if not self.data.recv(self.MAX_PACKET):
                    break
                discarded += 1
        except (BlockingIOError, socket.timeout, TimeoutError):
            pass
        if discarded:
            log.debug("Flushed %d stale packets.", discarded)
        self.data.settimeout(self.cfg.timeout)

    def close(self) -> None:
        """Close both sockets."""
        for sock in (self.control, self.data):
            try:
                sock.close()
            except Exception:  # noqa: BLE001 - best-effort teardown
                pass


class FrameReceiver(threading.Thread):
    """Reassembles fixed-size radar frames from the DCA1000EVM UDP stream.

    Runs in its own thread and hands each completed frame to `on_frame`
    immediately, so a slow consumer never stalls packet reception (the
    consumer is responsible for dropping frames it cannot keep up with).

    Args:
        sock: bound data socket.
        frame_size: bytes per radar frame.
        on_frame: called as `on_frame(data, timestamp, dropped_bytes)`.
        timeout: seconds of silence after which the stream is considered over.
    """

    def __init__(
        self, sock: socket.socket, frame_size: int,
        on_frame: Callable[[bytes, float, int], None], timeout: float = 1.0,
    ):
        super().__init__(daemon=True, name="FrameReceiver")
        self.sock = sock
        self.frame_size = frame_size
        self.on_frame = on_frame
        self.timeout = timeout
        self._stop = threading.Event()
        self._scratch = bytearray(DCA1000EVM.MAX_PACKET)
        self.packets = 0
        self.dropped_bytes = 0
        self.out_of_order = 0

    def stop(self) -> None:
        """Ask the thread to exit after the current recv."""
        self._stop.set()

    def run(self) -> None:  # noqa: D102 - threading.Thread
        view = memoryview(self._scratch)
        size = self.frame_size
        buf = bytearray()
        offset = 0          # global byte index of the next expected byte
        aligned = False
        dropped = 0
        timestamp = 0.0

        while not self._stop.is_set():
            try:
                n = self.sock.recv_into(view)
            except (socket.timeout, TimeoutError):
                log.info("Data stream idle for %.1fs; receiver exiting.",
                         self.timeout)
                break
            except OSError:
                break
            if n < 10:
                continue
            self.packets += 1

            count = int.from_bytes(self._scratch[4:10], "little")
            payload = bytes(view[10:n])

            if not aligned:
                # Snap to a frame boundary using the card's global byte count.
                offset = count - (count % size)
                aligned = True
                timestamp = time.time()

            gap = count - offset
            if gap < 0:
                self.out_of_order += 1
                if self.out_of_order <= 5:
                    log.warning("Out-of-order packet (%d bytes early).", -gap)
                continue
            if gap > 0:
                buf.extend(b"\x00" * gap)
                offset = count
                dropped += gap
                self.dropped_bytes += gap

            buf.extend(payload)
            offset += len(payload)

            while len(buf) >= size:
                self.on_frame(bytes(buf[:size]), timestamp, dropped)
                del buf[:size]
                dropped = 0
                timestamp = time.time()


# ---------------------------------------------------------------------------
# 4. Radar signal processing
# ---------------------------------------------------------------------------
#
# Axis conventions used everywhere below:
#
#   raw    (doppler, tx, rx, 2 * range)   int16, IIQQ interleaved
#   cube   (doppler, tx, rx, range)       complex64, after range+doppler FFT
#   virtual array: elevation = rx (4 elements), azimuth = tx (3 elements),
#   both on a lambda/2 grid, in "image order" (increasing index = down/right):
#
#       TX1-RX1  TX2-RX1  TX3-RX1     ^
#       TX1-RX2  TX2-RX2  TX3-RX2     | up
#       TX1-RX3  TX2-RX3  TX3-RX3
#       TX1-RX4  TX2-RX4  TX3-RX4
#
# The AOP therefore has a *3-element* azimuth aperture: azimuth resolution is
# intrinsically coarse (~30 deg 3 dB beamwidth) no matter how much the angle
# FFT is zero-padded. Zero-padding only interpolates the beam pattern.


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
    """

    def __init__(
        self, cfg: RadarConfig, azimuth_bins: int = 64,
        elevation_bins: int = 32, range_window: bool = True,
        doppler_window: bool = True, tdm_compensation: bool = True,
        doppler_sign: int = 1, azimuth_sign: int = 1,
        elevation_sign: int = -1, cfar: "CFAR | None" = None,
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

        # Azimuth beamformer uses the TX axis, elevation the RX axis.
        self.az_steer = steering_matrix(cfg.num_tx, azimuth_bins)
        self.el_steer = steering_matrix(cfg.num_rx, elevation_bins)

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

    def range_azimuth_power(self, cube: np.ndarray) -> np.ndarray:
        """(range, azimuth) power, summed over Doppler and elevation.

        Computed through the 3x3 spatial covariance of the TX axis rather than
        by beamforming the whole cube. The two are algebraically identical --

            sum_d sum_el |sum_t A[a,t] X[d,el,t,r]|^2
                = sum_{t,u} A[a,t] conj(A[a,u]) R[r,t,u],
            R[r,t,u] = sum_{d,el} X[d,el,t,r] conj(X[d,el,u,r])

        -- but the covariance form costs ~20x less and never materializes the
        (doppler, elevation, azimuth, range) cube. `--selftest` checks it.
        """
        # (doppler, tx, rx, range) -> (range, tx, doppler * rx)
        x = np.transpose(cube, (3, 1, 0, 2)).reshape(
            self.n_range, self.cfg.num_tx, -1)
        cov = np.matmul(x, x.conj().transpose(0, 2, 1))     # (range, tx, tx)
        tmp = np.einsum("at,rtu->rau", self.az_steer, cov, optimize=True)
        power = np.einsum(
            "rau,au->ra", tmp, self.az_steer.conj(), optimize=True).real
        return power.astype(np.float32)

    def angles_at(
        self, cube: np.ndarray, range_bins: np.ndarray,
        doppler_bins: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        """Estimate (azimuth bin, elevation bin) at the given detection cells.

        The full 4D angle cube is never needed: we only beamform the 3x4
        aperture of the cells that actually passed CFAR, then take the peak of
        the 2D angle spectrum.
        """
        if range_bins.size == 0:
            empty = np.zeros(0, dtype=np.int64)
            return empty, empty

        # (K, tx, rx) -> azimuth beamform -> (K, azimuth, rx)
        snapshot = cube[doppler_bins, :, :, range_bins]
        az = np.einsum(
            "at,ktr->kar", self.az_steer, snapshot, optimize=True)
        # -> elevation beamform -> (K, azimuth, elevation)
        spectrum = np.einsum(
            "kar,er->kae", az, self.el_steer, optimize=True)
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

        rd = self.range_doppler_power(cube)
        ra = self.range_azimuth_power(cube)
        mask, snr = self.cfar(rd)

        r_bins, d_bins = np.nonzero(mask)
        if r_bins.size > max_detections:
            order = np.argsort(snr[r_bins, d_bins])[::-1][:max_detections]
            r_bins, d_bins = r_bins[order], d_bins[order]
            mask = np.zeros_like(mask)
            mask[r_bins, d_bins] = True

        az_bins, el_bins = self.angles_at(cube, r_bins, d_bins)

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


# ---------------------------------------------------------------------------
# 5. CFAR
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# 6. Recording
# ---------------------------------------------------------------------------


def _to_db(power: np.ndarray, floor: float = 1e-12) -> np.ndarray:
    """Power (not amplitude) to dB, with a floor to keep log10 finite."""
    return (10.0 * np.log10(np.maximum(power, floor))).astype(np.float32)


class Recorder:
    """Snapshot ring buffer + continuous raw recorder, both off the hot path.

    The space-bar snapshot keeps a rolling window of the last few processed
    frames; when triggered it grabs those, waits for `after` more frames, then
    hands the whole batch to a writer thread. Several snapshots may be in
    flight at once (holding space down just queues more of them).

    Args:
        outdir: directory that receives `snap_*/` and `rec_*/` folders.
        before: frames kept before the trigger.
        after: frames collected after the trigger.
        save_raw: also store the int16 IIQQ frames (768 KiB each here).
        save_preview: render a PNG contact sheet next to each snapshot.
    """

    def __init__(
        self, outdir: str, radar: RadarConfig, pipeline: Pipeline,
        before: int = 2, after: int = 2, save_raw: bool = True,
        save_preview: bool = True,
    ):
        self.outdir = outdir
        self.radar = radar
        self.pipeline = pipeline
        self.before = before
        self.after = after
        self.save_raw = save_raw
        self.save_preview = save_preview

        os.makedirs(outdir, exist_ok=True)
        self.history: deque[Products] = deque(maxlen=before + 1)
        self._pending: list[dict[str, Any]] = []
        self._jobs: queue.Queue = queue.Queue()
        self._writer = threading.Thread(
            target=self._writer_loop, daemon=True, name="SnapshotWriter")
        self._writer.start()

        self.snapshots = 0
        self.recording: dict[str, Any] | None = None
        self.frames_recorded = 0

    # -- snapshots ---------------------------------------------------------

    def observe(self, product: Products) -> None:
        """Feed every processed frame in; drives both capture mechanisms."""
        self.history.append(product)

        for job in list(self._pending):
            job["frames"].append(product)
            job["remaining"] -= 1
            if job["remaining"] <= 0:
                self._pending.remove(job)
                self._jobs.put(job)

        if self.recording is not None:
            self.recording["file"].write(np.ascontiguousarray(product.raw))
            self.recording["timestamps"].append(product.timestamp)
            self.recording["indices"].append(product.index)
            self.frames_recorded += 1

    def trigger_snapshot(self) -> int:
        """Arm a snapshot around the current frame. Returns frames pending."""
        if not self.history:
            log.warning("No frames yet; snapshot ignored.")
            return 0
        self.snapshots += 1
        job = {
            "name": f"snap_{time.strftime('%Y%m%d_%H%M%S')}_"
                    f"{self.snapshots:03d}",
            "frames": list(self.history),
            "trigger_index": len(self.history) - 1,
            "remaining": self.after,
        }
        self._pending.append(job)
        log.info(
            "Snapshot armed: %d frame(s) buffered, %d to go -> %s",
            len(job["frames"]), self.after, job["name"])
        return self.after

    @property
    def pending(self) -> int:
        """Number of snapshots still collecting trailing frames."""
        return len(self._pending)

    def _writer_loop(self) -> None:
        while True:
            job = self._jobs.get()
            if job is None:
                return
            try:
                self._write_snapshot(job)
            except Exception:  # noqa: BLE001 - never kill the writer
                log.exception("Failed to write snapshot %s", job["name"])

    def _write_snapshot(self, job: dict[str, Any]) -> None:
        frames: list[Products] = job["frames"]
        path = os.path.join(self.outdir, job["name"])
        os.makedirs(path, exist_ok=True)
        pipe = self.pipeline

        indices = np.array([f.index for f in frames], dtype=np.int64)
        contiguous = bool(np.all(np.diff(indices) == 1))
        if not contiguous:
            log.warning(
                "Snapshot %s spans non-consecutive frames %s (the consumer "
                "fell behind).", job["name"], indices.tolist())

        detections = np.concatenate(
            [np.column_stack([np.full(len(f.detections), i, np.float32),
                              f.detections])
             for i, f in enumerate(frames) if len(f.detections)]
            or [np.zeros((0, len(DETECTION_COLUMNS) + 1), np.float32)])

        arrays: dict[str, np.ndarray] = {
            "range_doppler_db": np.stack(
                [_to_db(f.range_doppler) for f in frames]),
            "range_azimuth_db": np.stack(
                [_to_db(f.range_azimuth) for f in frames]),
            "cfar_mask": np.stack([f.cfar_mask for f in frames]),
            "cfar_snr_db": np.stack([_to_db(f.cfar_snr) for f in frames]),
            "detections": detections,
            "frame_index": indices,
            "timestamp": np.array([f.timestamp for f in frames]),
            "dropped_bytes": np.array(
                [f.dropped_bytes for f in frames], dtype=np.int64),
            "range_axis_m": pipe.range_axis.astype(np.float32),
            "velocity_axis_mps": pipe.velocity_axis.astype(np.float32),
            "azimuth_axis_deg": np.degrees(pipe.azimuth_axis).astype(
                np.float32),
            "elevation_axis_deg": np.degrees(pipe.elevation_axis).astype(
                np.float32),
        }
        if self.save_raw:
            arrays["iq_raw_iiqq"] = np.stack([f.raw for f in frames])

        np.savez_compressed(os.path.join(path, "frames.npz"), **arrays)

        meta = {
            "created": time.strftime("%Y-%m-%d %H:%M:%S"),
            "frames": len(frames),
            "trigger_index": job["trigger_index"],
            "frames_before": job["trigger_index"],
            "frames_after": len(frames) - job["trigger_index"] - 1,
            "frames_consecutive": contiguous,
            "frame_index": indices.tolist(),
            "detection_columns": ["frame"] + DETECTION_COLUMNS,
            "coordinate_frame":
                "x = right, y = forward (boresight), z = up; metres",
            "radar_config": {
                k: getattr(self.radar, k)
                for k in self.radar.__dataclass_fields__},
            "derived": {
                "range_resolution_m": self.radar.range_resolution,
                "max_range_m": self.radar.max_range,
                "doppler_resolution_mps": self.radar.doppler_resolution,
                "max_doppler_mps": self.radar.max_doppler,
                "bandwidth_mhz": self.radar.bandwidth,
                "center_frequency_ghz": self.radar.center_frequency,
                "wavelength_m": self.radar.wavelength,
            },
            "processing": {
                "azimuth_bins": pipe.n_azimuth,
                "elevation_bins": pipe.n_elevation,
                "tdm_compensation": pipe.tdm_compensation,
                "doppler_sign": pipe.doppler_sign,
                "clutter_removal": pipe.clutter_removal,
                "cfar": {
                    "guard": [pipe.cfar.guard_r, pipe.cfar.guard_d],
                    "train": [pipe.cfar.train_r, pipe.cfar.train_d],
                    "pfa": pipe.cfar.pfa,
                    "snr_db": pipe.cfar.snr_db,
                    "min_range_bin": pipe.cfar.min_range_bin,
                    "zero_doppler_guard": pipe.cfar.zero_doppler_guard,
                    "peak_grouping": pipe.cfar.group_peaks,
                    "noise_floor_fraction": pipe.cfar.noise_floor_fraction,
                },
            },
            "raw_layout": {
                "included": self.save_raw,
                "shape": list(self.radar.raw_shape),
                "dtype": "int16",
                "order": "IIQQ interleaved; see iq_from_iiqq()",
            },
        }
        with open(os.path.join(path, "meta.json"), "w") as f:
            json.dump(meta, f, indent=2)

        if self.save_preview:
            self._write_preview(os.path.join(path, "preview.png"), frames, job)

        log.info("Saved %d frames -> %s", len(frames), path)

    def _write_preview(
        self, path: str, frames: list[Products], job: dict[str, Any]
    ) -> None:
        """Render a contact sheet (rows = frames, cols = the three products)."""
        from matplotlib.figure import Figure

        pipe = self.pipeline
        n = len(frames)
        fig = Figure(figsize=(11, 2.6 * n), dpi=110)
        rd_extent = [pipe.velocity_axis[0], pipe.velocity_axis[-1],
                     pipe.range_axis[0], pipe.range_axis[-1]]

        for row, frame in enumerate(frames):
            tag = " <- trigger" if row == job["trigger_index"] else ""
            rd = _to_db(frame.range_doppler)
            ra = _to_db(frame.range_azimuth)

            ax = fig.add_subplot(n, 3, 3 * row + 1)
            ax.imshow(rd, origin="lower", aspect="auto", cmap="viridis",
                      extent=rd_extent, vmax=rd.max(), vmin=rd.max() - 40)
            ax.set_ylabel(f"#{frame.index}{tag}\nrange (m)", fontsize=8)
            if row == 0:
                ax.set_title("range-Doppler (dB)", fontsize=9)
            if row == n - 1:
                ax.set_xlabel("velocity (m/s)", fontsize=8)

            ax = fig.add_subplot(n, 3, 3 * row + 2)
            ax.imshow(ra, origin="lower", aspect="auto", cmap="viridis",
                      extent=[0, pipe.n_azimuth, pipe.range_axis[0],
                              pipe.range_axis[-1]],
                      vmax=ra.max(), vmin=ra.max() - 40)
            _label_angle_axis(ax, pipe.azimuth_axis)
            if row == 0:
                ax.set_title("range-azimuth (dB)", fontsize=9)
            if row == n - 1:
                ax.set_xlabel("azimuth (deg)", fontsize=8)

            ax = fig.add_subplot(n, 3, 3 * row + 3)
            ax.imshow(rd, origin="lower", aspect="auto", cmap="gray",
                      extent=rd_extent, vmax=rd.max(), vmin=rd.max() - 40)
            if len(frame.detections):
                ax.scatter(
                    frame.detections[:, DETECTION_COLUMNS.index(
                        "velocity_mps")],
                    frame.detections[:, DETECTION_COLUMNS.index("range_m")],
                    s=14, facecolors="none", edgecolors="#ff3b3b",
                    linewidths=0.9)
            if row == 0:
                ax.set_title("CFAR detections", fontsize=9)
            if row == n - 1:
                ax.set_xlabel("velocity (m/s)", fontsize=8)
            ax.text(0.02, 0.95, f"{len(frame.detections)} pts",
                    transform=ax.transAxes, va="top", fontsize=8,
                    color="#ff3b3b")

        fig.tight_layout()
        fig.savefig(path)

    # -- continuous recording ---------------------------------------------

    def toggle_recording(self) -> bool:
        """Start or stop continuous raw recording. Returns the new state."""
        if self.recording is None:
            name = f"rec_{time.strftime('%Y%m%d_%H%M%S')}"
            path = os.path.join(self.outdir, name)
            os.makedirs(path, exist_ok=True)
            self.recording = {
                "path": path,
                "file": open(os.path.join(path, "raw.bin"), "wb"),
                "timestamps": [],
                "indices": [],
                "started": time.time(),
            }
            self.frames_recorded = 0
            log.info("Recording -> %s", path)
            return True

        rec = self.recording
        self.recording = None
        rec["file"].close()
        np.save(
            os.path.join(rec["path"], "timestamps.npy"),
            np.array(rec["timestamps"]))
        np.save(
            os.path.join(rec["path"], "frame_index.npy"),
            np.array(rec["indices"], dtype=np.int64))
        with open(os.path.join(rec["path"], "meta.json"), "w") as f:
            json.dump({
                "frames": len(rec["timestamps"]),
                "duration_s": time.time() - rec["started"],
                "raw_shape_per_frame": list(self.radar.raw_shape),
                "dtype": "int16",
                "order": "IIQQ interleaved; see iq_from_iiqq()",
                "radar_config": {
                    k: getattr(self.radar, k)
                    for k in self.radar.__dataclass_fields__},
            }, f, indent=2)
        log.info(
            "Recording stopped: %d frames -> %s",
            len(rec["timestamps"]), rec["path"])
        return False

    def close(self, timeout: float = 120.0) -> None:
        """Flush any in-flight snapshot and close an open recording.

        Snapshots still waiting for trailing frames are written with whatever
        they have; the writer thread is then drained via a sentinel so nothing
        is lost when the process exits.
        """
        if self.recording is not None:
            self.toggle_recording()
        for job in self._pending:
            if job["frames"]:
                log.warning(
                    "Snapshot %s only got %d frame(s) before shutdown.",
                    job["name"], len(job["frames"]))
                self._jobs.put(job)
        self._pending.clear()

        self._jobs.put(None)
        self._writer.join(timeout=timeout)
        if self._writer.is_alive():
            log.error("Snapshot writer did not finish within %.0fs.", timeout)


def _label_angle_axis(ax, angles: np.ndarray, ticks=(-60, -30, 0, 30, 60)):
    """Put degree labels on an axis whose bins are uniform in sin(theta)."""
    n = len(angles)
    spacing = 0.5
    sign = 1.0 if angles[-1] >= angles[0] else -1.0
    positions, labels = [], []
    for deg in ticks:
        pos = n // 2 + sign * np.sin(np.radians(deg)) * n * spacing
        if 0 <= pos <= n:
            positions.append(pos)
            labels.append(f"{deg:g}")
    ax.set_xticks(positions)
    ax.set_xticklabels(labels, fontsize=8)


# ---------------------------------------------------------------------------
# 7. Live display
# ---------------------------------------------------------------------------


class Display:
    """Four-panel live matplotlib view with keyboard control.

    Args:
        pipeline: supplies the physical axes.
        dynamic_range: dB below each frame's peak that maps to the low end of
            the colormap.
    """

    HELP = "space: 5-frame snapshot   t: record   m: clutter   q: quit"

    def __init__(self, pipeline: Pipeline, dynamic_range: float = 40.0):
        import matplotlib.pyplot as plt

        self.plt = plt
        self.pipeline = pipeline
        self.dynamic_range = dynamic_range
        self.closed = False
        self.key_queue: queue.Queue[str] = queue.Queue()

        # Free up the keys we want; matplotlib grabs some by default.
        for param in ("keymap.save", "keymap.home", "keymap.yscale"):
            plt.rcParams[param] = [
                k for k in plt.rcParams[param] if k not in ("s", "r", "l")]

        plt.ion()
        self.fig, axes = plt.subplots(2, 2, figsize=(13, 8.5))
        self.fig.canvas.manager.set_window_title(  # type: ignore[union-attr]
            "AWR1843AOP live")
        (ax_rd, ax_ra), (ax_cfar, ax_pc) = axes

        r0, r1 = pipeline.range_axis[0], pipeline.range_axis[-1]
        v0, v1 = pipeline.velocity_axis[0], pipeline.velocity_axis[-1]
        rd_extent = [v0, v1, r0, r1]
        blank_rd = np.zeros(
            (pipeline.n_range, pipeline.n_doppler), dtype=np.float32)
        blank_ra = np.zeros(
            (pipeline.n_range, pipeline.n_azimuth), dtype=np.float32)

        self.im_rd = ax_rd.imshow(
            blank_rd, origin="lower", aspect="auto", cmap="viridis",
            extent=rd_extent)
        ax_rd.set_title("range-Doppler (dB)")
        ax_rd.set_xlabel("velocity (m/s)")
        ax_rd.set_ylabel("range (m)")

        self.im_ra = ax_ra.imshow(
            blank_ra, origin="lower", aspect="auto", cmap="viridis",
            extent=[0, pipeline.n_azimuth, r0, r1])
        ax_ra.set_title("range-azimuth (dB)")
        ax_ra.set_xlabel("azimuth (deg)")
        ax_ra.set_ylabel("range (m)")
        _label_angle_axis(ax_ra, pipeline.azimuth_axis)

        self.im_cfar = ax_cfar.imshow(
            blank_rd, origin="lower", aspect="auto", cmap="gray",
            extent=rd_extent)
        self.sc_cfar, = ax_cfar.plot(
            [], [], linestyle="none", marker="o", markersize=6,
            markerfacecolor="none", markeredgecolor="#ff3b3b",
            markeredgewidth=1.1)
        ax_cfar.set_title("CA-CFAR detections")
        ax_cfar.set_xlabel("velocity (m/s)")
        ax_cfar.set_ylabel("range (m)")

        vmax = max(abs(v0), abs(v1))
        self.sc_pc = ax_pc.scatter(
            [], [], c=[], s=26, cmap="coolwarm", vmin=-vmax, vmax=vmax)
        ax_pc.set_xlim(-r1, r1)
        ax_pc.set_ylim(0, r1)
        ax_pc.set_aspect("equal")
        ax_pc.grid(alpha=0.25)
        ax_pc.set_title("point cloud (bird's eye)")
        ax_pc.set_xlabel("x: right (m)")
        ax_pc.set_ylabel("y: forward (m)")
        self.fig.colorbar(self.sc_pc, ax=ax_pc, label="velocity (m/s)")

        self.status = self.fig.suptitle("starting...", fontsize=11)
        self.fig.tight_layout(rect=(0, 0, 1, 0.95))

        self.fig.canvas.mpl_connect("key_press_event", self._on_key)
        self.fig.canvas.mpl_connect("close_event", self._on_close)

    def _on_key(self, event) -> None:
        if event.key:
            self.key_queue.put(event.key)

    def _on_close(self, _event) -> None:
        self.closed = True

    def poll_keys(self) -> list[str]:
        """Drain and return the keys pressed since the last call."""
        keys = []
        while True:
            try:
                keys.append(self.key_queue.get_nowait())
            except queue.Empty:
                return keys

    def update(self, product: Products, status: str) -> None:
        """Redraw all four panels from one frame's products."""
        rd = _to_db(product.range_doppler)
        ra = _to_db(product.range_azimuth)

        self.im_rd.set_data(rd)
        self.im_rd.set_clim(rd.max() - self.dynamic_range, rd.max())
        self.im_ra.set_data(ra)
        self.im_ra.set_clim(ra.max() - self.dynamic_range, ra.max())
        self.im_cfar.set_data(rd)
        self.im_cfar.set_clim(rd.max() - self.dynamic_range, rd.max())

        det = product.detections
        if len(det):
            col = DETECTION_COLUMNS.index
            self.sc_cfar.set_data(
                det[:, col("velocity_mps")], det[:, col("range_m")])
            self.sc_pc.set_offsets(
                np.column_stack([det[:, col("x_right_m")],
                                 det[:, col("y_forward_m")]]))
            self.sc_pc.set_array(det[:, col("velocity_mps")])
        else:
            self.sc_cfar.set_data([], [])
            self.sc_pc.set_offsets(np.zeros((0, 2)))
            self.sc_pc.set_array(np.zeros(0))

        self.status.set_text(f"{status}\n{self.HELP}")
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

    def pump(self) -> None:
        """Service GUI events without redrawing data."""
        self.fig.canvas.flush_events()

    def close(self) -> None:
        """Tear down the figure."""
        try:
            self.plt.close(self.fig)
        except Exception:  # noqa: BLE001 - best-effort teardown
            pass


# ---------------------------------------------------------------------------
# 8. Frame sources
# ---------------------------------------------------------------------------


@dataclass
class RawFrame:
    """One raw frame handed from a source to the main loop."""

    index: int
    timestamp: float
    dropped_bytes: int
    data: np.ndarray


class HardwareSource:
    """Live AWR1843AOPEVM + DCA1000EVM capture.

    Startup order matters: the capture card must be recording *before* the
    radar starts chirping, otherwise the running byte count used for frame
    alignment is offset.
    """

    def __init__(
        self, radar_cfg: RadarConfig, capture_cfg: CaptureConfig,
        queue_size: int = 32,
    ):
        self.radar_cfg = radar_cfg
        self.queue: queue.Queue[RawFrame] = queue.Queue(maxsize=queue_size)
        self.received = 0
        self.dropped_frames = 0

        self.dca = DCA1000EVM(capture_cfg)
        self.dca.setup()
        self.radar = AWR1843AOP(port=radar_cfg.port)
        self.receiver: FrameReceiver | None = None

    def start(self) -> None:
        """Reset, arm the capture card, configure and start the radar.

        The receiver thread is started *last*: pushing ~30 CLI commands over a
        115200 baud UART takes seconds, and the receiver treats a second of
        silence as end-of-stream. Nothing is missed by waiting, because no
        data exists until `sensorStart` returns.
        """
        self.dca.stop()
        self.dca.reset_radar()
        self.dca.flush()
        self.dca.start()

        self.radar.configure(self.radar_cfg)
        self.radar.start()

        self.receiver = FrameReceiver(
            self.dca.data, self.radar_cfg.frame_size, self._on_frame,
            timeout=self.dca.cfg.timeout)
        self.receiver.start()

    def _on_frame(self, data: bytes, timestamp: float, dropped: int) -> None:
        array = np.frombuffer(data, dtype=np.int16).reshape(
            self.radar_cfg.raw_shape)
        frame = RawFrame(self.received, timestamp, dropped, array)
        self.received += 1
        try:
            self.queue.put_nowait(frame)
        except queue.Full:
            try:                     # make room by discarding the oldest
                self.queue.get_nowait()
                self.dropped_frames += 1
            except queue.Empty:
                pass
            try:
                self.queue.put_nowait(frame)
            except queue.Full:
                self.dropped_frames += 1

    def get(self, timeout: float) -> RawFrame | None:
        """Block for the next frame, or None on timeout."""
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def backlog(self) -> int:
        """Frames waiting to be processed."""
        return self.queue.qsize()

    def stop(self) -> None:
        """Stop the radar and the capture card; safe to call twice."""
        log.info("Shutting down radar and capture card...")
        if self.receiver is not None:
            self.receiver.stop()
        try:
            self.dca.stop()
            self.dca.reset_radar()
        except Exception as exc:  # noqa: BLE001 - always finish teardown
            log.error("Capture card shutdown: %s", exc)
        try:
            self.radar.close()
        finally:
            self.dca.close()


class SimulatedSource:
    """Synthesizes IIQQ frames with point targets; no hardware required.

    Targets are injected using exactly the phase model the pipeline inverts,
    so this validates the pipeline's internal consistency (bin indexing, TDM
    compensation, array geometry) -- it cannot validate hardware-dependent
    sign conventions.

    Args:
        cfg: radar configuration.
        targets: `(range_m, velocity_mps, azimuth_deg, elevation_deg,
            amplitude)` tuples.
        noise: standard deviation of the additive complex noise, in LSB.
        realtime: sleep to emulate the true frame period.
    """

    def __init__(
        self, cfg: RadarConfig,
        targets: list[tuple[float, float, float, float, float]] | None = None,
        noise: float = 60.0, realtime: bool = True, seed: int = 0,
    ):
        self.cfg = cfg
        self.noise = noise
        self.realtime = realtime
        self.rng = np.random.default_rng(seed)
        self.received = 0
        self.dropped_frames = 0
        self._next = time.time()
        self.targets = targets if targets is not None else [
            (1.2, 0.0, -25.0, 0.0, 1400.0),
            (2.4, 0.35, 10.0, 5.0, 1100.0),
            (3.6, -0.5, 30.0, -5.0, 900.0),
        ]

    def start(self) -> None:
        """No-op; present so both sources share an interface."""

    def _synthesize(self) -> np.ndarray:
        cfg = self.cfg
        n_d, n_tx, n_rx, n_s = cfg.cube_shape
        iq = np.zeros((n_d, n_tx, n_rx, n_s), dtype=np.complex64)

        d = np.arange(n_d)[:, None, None, None]
        tx = np.arange(n_tx)[None, :, None, None]
        rx = np.arange(n_rx)[None, None, :, None]
        s = np.arange(n_s)[None, None, None, :]
        drift = self.received * cfg.frame_period / 1000.0

        for rng_m, vel, az_deg, el_deg, amp in self.targets:
            rng_bin = (rng_m + vel * drift) / cfg.range_resolution
            dop_bin = vel / cfg.doppler_resolution
            sin_az = np.sin(np.radians(az_deg))
            # Elevation rows run downward (image order), hence the sign flip.
            sin_el = -np.sin(np.radians(el_deg))

            phase = (
                2j * np.pi * (
                    rng_bin * s / n_s
                    + dop_bin * (d + tx / n_tx) / n_d
                    + 0.5 * tx * sin_az
                    + 0.5 * rx * sin_el))
            iq += (amp * np.exp(phase)).astype(np.complex64)

        if self.noise > 0:
            iq += (self.rng.normal(0, self.noise, iq.shape)
                   + 1j * self.rng.normal(0, self.noise, iq.shape))
        return iiqq_from_iq(np.clip(iq.view(np.float32), -32768, 32767)
                            .view(np.complex64))

    def get(self, timeout: float) -> RawFrame | None:
        """Produce the next synthetic frame (optionally paced in real time)."""
        if self.realtime:
            delay = self._next - time.time()
            if delay > 0:
                time.sleep(min(delay, timeout))
            self._next += self.cfg.frame_period / 1000.0
        frame = RawFrame(self.received, time.time(), 0, self._synthesize())
        self.received += 1
        return frame

    def backlog(self) -> int:
        """Always zero; the simulator is generated on demand."""
        return 0

    def stop(self) -> None:
        """No-op."""


# ---------------------------------------------------------------------------
# 9. Self-test
# ---------------------------------------------------------------------------


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

    # 3. Covariance range-azimuth == direct beamforming.
    cfg = RadarConfig(adc_samples=32, frame_length=16)
    pipe = Pipeline(cfg, azimuth_bins=32, elevation_bins=16)
    cube = (rng.normal(size=cfg.cube_shape)
            + 1j * rng.normal(size=cfg.cube_shape)).astype(np.complex64)
    fast = pipe.range_azimuth_power(cube)
    beam = np.einsum("at,dtrn->darn", pipe.az_steer, cube, optimize=True)
    slow = (np.abs(beam) ** 2).sum(axis=(0, 2)).T
    rel = np.abs(fast - slow).max() / slow.max()
    check("covariance range-azimuth == direct beamforming",
          rel < 1e-4, f"max rel err {rel:.2e}")

    # 4. Integral-image CFAR training sums == brute force.
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

    # 5. End-to-end: a synthetic target lands in the expected bins.
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

    # 6. Throughput.
    start = time.perf_counter()
    for _ in range(10):
        pipe.process(frame.data, 0, 0.0)
    per_frame = (time.perf_counter() - start) / 10
    check(f"pipeline keeps up with {1000 / cfg.frame_period:.0f} fps",
          per_frame < cfg.frame_period / 1000,
          f"{per_frame * 1000:.1f} ms/frame")

    print(f"\n{'all checks passed' if not failures else 'FAILED: ' + ', '.join(failures)}")
    return 1 if failures else 0


# ---------------------------------------------------------------------------
# 10. Main loop
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    """CLI definition."""
    here = os.path.dirname(os.path.abspath(__file__))
    default_config = os.path.join(here, "demo", "config_awr1843aop.yaml")

    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    g = p.add_argument_group("configuration")
    g.add_argument(
        "--config", default=default_config if os.path.exists(default_config)
        else None, help="radar/capture YAML (default: %(default)s)")
    g.add_argument("--port", default=None,
                   help="radar control serial port (default: auto-detect)")
    g.add_argument("--outdir", default="captures",
                   help="where snapshots and recordings go")
    g.add_argument("--strict", action="store_true",
                   help="refuse to start if a config constraint fails")

    g = p.add_argument_group("processing")
    g.add_argument("--azimuth-bins", type=int, default=64,
                   help="zero-padded azimuth FFT size (lab requires >= 32)")
    g.add_argument("--elevation-bins", type=int, default=32,
                   help="zero-padded elevation FFT size")
    g.add_argument("--no-range-window", action="store_true",
                   help="skip the Hann window on the range FFT")
    g.add_argument("--no-doppler-window", action="store_true",
                   help="skip the Hann window on the Doppler FFT")
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
    g.add_argument("--cfar-pfa", type=float, default=1e-3,
                   help="nominal per-cell false alarm probability")
    g.add_argument("--cfar-snr-db", type=float, default=None,
                   help="fixed dB-over-local-mean threshold (overrides --cfar-pfa)")
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
    g.add_argument("--dynamic-range", type=float, default=40.0,
                   help="dB below peak shown in the heatmaps")
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

    detector = CFAR(
        guard=tuple(args.cfar_guard), train=tuple(args.cfar_train),
        pfa=args.cfar_pfa, snr_db=args.cfar_snr_db,
        min_range_bin=args.cfar_min_range_bin,
        max_range_bin=args.cfar_max_range_bin,
        zero_doppler_guard=args.cfar_zero_doppler_guard,
        group_peaks=not args.no_peak_grouping,
        noise_floor_fraction=args.cfar_noise_floor)

    pipeline = Pipeline(
        radar_cfg,
        azimuth_bins=args.azimuth_bins, elevation_bins=args.elevation_bins,
        range_window=not args.no_range_window,
        doppler_window=not args.no_doppler_window,
        tdm_compensation=not args.no_tdm_comp,
        doppler_sign=args.doppler_sign, azimuth_sign=args.azimuth_sign,
        elevation_sign=args.elevation_sign, cfar=detector)
    pipeline.clutter_removal = args.clutter_removal

    recorder = Recorder(
        args.outdir, radar_cfg, pipeline,
        before=args.snapshot_before, after=args.snapshot_after,
        save_raw=not args.no_save_raw, save_preview=not args.no_preview)

    source: Any
    if args.simulate:
        log.warning("SIMULATION MODE: frames are synthetic, not from hardware.")
        source = SimulatedSource(radar_cfg, realtime=not args.no_display)
    else:
        source = HardwareSource(radar_cfg, capture_cfg)

    display = None
    if not args.no_display:
        display = Display(pipeline, dynamic_range=args.dynamic_range)

    if args.record:
        recorder.toggle_recording()
    snapshot_at = set(args.snapshot_at or [])

    processed = 0
    last_report = time.perf_counter()
    last_draw = 0.0
    fps_window = 0
    fps = 0.0
    idle_since: float | None = None

    def handle_keys() -> None:
        """Act on keypresses; safe to call even when no frames are arriving."""
        if display is None:
            return
        for key in display.poll_keys():
            if key == " ":
                recorder.trigger_snapshot()
            elif key == "t":
                recorder.toggle_recording()
            elif key == "m":
                pipeline.clutter_removal = not pipeline.clutter_removal
                log.info("Clutter removal %s.",
                         "on" if pipeline.clutter_removal else "off")
            elif key in ("q", "escape"):
                log.info("Quit requested.")
                display.closed = True

    try:
        source.start()
        log.info("Streaming. %s", Display.HELP)

        while True:
            if display is not None and display.closed:
                log.info("Window closed.")
                break
            if args.frames is not None and processed >= args.frames:
                log.info("Reached --frames %d.", args.frames)
                break

            frame = source.get(timeout=0.2)
            if frame is None:
                if display is not None:
                    display.pump()
                    handle_keys()
                if idle_since is None:
                    idle_since = time.perf_counter()
                elif time.perf_counter() - idle_since > 5.0:
                    log.error(
                        "No frames for 5 s. Is the radar chirping and the "
                        "capture card wired to %s?", capture_cfg.sys_ip)
                    idle_since = time.perf_counter()
                continue
            idle_since = None

            product = pipeline.process(
                frame.data, frame.index, frame.timestamp,
                dropped_bytes=frame.dropped_bytes,
                max_detections=args.max_detections)
            recorder.observe(product)
            processed += 1
            fps_window += 1

            if frame.index in snapshot_at:
                recorder.trigger_snapshot()
            handle_keys()

            now = time.perf_counter()
            if now - last_report >= 2.0:
                fps = fps_window / (now - last_report)
                fps_window = 0
                last_report = now

            backlog = source.backlog()
            if display is not None and (backlog == 0 or now - last_draw > 0.25):
                last_draw = now
                rec = ("REC %d" % recorder.frames_recorded
                       if recorder.recording else "idle")
                pending = (f"  snapshot pending ({recorder.pending})"
                           if recorder.pending else "")
                display.update(product, (
                    f"frame {frame.index}   {fps:4.1f} fps   "
                    f"{len(product.detections)} detections   "
                    f"backlog {backlog}   dropped {source.dropped_frames}   "
                    f"clutter-removal {'on' if pipeline.clutter_removal else 'off'}"
                    f"   {rec}   snapshots {recorder.snapshots}{pending}"))

    except KeyboardInterrupt:
        log.info("Interrupted.")
    finally:
        source.stop()
        recorder.close()
        if display is not None:
            display.close()

    log.info(
        "Processed %d frames; %d frames dropped before processing; "
        "%d snapshots written.",
        processed, getattr(source, "dropped_frames", 0), recorder.snapshots)
    return 0


if __name__ == "__main__":
    sys.exit(main())
