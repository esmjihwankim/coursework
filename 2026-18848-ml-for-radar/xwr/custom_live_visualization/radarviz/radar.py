"""Radar control: the mmWave demo firmware UART CLI.

The AWR1843's demo firmware exposes an ASCII command prompt over a serial
port. This module wraps that prompt: it pushes a `RadarConfig` as the command
sequence the firmware expects, then starts and stops the sensor.
"""

from __future__ import annotations

import logging
import re
import time

from .config import RadarConfig

log = logging.getLogger(__name__)


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
