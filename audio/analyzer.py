"""
Lumina Asynchronous Audio Analyzer Subprocess Module
Captures low-latency PCM audio, processes FFT spectral bands, and implements RMS noise gating.
"""

import asyncio
import shutil
import math
import time
import numpy as np
from typing import Optional

class AudioAnalyzer:
    def __init__(self):
        self.lows: float = 0.0
        self.mids: float = 0.0
        self.highs: float = 0.0
        self.running: bool = False
        self.process: Optional[asyncio.subprocess.Process] = None
        self._loop_task: Optional[asyncio.Task] = None
        self.mode: str = "input"
        self.device_id: str = "default"
        self.emulation_mode: bool = False
        self.noise_gate: float = 0.02

    def start(self, mode: str = "input", device_id: str = "default", emulation: bool = False, noise_gate: float = 0.02):
        self.running = True
        self.mode = mode
        self.device_id = device_id
        self.emulation_mode = emulation
        self.noise_gate = noise_gate
        self._loop_task = asyncio.create_task(self._audio_capture_loop())

    async def _audio_capture_loop(self):
        if self.emulation_mode:
            print("[*] Audio emulation active (Demo Mode). Bypassing capture subprocess.")
            await self._audio_emulation_loop()
            return

        cmd = None
        device = self.device_id
        
        # 1. Output/Speakers loopback capture mode
        if self.mode == "output":
            if shutil.which("pw-record"):
                # Clean up Pulse .monitor suffix for native PipeWire targets
                target = device.replace(".monitor", "") if device and device != "default" else "@DEFAULT_MONITOR@"
                # Set stream.capture.sink=true property to record from loopback
                cmd = [
                    "pw-record", 
                    "--target", target, 
                    "--properties", "{ stream.capture.sink=true }", 
                    "--format=s16", 
                    "--channels=1", 
                    "--rate=44100", 
                    "-"
                ]
            elif shutil.which("parec"):
                # parec expects PulseAudio-style monitor name
                target = device if device and device != "default" else "@DEFAULT_MONITOR@"
                cmd = ["parec", "-d", target, "--format=s16le", "--channels=1", "--rate=44100"]

        # 2. Input/Microphone capture mode
        else:
            if shutil.which("pw-record"):
                target = device.replace(".monitor", "") if device and device != "default" else "default"
                cmd = ["pw-record", "--target", target, "--format=s16", "--channels=1", "--rate=44100", "-"]
            elif shutil.which("parec"):
                target = device if device and device != "default" else "default"
                cmd = ["parec", "-d", target, "--format=s16le", "--channels=1", "--rate=44100"]
            elif shutil.which("arecord"):
                target = "default" if not device or device.startswith("alsa_") else device
                cmd = ["arecord", "-D", target, "-f", "S16_LE", "-c", "1", "-r", "44100", "-t", "raw"]

        if not cmd:
            print(f"[*] No compatible recording utilities found for mode: {self.mode}. Keeping levels silent.")
            self._reset_levels()
            return

        try:
            self.process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
            )
            print(f"[*] Audio capture pipeline active (Process: {' '.join(cmd)})")
        except Exception as e:
            print(f"[*] Failed to spawn system recording process: {e}. Keeping levels silent.")
            self._reset_levels()
            return

        chunk_size = 512
        byte_size = chunk_size * 2  # 16-bit PCM = 2 bytes per sample

        try:
            while self.running and self.process.returncode is None:
                data = await self.process.stdout.readexactly(byte_size)
                if not data:
                    break

                decoded = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                if len(decoded) == 0:
                    continue

                # Time-domain RMS Energy Noise Gate
                rms = np.sqrt(np.mean(decoded ** 2))
                if rms < self.noise_gate:
                    self._reset_levels()
                    continue

                # Correct FFT Normalization by dividing by chunk size N
                fft_data = np.abs(np.fft.rfft(decoded)) / len(decoded)

                # Calibrated Multipliers for Normalized Float Range
                self.lows = float(np.mean(fft_data[0:10]) * 90.0)
                self.mids = float(np.mean(fft_data[10:60]) * 110.0)
                self.highs = float(np.mean(fft_data[60:]) * 130.0)

                # Clamping bounds
                self.lows = min(1.0, max(0.0, self.lows))
                self.mids = min(1.0, max(0.0, self.mids))
                self.highs = min(1.0, max(0.0, self.highs))
        except asyncio.IncompleteReadError:
            pass
        except Exception as e:
            print(f"[*] Pipe capture parsing exception: {e}")
        finally:
            await self._cleanup_process()
            self._reset_levels()
            # ONLY fall back to emulation loop if user explicitly enabled it
            if self.running and self.emulation_mode:
                await self._audio_emulation_loop()

    def _reset_levels(self):
        self.lows = 0.0
        self.mids = 0.0
        self.highs = 0.0

    async def _audio_emulation_loop(self):
        while self.running:
            t = time.time()
            self.lows = (math.sin(t * 3.0) * 0.4 + 0.6) * (0.8 + 0.2 * math.cos(t * 12.0))
            self.mids = (math.sin(t * 5.0) * 0.3 + 0.5) * (0.7 + 0.3 * math.cos(t * 20.0))
            self.highs = (math.sin(t * 8.0) * 0.25 + 0.4) * (0.6 + 0.4 * math.cos(t * 35.0))
            await asyncio.sleep(0.03)

    async def _cleanup_process(self):
        if self.process:
            try:
                self.process.terminate()
                await self.process.wait()
            except Exception:
                pass
            self.process = None

    def stop(self):
        self.running = False
        if self._loop_task:
            self._loop_task.cancel()
        if self.process:
            try:
                self.process.terminate()
            except Exception:
                pass