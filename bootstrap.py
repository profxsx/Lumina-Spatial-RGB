
"""
Lumina Modular Bootstrapper Script
Generates the entire modular directory structure and writes all base files directly.
"""
import os
import math

folders = [
    "core",
    "hal",
    "audio",
    "managers",
    "effects",
    "plugins",
    "assets",
    "gifs",
    "api"
]

files = {}

# 1. Requirements
files["requirements.txt"] = """
fastapi==0.110.0
uvicorn==0.28.0
numpy==1.26.4
pillow==10.2.0
pydantic==2.6.4
""".strip()

# 2. Core Config
files["core/config.py"] = """
import os
import json
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class AppSettings(BaseModel):
    openrgb_host: str = "127.0.0.1"
    openrgb_port: int = 6742
    target_fps: int = Field(default=30, ge=10, le=120)
    canvas_width: int = 320
    active_effect: str = "RainbowWave"
    audio_mode: str = "input"
    audio_device_id: str = "default"
    audio_emulation: bool = False
    audio_noise_gate: float = Field(default=0.02, ge=0.0, le=0.2)
    effect_parameters: Dict[str, Any] = Field(default_factory=dict)
    favorited_effects: List[str] = Field(default_factory=list)
    enabled_plugins: List[str] = Field(default_factory=list)
    plugin_parameters: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    gif_library_names: Dict[str, str] = Field(default_factory=dict)
    active_gif_filename: str = "target.gif"
    devices_layout: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

class ConfigManager:
    def __init__(self, filename: str = "config.json"):
        self.filename = filename
        self.config = self.load_config()

    def load_config(self) -> AppSettings:
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    return AppSettings(**json.load(f))
            except Exception as e:
                print(f"[*] Configuration load failed: {e}. Reverting to defaults.")
        
        default_config = AppSettings()
        default_config.devices_layout = {
            "virtual_apex5": {
                "x": 0.05, "y": 0.25, "width": 0.55, "height": 0.35,
                "led_order": list(range(90)), "enabled": True, "form_type": "KEYBOARD",
                "custom_profiles": {}, "active_profile": "procedural"
            },
            "virtual_ram_1": {
                "x": 0.65, "y": 0.2, "width": 0.05, "height": 0.3,
                "led_order": list(range(8)), "enabled": True, "form_type": "RAM",
                "custom_profiles": {}, "active_profile": "procedural"
            },
            "virtual_strimer": {
                "x": 0.75, "y": 0.2, "width": 0.18, "height": 0.5,
                "led_order": list(range(120)), "enabled": True, "form_type": "STRIMER_24PIN",
                "custom_profiles": {}, "active_profile": "procedural"
            }
        }
        return default_config

    def save_config(self):
        try:
            with open(self.filename, 'w') as f:
                try:
                    data_str = self.config.model_dump_json(indent=4)
                except AttributeError:
                    data_str = self.config.json(indent=4)
                f.write(data_str)
        except Exception as e:
            print(f"[*] Failed to save configuration: {e}")
""".strip()

# 3. Core Canvas
files["core/canvas.py"] = """
import numpy as np
import asyncio

class CanvasRenderer:
    def __init__(self, width: int):
        self.width = width
        self.height = int(width * 10 // 16)
        self._buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self._lock = asyncio.Lock()

    async def resize(self, width: int):
        async with self._lock:
            self.width = width
            self.height = int(width * 10 // 16)
            self._buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)

    @property
    def buffer(self) -> np.ndarray:
        return self._buffer

class LEDSampler:
    @staticmethod
    def sample(canvas_buffer: np.ndarray, coordinates: np.ndarray) -> np.ndarray:
        h, w, _ = canvas_buffer.shape
        if coordinates.size == 0:
            return np.zeros((0, 3), dtype=np.uint8)
        x_indices = np.clip((coordinates[:, 0] * (w - 1)), 0, w - 1).astype(np.int32)
        y_indices = np.clip((coordinates[:, 1] * (h - 1)), 0, h - 1).astype(np.int32)
        return canvas_buffer[y_indices, x_indices]
""".strip()

# 4. Core Sampler
files["core/sampler.py"] = """
# Kept for package initialization
""".strip()

# 5. HAL Base
files["hal/base.py"] = """
import numpy as np
import math
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class AbstractRGBDevice(ABC):
    def __init__(self, device_id: str, name: str, led_count: int, form_type: str):
        self.device_id = device_id
        self.name = name
        self.led_count = led_count
        self.form_type = form_type
        self.enabled: bool = True
        self.x: float = 0.1
        self.y: float = 0.1
        self.width: float = 0.3
        self.height: float = 0.2
        self.local_coords: np.ndarray = np.zeros((led_count, 2), dtype=np.float32)
        self.custom_profiles: Dict[str, List[List[float]]] = {}
        self.active_profile: str = "procedural"
        self.coordinates: np.ndarray = np.zeros((led_count, 2), dtype=np.float32)
        self.led_order_mapping: np.ndarray = np.arange(led_count, dtype=np.int32)
        self._build_local_layout()
        self.recompute_global_coordinates()

    def _build_local_layout(self):
        if "RAM" in self.form_type:
            y_steps = np.linspace(0.1, 0.9, self.led_count)
            self.local_coords[:, 0] = 0.5
            self.local_coords[:, 1] = y_steps
        elif "KEYBOARD" in self.form_type:
            rows, cols = 6, 15
            for i in range(self.led_count):
                r = i // cols
                c = i % cols
                self.local_coords[i, 0] = 0.05 + (c / max(1, cols - 1)) * 0.9
                self.local_coords[i, 1] = 0.08 + (r / max(1, rows - 1)) * 0.84
        elif "FAN" in self.form_type:
            for i in range(self.led_count):
                angle = (i / self.led_count) * 2.0 * np.pi
                self.local_coords[i, 0] = 0.5 + 0.4 * math.cos(angle)
                self.local_coords[i, 1] = 0.5 + 0.4 * math.sin(angle)
        elif "STRIMER" in self.form_type:
            num_lines = 12 if "24PIN" in self.form_type else 8
            leds_per_line = self.led_count // num_lines
            if leds_per_line == 0: leds_per_line = 1
            for i in range(self.led_count):
                line_idx = i // leds_per_line
                led_idx = i % leds_per_line
                self.local_coords[i, 0] = 0.08 + (line_idx / max(1, num_lines - 1)) * 0.84
                self.local_coords[i, 1] = 0.05 + (led_idx / max(1, leds_per_line - 1)) * 0.9
        else:
            x_steps = np.linspace(0.05, 0.95, self.led_count)
            self.local_coords[:, 0] = x_steps
            self.local_coords[:, 1] = 0.5

    def recompute_global_coordinates(self):
        active_local = self.local_coords
        if self.active_profile != "procedural" and self.active_profile in self.custom_profiles:
            active_local = np.array(self.custom_profiles[self.active_profile], dtype=np.float32)
        self.coordinates[:, 0] = self.x + active_local[:, 0] * self.width
        self.coordinates[:, 1] = self.y + active_local[:, 1] * self.height
        self.coordinates = np.clip(self.coordinates, 0.0, 1.0)

    def load_layout(self, layout: Dict[str, Any]):
        self.x = layout.get("x", self.x)
        self.y = layout.get("y", self.y)
        self.width = layout.get("width", self.width)
        self.height = layout.get("height", self.height)
        self.enabled = layout.get("enabled", self.enabled)
        self.form_type = layout.get("form_type", self.form_type)
        self.active_profile = layout.get("active_profile", "procedural")
        self.custom_profiles = layout.get("custom_profiles", {})
        if "led_order" in layout and len(layout["led_order"]) == self.led_count:
            self.led_order_mapping = np.array(layout["led_order"], dtype=np.int32)
        else:
            self.led_order_mapping = np.arange(self.led_count, dtype=np.int32)
        self._build_local_layout()
        self.recompute_global_coordinates()

    def export_layout(self) -> Dict[str, Any]:
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "enabled": self.enabled,
            "form_type": self.form_type,
            "active_profile": self.active_profile,
            "custom_profiles": self.custom_profiles,
            "led_order": self.led_order_mapping.tolist()
        }

    @abstractmethod
    async def push_colors(self, color_array: np.ndarray):
        pass
""".strip()

# 6. HAL Devices
files["hal/openrgb_client.py"] = """
import asyncio
import numpy as np
from hal.base import AbstractRGBDevice
try:
    from openrgb.utils import RGBColor
    OPENRGB_AVAILABLE = True
except ImportError:
    OPENRGB_AVAILABLE = False

class OpenRGBClientDevice(AbstractRGBDevice):
    def __init__(self, orbg_device, index: int):
        dev_id = f"openrgb_{index}"
        name = orbg_device.name.upper()
        if "KEYBOARD" in name: form = "KEYBOARD"
        elif "RAM" in name or "DRAM" in name: form = "RAM"
        elif "FAN" in name or "COOLER" in name: form = "FAN"
        elif "STRIMER" in name: form = "STRIMER_24PIN"
        else: form = "STRIP"
        super().__init__(dev_id, orbg_device.name, len(orbg_device.leds), form)
        self._raw_device = orbg_device

    async def push_colors(self, color_array: np.ndarray):
        if not self.enabled or not OPENRGB_AVAILABLE: return
        mapped_colors = color_array[self.led_order_mapping]
        def _sync_write():
            self._raw_device.set_colors([RGBColor(c[0], c[1], c[2]) for c in mapped_colors], fast=True)
        await asyncio.to_thread(_sync_write)
""".strip()

files["hal/virtual_device.py"] = """
import numpy as np
from hal.base import AbstractRGBDevice

class VirtualDemoDevice(AbstractRGBDevice):
    def __init__(self, device_id: str, name: str, led_count: int, form_type: str):
        super().__init__(device_id, name, led_count, form_type)
        self.last_sent_colors = [[0, 0, 0] for _ in range(led_count)]

    async def push_colors(self, color_array: np.ndarray):
        if not self.enabled: return
        self.last_sent_colors = color_array[self.led_order_mapping].tolist()
""".strip()

# 7. Audio Modules
files["audio/discovery.py"] = """
import shutil
import subprocess
from typing import Dict, List, Any

def discover_system_audio_devices() -> Dict[str, List[Dict[str, Any]]]:
    inputs, outputs = [], []
    if shutil.which("pactl"):
        try:
            res = subprocess.run(["pactl", "list", "short", "sources"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0:
                for line in res.stdout.strip().split("\\n"):
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[1].strip()
                        display_name = name
                        if name.startswith("alsa_input."):
                            display_name = name.replace("alsa_input.", "Mic: ").replace(".analog-stereo", "").replace("_", " ")
                        elif name.startswith("alsa_output."):
                            display_name = name.replace("alsa_output.", "Speaker: ").replace(".analog-stereo.monitor", "").replace("_", " ")
                        device_item = {"id": name, "name": display_name}
                        if ".monitor" in name: outputs.append(device_item)
                        else: inputs.append(device_item)
        except Exception as e:
            print(f"[*] Audio discovery error: {e}")
    if not inputs and not outputs and shutil.which("arecord"):
        try:
            res = subprocess.run(["arecord", "-L"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0:
                for line in res.stdout.split("\\n"):
                    line = line.strip()
                    if line and not line.startswith(" ") and ":" in line:
                        inputs.append({"id": line, "name": f"ALSA: {line}"})
        except Exception:
            pass
    if not inputs: inputs.append({"id": "default", "name": "System Default Microphone"})
    if not outputs: outputs.append({"id": "@DEFAULT_MONITOR@", "name": "System Default Output (Speakers)"})
    return {"inputs": inputs, "outputs": outputs}
""".strip()

files["audio/analyzer.py"] = """
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
            await self._audio_emulation_loop()
            return
        cmd = None
        device = self.device_id
        if self.mode == "output":
            if shutil.which("pw-record"):
                target = device if device and device != "default" else "@DEFAULT_MONITOR@"
                cmd = ["pw-record", "--target", target, "--format=s16", "--channels=1", "--rate=44100", "-"]
            elif shutil.which("parec"):
                target = device if device and device != "default" else "@DEFAULT_MONITOR@"
                cmd = ["parec", "-d", target, "--format=s16le", "--channels=1", "--rate=44100"]
        else:
            if shutil.which("pw-record"):
                target = device if device and device != "default" else "default"
                cmd = ["pw-record", "--target", target, "--format=s16", "--channels=1", "--rate=44100", "-"]
            elif shutil.which("parec"):
                target = device if device and device != "default" else "default"
                cmd = ["parec", "-d", target, "--format=s16le", "--channels=1", "--rate=44100"]
            elif shutil.which("arecord"):
                target = device if device else "default"
                cmd = ["arecord", "-D", target, "-f", "S16_LE", "-c", "1", "-r", "44100", "-t", "raw"]
        if not cmd:
            await self._audio_emulation_loop()
            return
        try:
            self.process = await asyncio.create_subprocess_exec(
                *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.DEVNULL
            )
        except Exception:
            await self._audio_emulation_loop()
            return
        chunk_size = 512
        byte_size = chunk_size * 2
        try:
            while self.running and self.process.returncode is None:
                data = await self.process.stdout.readexactly(byte_size)
                if not data: break
                decoded = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                if len(decoded) == 0: continue
                fft_data = np.abs(np.fft.rfft(decoded))
                lows_raw = float(np.mean(fft_data[0:10]) * 18.0)
                mids_raw = float(np.mean(fft_data[10:60]) * 28.0)
                highs_raw = float(np.mean(fft_data[60:]) * 45.0)
                self.lows = lows_raw if lows_raw >= self.noise_gate else 0.0
                self.mids = mids_raw if mids_raw >= self.noise_gate else 0.0
                self.highs = highs_raw if highs_raw >= self.noise_gate else 0.0
                self.lows = min(1.0, max(0.0, self.lows))
                self.mids = min(1.0, max(0.0, self.mids))
                self.highs = min(1.0, max(0.0, self.highs))
        except asyncio.IncompleteReadError:
            pass
        except Exception:
            pass
        finally:
            await self._cleanup_process()
            if self.running: await self._audio_emulation_loop()

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
        if self._loop_task: self._loop_task.cancel()
        if self.process:
            try: self.process.terminate()
            except Exception: pass
""".strip()

# 8. Dynamic Managers
files["effects/base_effect.py"] = """
from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Any

class BaseEffect(ABC):
    @abstractmethod
    def render(self, canvas: np.ndarray, dt: float, params: Dict[str, Any], audio_bands: Dict[str, float]) -> np.ndarray:
        pass
    @abstractmethod
    def get_parameter_schema(self) -> Dict[str, Any]:
        pass
""".strip()

# Dynamic Seeding of Effects inside files dictionary to solve StopIteration
files["effects/rainbow_wave.py"] = r"""
import time
import numpy as np
from effects.base_effect import BaseEffect

class RainbowWave(BaseEffect):
    def render(self, canvas, dt, params, audio_bands):
        h, w, _ = canvas.shape
        speed = params.get("speed", 1.5)
        scale = params.get("scale", 0.5)
        t = time.time() * speed

        y, x = np.mgrid[0:h, 0:w]
        nx = x / max(1, w - 1)
        ny = y / max(1, h - 1)

        grad = (nx * scale + ny * (1.0 - scale)) * 2.0 * np.pi + t
        canvas[..., 0] = (np.sin(grad) * 127 + 128).astype(np.uint8)
        canvas[..., 1] = (np.sin(grad + 2 * np.pi / 3) * 127 + 128).astype(np.uint8)
        canvas[..., 2] = (np.sin(grad + 4 * np.pi / 3) * 127 + 128).astype(np.uint8)
        return canvas

    def get_parameter_schema(self):
        return {
            "speed": {"label": "Cycle Speed", "type": "range", "min": 0.1, "max": 10.0, "default": 1.5, "step": 0.1},
            "scale": {"label": "Angle Wave", "type": "range", "min": 0.0, "max": 1.0, "default": 0.5, "step": 0.05}
        }
""".strip()

files["effects/cyber_pulse.py"] = r"""
import time
import math
import numpy as np
from effects.base_effect import BaseEffect

class CyberPulse(BaseEffect):
    def render(self, canvas, dt, params, audio_bands):
        speed = params.get("speed", 2.0)
        t = time.time() * speed
        intensity = (math.sin(t) * 0.5 + 0.5)
        
        primary_color = np.array(params.get("primary", [236, 72, 153]))
        secondary_color = np.array(params.get("secondary", [6, 182, 212]))
        
        canvas[:, :] = (primary_color * intensity + secondary_color * (1.0 - intensity)).astype(np.uint8)
        return canvas

    def get_parameter_schema(self):
        return {
            "speed": {"label": "Pulse Speed", "type": "range", "min": 0.5, "max": 5.0, "default": 2.0, "step": 0.1},
            "primary": {"label": "Neon Primary", "type": "color", "default": [236, 72, 153]},
            "secondary": {"label": "Neon Secondary", "type": "color", "default": [6, 182, 212]}
        }
""".strip()

files["effects/audio_spectrum.py"] = r"""
import numpy as np
from effects.base_effect import BaseEffect

class AudioSpectrumBlast(BaseEffect):
    def render(self, canvas, dt, params, audio_bands):
        h, w, _ = canvas.shape
        canvas.fill(0)

        gain = params.get("gain", 1.2)
        lows_bar = int(audio_bands["lows"] * gain * h)
        mids_bar = int(audio_bands["mids"] * gain * h)
        highs_bar = int(audio_bands["highs"] * gain * h)

        seg_w = w // 3
        if lows_bar > 0:
            canvas[-lows_bar:, :seg_w] = [236, 72, 153]
        if mids_bar > 0:
            canvas[-mids_bar:, seg_w:2*seg_w] = [6, 182, 212]
        if highs_bar > 0:
            canvas[-highs_bar:, 2*seg_w:] = [34, 197, 94]

        return canvas

    def get_parameter_schema(self):
        return {
            "gain": {"label": "System Reactivity Gain", "type": "range", "min": 0.5, "max": 5.0, "default": 1.5, "step": 0.1}
        }
""".strip()

files["effects/gif_player.py"] = r"""
import os
import time
import numpy as np
from PIL import Image
from effects.base_effect import BaseEffect

class GifPlayer(BaseEffect):
    def __init__(self):
        self.gif_path = "./gifs/target.gif"
        self.frames = []
        self.last_time = time.time()
        self.current_frame = 0
        self.loaded = False
        self.last_path = ""

    def load_gif(self, active_filename):
        target_path = f"./gifs/{active_filename}"
        if not os.path.exists(target_path):
            target_path = "./gifs/target.gif"
            
        if self.loaded and target_path == self.last_path:
            return
            
        try:
            img = Image.open(target_path)
            self.frames = []
            while True:
                self.frames.append(img.convert("RGB"))
                try:
                    img.seek(img.tell() + 1)
                except EOFError:
                    break
            self.last_path = target_path
            self.loaded = True
        except Exception as e:
            print(f"[*] Failed to parse GIF file {target_path}: {e}")
            self.loaded = False

    def render(self, canvas, dt, params, audio_bands):
        active_file = params.get("_active_gif_file", "target.gif")
        self.load_gif(active_file)
        
        if not self.loaded or not self.frames:
            canvas.fill(10)
            canvas[10:-10, 10:-10] = [236, 72, 153]
            return canvas

        h, w, _ = canvas.shape
        speed = params.get("playback_speed", 1.0)
        grayscale_mode = params.get("grayscale", False)
        
        now = time.time()
        if now - self.last_time > (0.15 / speed):
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_time = now

        frame_img = self.frames[self.current_frame].resize((w, h))
        raw_frame = np.array(frame_img)
        
        if grayscale_mode:
            gray = np.dot(raw_frame[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
            canvas[..., 0] = gray
            canvas[..., 1] = gray
            canvas[..., 2] = gray
        else:
            canvas[:, :] = raw_frame
            
        return canvas

    def get_parameter_schema(self):
        return {
            "playback_speed": {"label": "GIF Playback Speed", "type": "range", "min": 0.1, "max": 5.0, "default": 1.0, "step": 0.1},
            "grayscale": {"label": "Grayscale (Black & White)", "type": "toggle", "default": False},
            "_active_gif_file": {"label": "Internal File Binding", "type": "hidden", "default": "target.gif"}
        }
""".strip()

# Dynamic Seeding of Plugins
files["plugins/audio_pulsar.py"] = r"""
import numpy as np

class AudioPulsarPlugin:
    def __init__(self):
        self.name = "Audio Pulsar"
        self.description = "Creates a pulsating ring mapped to live system bass output."
        
    def render_frame(self, canvas, dt, params, audio_bands):
        h, w, _ = canvas.shape
        bass = audio_bands["lows"] * params.get("multiplier", 1.5)
        glow_color = params.get("glow_color", [6, 182, 212])
        
        cx, cy = w // 2, h // 2
        radius = int(min(w, h) * 0.15 + bass * min(w, h) * 0.3)
        radius = max(2, min(radius, min(w, h) // 2 - 1))
        
        y, x = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((x - cx)**2 + (y - cy)**2)
        mask = (dist_from_center >= radius - 3) & (dist_from_center <= radius + 3)
        canvas[mask] = glow_color
        return canvas

    def get_settings_schema(self):
        return {
            "multiplier": {"label": "React Limit", "type": "range", "min": 0.5, "max": 5.0, "default": 1.5, "step": 0.1},
            "glow_color": {"label": "Neon Color", "type": "color", "default": [6, 182, 212]}
        }
""".strip()

files["managers/effect_manager.py"] = """
import os
import inspect
import importlib.util
from typing import Dict
from effects.base_effect import BaseEffect
from core.config import ConfigManager

def ensure_effects_directory():
    os.makedirs("./effects", exist_ok=True)
    os.makedirs("./assets", exist_ok=True)
    os.makedirs("./gifs", exist_ok=True)

class EffectManager:
    def __init__(self, config_manager: ConfigManager):
        self.cm = config_manager
        self.effects: Dict[str, BaseEffect] = {}
        ensure_effects_directory()
        self.load_all_effects()

    def load_all_effects(self):
        self.effects.clear()
        if not os.path.exists("./effects"): return
        for file in os.listdir("./effects"):
            if file.endswith(".py") and file != "base_effect.py" and not file.startswith("__"):
                module_name = file[:-3]
                module_path = os.path.join("./effects", file)
                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        for name, cls in inspect.getmembers(module, inspect.isclass):
                            if cls.__module__ == module_name and hasattr(cls, "render") and hasattr(cls, "get_parameter_schema"):
                                self.effects[name] = cls()
                                print(f"[*] Registered Effect: {name}")
                except Exception as e:
                    print(f"[*] Failed to import effect {file}: {e}")
""".strip()

files["managers/plugin_manager.py"] = """
import os
import inspect
import importlib.util
from typing import Dict, Any
from core.config import ConfigManager

def ensure_plugins_directory():
    os.makedirs("./plugins", exist_ok=True)

class PluginManager:
    def __init__(self, config_manager: ConfigManager):
        self.cm = config_manager
        self.plugins: Dict[str, Dict[str, Any]] = {}
        ensure_plugins_directory()
        self.load_all_plugins()

    def load_all_plugins(self):
        self.plugins.clear()
        cfg = self.cm.config
        if not os.path.exists("./plugins"): return
        for file in os.listdir("./plugins"):
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]
                module_path = os.path.join("./plugins", file)
                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        for name, cls in inspect.getmembers(module, inspect.isclass):
                            if cls.__module__ == module_name and hasattr(cls, "render_frame") and hasattr(cls, "get_settings_schema"):
                                instance = cls()
                                is_enabled = module_name in cfg.enabled_plugins
                                saved_params = cfg.plugin_parameters.get(module_name, {})
                                resolved_params = self._resolve_params(instance, saved_params)
                                self.plugins[module_name] = {
                                    "id": module_name,
                                    "name": getattr(instance, "name", module_name),
                                    "description": getattr(instance, "description", "Custom plugin"),
                                    "class_name": name,
                                    "instance": instance,
                                    "enabled": is_enabled,
                                    "params": resolved_params,
                                    "schema": instance.get_settings_schema()
                                }
                                print(f"[*] Registered Plugin: {name}")
                except Exception as e:
                    print(f"[*] Failed to import plugin {file}: {e}")
        for plug_id in self.plugins:
            if plug_id not in cfg.plugin_parameters:
                cfg.plugin_parameters[plug_id] = self.plugins[plug_id]["params"]
        self.cm.save_config()

    def _resolve_params(self, instance: Any, saved_params: Dict[str, Any]) -> Dict[str, Any]:
        resolved = {}
        schema = instance.get_settings_schema()
        for k, v in schema.items():
            resolved[k] = saved_params.get(k, v["default"])
        return resolved
""".strip()

# 9. Core Engine Loop
files["core/engine.py"] = """
import asyncio
import time
import numpy as np
from typing import List, Optional, Dict, Any
from core.config import ConfigManager
from core.canvas import CanvasRenderer, LEDSampler
from audio.analyzer import AudioAnalyzer
from managers.effect_manager import EffectManager
from managers.plugin_manager import PluginManager
from hal.base import AbstractRGBDevice
from hal.openrgb_client import OpenRGBClientDevice, OPENRGB_AVAILABLE
from hal.virtual_device import VirtualDemoDevice

try:
    from openrgb import OpenRGBClient
except ImportError:
    pass

class EngineCore:
    def __init__(self, config_manager: ConfigManager):
        self.cm = config_manager
        cfg = self.cm.config
        self.canvas = CanvasRenderer(cfg.canvas_width)
        self.audio = AudioAnalyzer()
        self.effect_manager = EffectManager(config_manager)
        self.plugin_manager = PluginManager(config_manager)
        self.devices: List[AbstractRGBDevice] = []
        self.active_effect_name: str = cfg.active_effect
        self.effect_params: Dict[str, Any] = self._resolve_params(self.active_effect_name, cfg.effect_parameters)
        self.highlight_device_id: Optional[str] = None
        self.highlight_led_index: int = -1
        self.running: bool = False
        self._loop_task: Optional[asyncio.Task] = None

    def _resolve_params(self, effect_name: str, saved_params: Dict[str, Any]) -> Dict[str, Any]:
        effect = self.effect_manager.effects.get(effect_name, next(iter(self.effect_manager.effects.values())))
        resolved = {}
        for k, v in effect.get_parameter_schema().items():
            resolved[k] = saved_params.get(k, v["default"])
        return resolved

    def initialize_hardware(self):
        self.devices.clear()
        cfg = self.cm.config
        if OPENRGB_AVAILABLE:
            try:
                client = OpenRGBClient(cfg.openrgb_host, cfg.openrgb_port)
                for idx, dev in enumerate(client.devices):
                    wrapped = OpenRGBClientDevice(dev, idx)
                    if dev.name in cfg.devices_layout: wrapped.load_layout(cfg.devices_layout[dev.name])
                    elif wrapped.device_id in cfg.devices_layout: wrapped.load_layout(cfg.devices_layout[wrapped.device_id])
                    else: wrapped.load_layout({})
                    self.devices.append(wrapped)
                print(f"[*] Bound {len(self.devices)} physical OpenRGB targets.")
            except Exception as e:
                print(f"[*] OpenRGB Server unavailable: {e}")
        if not self.devices:
            print("[*] Launching layout engine in virtual simulation mode.")
            v_apex = VirtualDemoDevice("virtual_apex5", "SteelSeries Apex 5", 90, "KEYBOARD")
            v_ram1 = VirtualDemoDevice("virtual_ram_1", "Crucial Ballistix RAM 1", 8, "RAM")
            v_strimer = VirtualDemoDevice("virtual_strimer", "Lian Li Strimer Ribbon", 120, "STRIMER_24PIN")
            for d in [v_apex, v_ram1, v_strimer]:
                if d.device_id in self.cm.config.devices_layout: d.load_layout(self.cm.config.devices_layout[d.device_id])
                else: d.load_layout({})
                self.devices.append(d)

    async def update_active_effect(self, effect_name: str):
        if effect_name in self.effect_manager.effects:
            self.active_effect_name = effect_name
            self.effect_params = self._resolve_params(effect_name, {})
            self.cm.config.active_effect = effect_name
            self.cm.config.effect_parameters = self.effect_params
            self.cm.save_config()

    async def update_parameter(self, param_key: str, param_val: Any):
        self.effect_params[param_key] = param_val
        self.cm.config.effect_parameters = self.effect_params
        self.cm.save_config()

    def start(self):
        self.running = True
        self.audio.start(self.cm.config.audio_mode, self.cm.config.audio_device_id, self.cm.config.audio_emulation, self.cm.config.audio_noise_gate)
        self.initialize_hardware()
        self._loop_task = asyncio.create_task(self._engine_tick_loop())

    async def stop(self):
        self.running = False
        self.audio.stop()
        if self._loop_task:
            self._loop_task.cancel()
            try: await self._loop_task
            except asyncio.CancelledError: pass
        self.cm.save_config()

    async def _engine_tick_loop(self):
        while self.running:
            now = time.perf_counter()
            dt = 1.0 / self.cm.config.target_fps
            active_eff = self.effect_manager.effects.get(self.active_effect_name, next(iter(self.effect_manager.effects.values())))
            async with self.canvas._lock:
                audio_bands = {"lows": self.audio.lows, "mids": self.audio.mids, "highs": self.audio.highs}
                active_eff.render(self.canvas.buffer, dt, self.effect_params, audio_bands)
                for plug_id, plug_data in self.plugin_manager.plugins.items():
                    if plug_data["enabled"]:
                        try:
                            plug_data["instance"].render_frame(self.canvas.buffer, dt, plug_data["params"], audio_bands)
                        except Exception as e:
                            print(f"[*] Plugin {plug_id} crashed: {e}")
                current_frame = self.canvas.buffer.copy()
            tasks = []
            for device in self.devices:
                if not device.enabled: continue
                if self.highlight_device_id == device.device_id:
                    colors = np.zeros((device.led_count, 3), dtype=np.uint8)
                    if 0 <= self.highlight_led_index < device.led_count:
                        indices = np.where(device.led_order_mapping == self.highlight_led_index)[0]
                        if indices.size > 0: colors[indices[0]] = [6, 182, 212]
                        else:
                            if self.highlight_led_index < device.led_count: colors[self.highlight_led_index] = [6, 182, 212]
                    tasks.append(device.push_colors(colors))
                elif self.active_effect_name == "SequenceWave":
                    speed = self.effect_params.get("speed", 2.5)
                    t = time.time() * speed
                    indices = np.arange(device.led_count)
                    phase = (indices / max(1, device.led_count - 1)) * 2.0 * np.pi - t
                    r = (np.sin(phase) * 127 + 128).astype(np.uint8)
                    g = (np.sin(phase + 2 * np.pi / 3) * 127 + 128).astype(np.uint8)
                    b = (np.sin(phase + 4 * np.pi / 3) * 127 + 128).astype(np.uint8)
                    colors = np.stack([r, g, b], axis=-1)
                    tasks.append(device.push_colors(colors))
                else:
                    sampled = LEDSampler.sample(current_frame, device.coordinates)
                    tasks.append(device.push_colors(sampled))
            if tasks: await asyncio.gather(*tasks)
            elapsed = time.perf_counter() - now
            sleep_duration = max(0.0, (1.0 / self.cm.config.target_fps) - elapsed)
            await asyncio.sleep(sleep_duration)
""".strip()

# 10. Web Interface Templates File
files["api/templates.py"] = r"""
INDEX_HTML = r'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Lumina Control Panel</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            body {
                background-color: #050811;
                color: #e2e8f0;
                font-family: ui-sans-serif, system-ui, sans-serif;
            }
            .glass-panel {
                background: rgba(13, 19, 35, 0.7);
                backdrop-filter: blur(14px);
                border: 1px solid rgba(255, 255, 255, 0.06);
            }
            .cyber-tab {
                border-bottom: 2px solid transparent;
            }
            .cyber-tab.active {
                border-bottom: 2px solid #ec4899;
                color: #ec4899;
            }
            input[type="range"] {
                -webkit-appearance: none;
                background: #1e293b;
            }
            input[type="range"]::-webkit-slider-thumb {
                -webkit-appearance: none;
                height: 12px;
                width: 12px;
                border-radius: 50%;
                background: #06b6d4;
                cursor: pointer;
                box-shadow: 0 0 10px #06b6d4;
            }
            ::-webkit-scrollbar { width: 6px; }
            ::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); }
            ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
            ::-webkit-scrollbar-thumb:hover { background: #06b6d4; }
        </style>
    </head>
    <body class="h-screen w-screen overflow-hidden flex flex-col font-sans select-none">

        <!-- Header -->
        <header class="h-16 border-b border-slate-900 bg-slate-950/80 backdrop-blur-md flex items-center justify-between px-6 z-10 select-none">
            <div class="flex items-center gap-3">
                <div class="h-8 w-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-pink-500 flex items-center justify-center animate-pulse">
                    <i class="fa-solid fa-wand-magic-sparkles text-slate-950 text-sm"></i>
                </div>
                <div>
                    <h1 class="text-md font-bold tracking-wider text-slate-100 uppercase">Lumina <span class="text-cyan-400 font-black text-xs tracking-tighter">Spatial Studio</span></h1>
                    <p class="text-[9px] text-slate-500 font-mono tracking-widest uppercase">Arch Linux Edition // V4.10</p>
                </div>
            </div>

            <!-- Tab Navigation Control Bar -->
            <nav class="flex gap-6 h-full items-center text-xs font-mono tracking-wider uppercase font-bold text-slate-400">
                <button onclick="switchTab('layout')" id="tab-btn-layout" class="cyber-tab h-full px-2 transition-all flex items-center gap-2 hover:text-slate-200">
                    <i class="fa-solid fa-map-location-dot"></i> Layout Canvas
                </button>
                <button onclick="switchTab('shaders')" id="tab-btn-shaders" class="cyber-tab h-full px-2 transition-all flex items-center gap-2 hover:text-slate-200">
                    <i class="fa-solid fa-palette"></i> Effects
                </button>
                <button onclick="switchTab('plugins')" id="tab-btn-plugins" class="cyber-tab h-full px-2 transition-all flex items-center gap-2 hover:text-slate-200">
                    <i class="fa-solid fa-puzzle-piece"></i> Plugins
                </button>
                <button onclick="switchTab('devices')" id="tab-btn-devices" class="cyber-tab h-full px-2 transition-all flex items-center gap-2 hover:text-slate-200">
                    <i class="fa-solid fa-microchip"></i> Hardware
                </button>
                <button onclick="switchTab('settings')" id="tab-btn-settings" class="cyber-tab h-full px-2 transition-all flex items-center gap-2 hover:text-slate-200">
                    <i class="fa-solid fa-sliders"></i> Settings
                </button>
            </nav>

            <div class="flex items-center gap-2 text-xs font-mono">
                <span id="active-fps-display" class="text-slate-500">Target: 30 FPS</span>
            </div>
        </header>

        <!-- Dynamic Content Tabs -->
        <div class="flex-1 flex overflow-hidden">

            <!-- TAB 1: Draggable Workspace Layout Viewport -->
            <div id="tab-view-layout" class="flex-1 flex overflow-hidden">
                <!-- Workspace Side Options Column (Layout Settings) -->
                <aside class="w-80 border-r border-slate-900 bg-slate-950/30 p-4 flex flex-col gap-4 overflow-y-auto z-10">
                    <h2 class="text-xs font-bold font-mono tracking-widest uppercase text-slate-400">Canvas Options</h2>
                    <div class="glass-panel p-4 rounded-xl border border-slate-900 flex flex-col gap-4">
                        <div class="flex items-center gap-2 border-b border-slate-900 pb-2">
                            <i class="fa-solid fa-arrows-alt text-cyan-400"></i>
                            <span class="text-xs font-bold font-mono uppercase text-slate-200">Node Calibration</span>
                        </div>
                        <div class="flex flex-col gap-2 font-mono text-[10px]">
                            <p class="text-slate-500 leading-normal mb-2">Switch layout edit targets to calibrate coordinate grids or fine-tune individual LED pins.</p>
                            <div class="flex flex-col gap-1.5">
                                <label class="text-slate-400">Calibrator Targeting</label>
                                <select id="layout-edit-mode" onchange="toggleLayoutCalibratorMode(this.value)" class="w-full bg-slate-900 border border-slate-800 rounded py-1.5 px-3 outline-none text-slate-300">
                                    <option value="bounds">Device Boundaries (Standard Block Drag)</option>
                                    <option value="nodes" disabled>Fine-Grain Pins (Use Hardware Modal Instead)</option>
                                </select>
                            </div>
                        </div>
                    </div>
                </aside>

                <div class="flex-1 flex flex-col bg-[#03050a] p-6 relative">
                    <div class="flex items-center justify-between mb-4 font-mono text-[11px] text-slate-400">
                        <span><i class="fa-solid fa-expand mr-2"></i>Canvas is locked to panoramic widescreen (16:10 standard)</span>
                        <div class="flex items-center gap-2">
                            <span>Overlay Opacity:</span>
                            <input id="ref-opacity" type="range" min="0.0" max="1.0" step="0.1" value="0.3" class="w-16" oninput="updateRefOpacity(this.value)">
                        </div>
                    </div>
                    <!-- Layout Grid Viewport -->
                    <div class="flex-1 relative rounded-xl border border-slate-900/80 bg-slate-950/20 overflow-hidden shadow-inner flex items-center justify-center" id="canvas-workspace">
                        <!-- Restored rendering opacity & removed mix-blend-screen for clear visibility -->
                        <canvas id="stream-preview" class="absolute w-full h-full object-cover select-none pointer-events-none opacity-85 z-0" style="filter: blur(2px);"></canvas>
                        <div class="absolute inset-0 bg-[linear-gradient(to_right,#0d1324_1px,transparent_1px),linear-gradient(to_bottom,#0d1324_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none opacity-60 z-10"></div>
                        <div id="workspace-elements-root" class="absolute inset-0 z-20"></div>
                    </div>
                </div>
            </div>

            <!-- TAB 2: Effects Selection & Favorites Manager -->
            <div id="tab-view-shaders" class="flex-1 flex overflow-hidden hidden">
                <!-- Sidebar Parameters Card -->
                <aside class="w-80 border-r border-slate-900 bg-slate-950/30 p-4 flex flex-col gap-4 overflow-y-auto">
                    
                    <!-- Dynamic GIF Library Panel (Placed on the left of effect configurations) -->
                    <div id="shader-gif-panel" class="hidden flex flex-col gap-3">
                        <h2 class="text-xs font-bold font-mono tracking-widest uppercase text-slate-400">GIF Library Manager</h2>
                        <div class="glass-panel p-3 rounded-xl border border-slate-900 flex flex-col gap-3">
                            <input type="text" id="gif-library-search" oninput="onGifSearch(this.value)" placeholder="Search animations..." class="w-full bg-slate-950 border border-slate-800 rounded py-1 px-2.5 text-[10px] text-slate-300 outline-none focus:border-cyan-500 font-mono">
                            <div id="gif-library-list" class="flex flex-col gap-2 max-h-48 overflow-y-auto border-b border-slate-900 pb-2">
                                <!-- Dynamically populated GIF Cards -->
                            </div>
                            
                            <!-- Drag-and-Drop Custom GIF File Upload Panel -->
                            <div id="effect-upload-container" class="flex flex-col gap-1.5 text-[10px] font-mono">
                                <label class="text-slate-400 uppercase tracking-widest text-[9px]"><i class="fa-solid fa-upload"></i> Upload Custom GIF</label>
                                <div class="border border-dashed border-slate-800 rounded-lg p-3 text-center cursor-pointer hover:border-pink-500/40 transition-colors"
                                     onclick="document.getElementById('gif-uploader-input').click()"
                                     ondragover="event.preventDefault()"
                                     ondrop="handleGifDrop(event)">
                                    <span class="text-slate-500 text-[9px]">Drop .gif file here or click to browse</span>
                                    <input type="file" id="gif-uploader-input" accept="image/gif" class="hidden" onchange="handleGifSelect(this)">
                                </div>
                            </div>
                        </div>
                    </div>

                    <h2 class="text-xs font-bold font-mono tracking-widest uppercase text-slate-400">Effect Controls</h2>
                    <div class="glass-panel p-4 rounded-xl border border-slate-900 flex flex-col gap-4">
                        <div class="flex items-center gap-2 border-b border-slate-900 pb-2">
                            <i class="fa-solid fa-palette text-cyan-400"></i>
                            <span id="active-shader-title" class="text-xs font-bold font-mono uppercase text-slate-200">No Active Effect</span>
                        </div>
                        <div id="params-container" class="flex flex-col gap-4">
                            <!-- Dynamic settings sliders generated dynamically -->
                        </div>
                    </div>
                </aside>
                <!-- Main Grid Options Content -->
                <main class="flex-1 bg-[#03050a] p-6 flex flex-col gap-4 overflow-y-auto">
                    <div class="flex items-center gap-4">
                        <!-- Search Box -->
                        <div class="relative flex-1 max-w-md">
                            <i class="fa-solid fa-magnifying-glass absolute left-3 top-2.5 text-slate-500 text-xs"></i>
                            <input type="text" id="effect-search" oninput="renderEffectsList()" placeholder="Search effects (e.g. Wave, Pulse...)" class="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 pl-9 pr-4 text-xs text-slate-300 outline-none focus:border-cyan-500">
                        </div>
                    </div>
                    
                    <!-- Shader Matrix Cards -->
                    <div id="effects-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>
                </main>
            </div>

            <!-- TAB 3: Plugins Manager -->
            <div id="tab-view-plugins" class="flex-1 flex overflow-hidden hidden">
                <!-- Sidebar Parameters Card -->
                <aside class="w-80 border-r border-slate-900 bg-slate-950/30 p-4 flex flex-col gap-4 overflow-y-auto">
                    <h2 class="text-xs font-bold font-mono tracking-widest uppercase text-slate-400">Plugin Settings</h2>
                    <div class="glass-panel p-4 rounded-xl border border-slate-900 flex flex-col gap-4">
                        <div class="flex items-center gap-2 border-b border-slate-900 pb-2">
                            <i class="fa-solid fa-sliders text-pink-500"></i>
                            <span id="active-plugin-title" class="text-xs font-bold font-mono uppercase text-slate-200">Select a Plugin</span>
                        </div>
                        <div id="plugin-params-container" class="flex flex-col gap-4">
                            <!-- Populated dynamically upon clicking plugin card -->
                            <p class="text-[10px] text-slate-500 font-mono text-center py-4">Click "Config" on an enabled plugin to modify its settings.</p>
                        </div>
                    </div>
                </aside>
                <!-- Main Grid Options Content -->
                <main class="flex-1 bg-[#03050a] p-6 flex flex-col gap-4 overflow-y-auto">
                    <h2 class="text-xs font-bold font-mono tracking-widest uppercase text-slate-400">Discovered Extensions</h2>
                    <div id="plugins-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        <!-- Dynamic plugins injected -->
                    </div>
                </main>
            </div>

            <!-- TAB 4: Device Calibration Index Ordering -->
            <div id="tab-view-devices" class="flex-1 flex overflow-hidden hidden">
                <main class="flex-1 bg-[#03050a] p-6 flex flex-col gap-4 overflow-y-auto">
                    <h2 class="text-xs font-bold font-mono tracking-widest uppercase text-slate-400">Active Controllers & Modules</h2>
                    <div id="hardware-cards-container" class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <!-- Instantiated below -->
                    </div>
                </main>
            </div>

            <!-- TAB 5: Engine Global Settings Configuration -->
            <div id="tab-view-settings" class="flex-1 flex items-center justify-center bg-[#03050a] p-6 overflow-y-auto">
                <div class="glass-panel p-6 rounded-xl border border-slate-800 w-full max-w-md shadow-2xl flex flex-col gap-5">
                    <h2 class="text-sm font-bold font-mono tracking-wider uppercase text-slate-200 border-b border-slate-900 pb-3">
                        <i class="fa-solid fa-gears text-cyan-400 mr-2"></i> System Configuration
                    </h2>
                    
                    <div class="flex flex-col gap-4 text-xs font-mono">
                        <div class="flex flex-col gap-1.5">
                            <label class="text-slate-400">OpenRGB Server Host</label>
                            <input type="text" id="setting-host" class="w-full bg-slate-900 border border-slate-700 rounded-md py-2 px-3 text-slate-200 outline-none focus:border-cyan-500">
                        </div>
                        <div class="flex flex-col gap-1.5">
                            <label class="text-slate-400">OpenRGB Server Port</label>
                            <input type="number" id="setting-port" class="w-full bg-slate-900 border border-slate-700 rounded-md py-2 px-3 text-slate-200 outline-none focus:border-cyan-500">
                        </div>
                        
                        <!-- Cascading Audio Settings Dropdowns -->
                        <div class="flex flex-col gap-1.5 border-t border-slate-900/60 pt-3">
                            <label class="text-slate-400">Audio capture Mode</label>
                            <select id="setting-audio-mode" onchange="onAudioModeChange(this.value)" class="w-full bg-slate-900 border border-slate-700 rounded-md py-2 px-3 text-slate-200 outline-none focus:border-cyan-500">
                                <option value="input">Input (Microphones / Physical Inputs)</option>
                                <option value="output">Output (System Sound Monitors / Loopback)</option>
                            </select>
                        </div>
                        <div class="flex flex-col gap-1.5">
                            <label class="text-slate-400">Target Sound Interface</label>
                            <select id="setting-audio-device" class="w-full bg-slate-900 border border-slate-700 rounded-md py-2 px-3 text-slate-200 outline-none focus:border-cyan-500">
                                <!-- Dynamically populated based on active Mode -->
                            </select>
                        </div>
                        
                        <!-- Calibration Audio Noise Gate and Demo Toggles -->
                        <div class="flex flex-col gap-1.5 border-t border-slate-900/60 pt-3">
                            <div class="flex items-center justify-between">
                                <label class="text-slate-400">Mute Real Audio (Enable Demo waves)</label>
                                <button onclick="toggleAudioEmulation()" id="setting-audio-emulation-btn" class="text-cyan-400 text-lg">
                                    <i class="fa-solid fa-toggle-off"></i>
                                </button>
                            </div>
                        </div>
                        <div class="flex flex-col gap-1.5">
                            <div class="flex justify-between">
                                <label class="text-slate-400">Noise Gate Threshold</label>
                                <span id="val-noise-gate" class="text-pink-500 font-bold">0.02</span>
                            </div>
                            <input type="range" id="setting-noise-gate" min="0.00" max="0.20" step="0.01" value="0.02" class="w-full" oninput="document.getElementById('val-noise-gate').textContent=this.value">
                        </div>

                        <!-- Real-Time Decoupled Live Audio Telemetry Meter -->
                        <div class="flex flex-col gap-1.5 border-t border-slate-900/60 pt-3">
                            <label class="text-slate-400 uppercase tracking-widest text-[10px]">Real-Time Capture Amplitude Telemetry</label>
                            <div class="flex flex-col gap-2 bg-slate-950 p-3 rounded-lg border border-slate-900">
                                <div class="flex items-center gap-3">
                                    <span class="w-8 text-[9px] text-pink-400">LOWS</span>
                                    <div class="flex-1 h-2 bg-slate-900 rounded-full overflow-hidden">
                                        <div id="telemetry-bar-lows" class="h-full bg-pink-500 shadow-[0_0_8px_#ec4899] transition-all duration-75" style="width: 0%"></div>
                                    </div>
                                </div>
                                <div class="flex items-center gap-3">
                                    <span class="w-8 text-[9px] text-cyan-400">MIDS</span>
                                    <div class="flex-1 h-2 bg-slate-900 rounded-full overflow-hidden">
                                        <div id="telemetry-bar-mids" class="h-full bg-cyan-500 shadow-[0_0_8px_#06b6d4] transition-all duration-75" style="width: 0%"></div>
                                    </div>
                                </div>
                                <div class="flex items-center gap-3">
                                    <span class="w-8 text-[9px] text-green-400">HIGHS</span>
                                    <div class="flex-1 h-2 bg-slate-900 rounded-full overflow-hidden">
                                        <div id="telemetry-bar-highs" class="h-full bg-green-500 shadow-[0_0_8px_#22c55e] transition-all duration-75" style="width: 0%"></div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Dynamic Canvas Matrix Boundaries Scaling controls -->
                        <div class="flex flex-col gap-1.5 border-t border-slate-900/60 pt-3">
                            <div class="flex justify-between">
                                <label class="text-slate-400">Virtual Canvas Dimensions</label>
                                <span id="val-canvas-res" class="text-cyan-400 font-bold">320 px Width (16:10 Ratio)</span>
                            </div>
                            <input type="range" id="setting-canvas-res" min="160" max="480" step="16" class="w-full" oninput="document.getElementById('val-canvas-res').textContent=`${this.value} px Width (16:10 Ratio)`">
                        </div>

                        <div class="flex flex-col gap-1.5 border-t border-slate-900/60 pt-3">
                            <div class="flex justify-between">
                                <label class="text-slate-400">Engine Output Target FPS</label>
                                <span id="val-target-fps" class="text-cyan-400 font-bold">30</span>
                            </div>
                            <input type="range" id="setting-fps" min="10" max="120" step="5" class="w-full" oninput="document.getElementById('val-target-fps').textContent=this.value">
                        </div>
                    </div>

                    <button onclick="saveGlobalSettings()" class="w-full py-2 bg-gradient-to-r from-cyan-500 to-pink-500 text-slate-950 font-extrabold rounded-lg hover:brightness-110 transition-all font-mono text-xs uppercase shadow-[0_0_15px_rgba(6,182,212,0.3)]">
                        Apply Settings
                    </button>
                </div>
            </div>

        </div>

        <!-- Custom Order Sequencer Pin Mapping Modal -->
        <div id="reorder-modal" class="fixed inset-0 bg-slate-950/85 backdrop-blur-md hidden items-center justify-center z-50 p-4">
            <div class="glass-panel p-6 rounded-xl border border-slate-800 w-full max-w-lg shadow-2xl flex flex-col gap-4">
                <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div>
                        <h3 class="text-sm font-bold tracking-wider font-mono uppercase text-slate-200">Reorder Diagnostics Map</h3>
                        <p class="text-[10px] text-pink-500 font-mono mt-0.5"><i class="fa-solid fa-lightbulb"></i> Non-target LEDs remain black on your desktop</p>
                    </div>
                    <button onclick="closeReorderModal()" class="text-slate-400 hover:text-slate-200 text-sm"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <p class="text-xs text-slate-400 leading-relaxed font-mono">
                    Click physical nodes sequentially inside the pool. Each hovered button lights up that exact physical LED in <span class="text-cyan-400 font-bold">Cyan</span>, allowing you to instantly map the hardware pathway.
                </p>
                <div id="modal-node-pool" class="flex flex-wrap gap-2 py-4 justify-center bg-slate-950 rounded-lg p-4 border border-slate-900 shadow-inner max-h-60 overflow-y-auto"></div>
                <div class="flex items-center justify-between border-t border-slate-800 pt-3 mt-2 text-xs font-mono">
                    <div class="text-slate-500">Assigned Mapping: <span id="modal-sequence-preview" class="text-pink-500 font-bold">[]</span></div>
                    <div class="flex gap-2">
                        <button onclick="resetReorderSequence()" class="px-3 py-1 bg-slate-900 border border-slate-700 rounded text-slate-300 hover:bg-slate-800">Clear Map</button>
                        <button onclick="saveReorderSequence()" class="px-3 py-1 bg-cyan-500 text-slate-950 font-bold rounded hover:bg-cyan-400">Save Sequence</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- NEW: Dedicated Single-Device Calibration Modal Workspace -->
        <div id="calibration-modal" class="fixed inset-0 bg-slate-950/95 backdrop-blur-md hidden flex-col z-50 p-6 select-none font-sans">
            <!-- Modal Header -->
            <div class="h-12 border-b border-slate-900 flex items-center justify-between pb-3 flex-none">
                <div>
                    <h3 class="text-sm font-bold tracking-wider font-mono uppercase text-slate-200 flex items-center gap-2">
                        <i class="fa-solid fa-arrows-spin text-pink-500"></i> Local Calibrator: <span id="cal-modal-title" class="text-cyan-400">Device</span>
                    </h3>
                    <p class="text-[10px] text-slate-500 font-mono mt-0.5">MANUAL PIN CALIBRATION AND NODE-GRID SNAPPING</p>
                </div>
                <button onclick="closeCalibrationModal()" class="text-slate-400 hover:text-slate-200"><i class="fa-solid fa-xmark text-lg"></i></button>
            </div>
            
            <!-- Modal Content Grid -->
            <div class="flex-1 flex overflow-hidden py-4 gap-6 min-h-0">
                <!-- Left Panel: LED list + Grid Lock Settings -->
                <div class="w-80 flex flex-col gap-4 overflow-y-auto pr-2 flex-none">
                    <div class="glass-panel p-4 rounded-xl border border-slate-900 flex flex-col gap-3 font-mono text-[10px]">
                        <div class="flex items-center justify-between border-b border-slate-900 pb-2">
                            <span class="text-slate-300 font-bold uppercase">Grid Snapping (Grid Lock)</span>
                            <button onclick="toggleCalibrationGridLock()" id="cal-grid-lock-btn" class="text-cyan-400 text-lg">
                                <i class="fa-solid fa-toggle-off"></i>
                            </button>
                        </div>
                        <div class="flex flex-col gap-1.5">
                            <div class="flex justify-between">
                                <label class="text-slate-400">Grid Snappings</label>
                                <span id="cal-val-divisions" class="text-cyan-400 font-bold">16</span>
                            </div>
                            <!-- Snapping slider limit expanded to 100 -->
                            <input type="range" id="cal-setting-divisions" min="4" max="100" step="2" value="16" class="w-full" oninput="onCalDivisionsChange(this.value)">
                        </div>
                    </div>
                    
                    <div class="flex-1 flex flex-col gap-3 bg-slate-950/40 p-4 rounded-xl border border-slate-900/60 overflow-hidden min-h-0">
                        <span class="text-xs font-bold font-mono tracking-widest uppercase text-slate-400 border-b border-slate-900 pb-2">LED Directory</span>
                        <div class="relative flex-none">
                            <i class="fa-solid fa-magnifying-glass absolute left-3 top-2.5 text-slate-500 text-xs"></i>
                            <input type="text" id="cal-led-search" oninput="onCalLedSearch(this.value)" placeholder="Search LEDs..." class="w-full bg-slate-950 border border-slate-800 rounded py-1.5 pl-9 pr-3 text-[10px] text-slate-300 outline-none focus:border-cyan-500 font-mono">
                        </div>
                        <div id="cal-led-list-container" class="flex-1 overflow-y-auto flex flex-col gap-2 pr-1">
                            <!-- Injected LED directory items -->
                        </div>
                    </div>
                </div>
                
                <!-- Center/Right Panel: local relative 16:10 coordinate canvas -->
                <div class="flex-1 flex flex-col bg-slate-950/30 rounded-xl border border-slate-900/80 p-4 relative overflow-hidden flex items-center justify-center min-h-0">
                    <div class="w-full h-full relative aspect-[16/10] border border-slate-800 bg-slate-950/40 rounded-lg overflow-hidden max-h-[80vh]" id="cal-workspace-bounds">
                        <!-- Snapping grid overlay -->
                        <div id="cal-grid-overlay" class="absolute inset-0 pointer-events-none opacity-20"></div>
                        <!-- Canvas SVG connects -->
                        <svg id="cal-svg" class="absolute inset-0 w-full h-full pointer-events-none z-10"></svg>
                        <!-- Draggable circles -->
                        <div id="cal-nodes-root" class="absolute inset-0 z-20"></div>
                    </div>
                </div>
            </div>
            
            <!-- Modal Footer -->
            <div class="h-14 border-t border-slate-900 flex items-center justify-between pt-3 flex-none">
                <button onclick="resetCalibrationToDefault()" class="px-4 py-2 bg-slate-900 border border-slate-800 hover:border-pink-500 text-pink-500 rounded text-xs font-mono font-bold uppercase transition-colors">
                    Reset to default shape
                </button>
                <button onclick="saveCalibrationAndClose()" class="px-5 py-2 bg-gradient-to-r from-cyan-500 to-pink-500 text-slate-950 font-extrabold rounded-lg hover:brightness-110 transition-all font-mono text-xs uppercase shadow-[0_0_15px_rgba(6,182,212,0.3)]">
                    Save Mapping & Close
                </button>
            </div>
        </div>

        <script>
            let devices = [];
            let activeEffect = "";
            let parameterSchema = {};
            let favoritedEffects = [];
            let activeTab = "layout";
            let activeDragDevice = null;
            let dragOffset = { x: 0, y: 0 };
            let activeResizeDevice = null;
            let resizeAnchor = { x: 0, y: 0 };
            
            // Audio hardware options cache
            let audioHardware = { inputs: [], outputs: [] };

            // Plugins state cache
            let plugins = [];
            let selectedConfigPluginId = null;
            
            // GIF Library state cache
            let gifLibrary = [];
            let gifSearchQuery = "";

            // Reordering modal states
            let currentReorderDeviceId = "";
            let currentReorderSequence = [];
            
            // Fine-grained LED Pin calibration state
            let currentCalibratorDeviceId = "";
            let localCalCoords = [];
            let calGridLockEnabled = false;
            let calGridDivisions = 16;
            let activeDragCalNodeIdx = null;
            let activeHighlightNodeIdx = null;
            let calLedSearchQuery = "";
            
            let audioEmulatedState = false;

            async function init() {
                await fetchAudioHardware();
                await fetchConfig();
                await fetchDevices();
                await fetchEffects();
                await fetchPlugins();
                setupWebSocket();
            }

            async function fetchAudioHardware() {
                try {
                    const res = await fetch('/api/audio/devices');
                    audioHardware = await res.json();
                } catch(e) {
                    console.error("Failed fetching audio devices:", e);
                }
            }

            async function fetchConfig() {
                const res = await fetch('/api/config');
                const cfg = await res.json();
                
                // Load global settings panel inputs
                document.getElementById("setting-host").value = cfg.openrgb_host;
                document.getElementById("setting-port").value = cfg.openrgb_port;
                document.getElementById("setting-fps").value = cfg.target_fps;
                document.getElementById("val-target-fps").textContent = cfg.target_fps;
                document.getElementById("active-fps-display").textContent = `Target: ${cfg.target_fps} FPS`;

                // Set canvas and audio parameters
                document.getElementById("setting-canvas-res").value = cfg.canvas_width;
                document.getElementById("val-canvas-res").textContent = `${cfg.canvas_width} px Width (16:10 Ratio)`;
                document.getElementById("setting-noise-gate").value = cfg.audio_noise_gate;
                document.getElementById("val-noise-gate").textContent = cfg.audio_noise_gate;
                
                audioEmulatedState = cfg.audio_emulation;
                updateEmulationToggleUI();

                const audioModeSelect = document.getElementById("setting-audio-mode");
                audioModeSelect.value = cfg.audio_mode || "input";
                populateAudioDevicesDropdown(cfg.audio_mode || "input", cfg.audio_device_id || "default");
            }

            function populateAudioDevicesDropdown(mode, selectedDeviceId) {
                const deviceSelect = document.getElementById("setting-audio-device");
                deviceSelect.innerHTML = "";
                
                // Read from cache depending on target filter category
                const list = mode === "input" ? audioHardware.inputs : audioHardware.outputs;
                list.forEach(dev => {
                    const opt = document.createElement("option");
                    opt.value = dev.id;
                    opt.textContent = dev.name;
                    if (dev.id === selectedDeviceId) {
                        opt.selected = true;
                    }
                    deviceSelect.appendChild(opt);
                });
            }

            function onAudioModeChange(mode) {
                populateAudioDevicesDropdown(mode, null);
            }
            
            function toggleAudioEmulation() {
                audioEmulatedState = !audioEmulatedState;
                updateEmulationToggleUI();
            }
            
            function updateEmulationToggleUI() {
                const btn = document.getElementById("setting-audio-emulation-btn");
                if (audioEmulatedState) {
                    btn.className = "text-cyan-400 text-lg";
                    btn.innerHTML = '<i class="fa-solid fa-toggle-on"></i>';
                } else {
                    btn.className = "text-slate-600 text-lg";
                    btn.innerHTML = '<i class="fa-solid fa-toggle-off"></i>';
                }
            }

            async function fetchDevices() {
                try {
                    const res = await fetch('/api/devices');
                    devices = await res.json();
                    if (activeTab === "layout") renderWorkspaceDevices();
                    if (activeTab === "devices") renderHardwareTab();
                } catch(e) {
                    console.error("Failed fetching hardware layouts: ", e);
                }
            }

            async function fetchEffects() {
                try {
                    const res = await fetch('/api/effects');
                    const data = await res.json();
                    activeEffect = data.active;
                    parameterSchema = data.library;
                    favoritedEffects = data.favorites || [];
                    
                    document.getElementById("active-shader-title").textContent = activeEffect.replace(/([A-Z])/g, ' $1').trim();
                    renderEffectsList();
                    renderEffectParameters(data.params);
                } catch(e) {
                    console.error("Failed loading shader maps: ", e);
                }
            }

            // --- TAB: Plugins Manager ---

            async function fetchPlugins() {
                try {
                    const res = await fetch('/api/plugins');
                    plugins = await res.json();
                    if (activeTab === "plugins") {
                        renderPluginsGrid();
                    }
                } catch(e) {
                    console.error("Failed to load plugins: ", e);
                }
            }

            function renderPluginsGrid() {
                const grid = document.getElementById("plugins-grid");
                grid.innerHTML = "";
                
                plugins.forEach(p => {
                    const activeBorder = p.enabled ? 'border-pink-500 bg-slate-900/60 shadow-[0_0_15px_rgba(236,72,153,0.15)]' : 'border-slate-900 bg-slate-950/40';
                    const card = document.createElement("div");
                    card.className = `glass-panel p-4 rounded-xl border flex flex-col justify-between h-36 relative transition-all ${activeBorder}`;
                    
                    card.innerHTML = `
                        <div>
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold font-mono text-slate-300 tracking-wide uppercase">${p.name}</span>
                                <button onclick="togglePlugin('${p.id}', ${!p.enabled})" class="text-xs ${p.enabled ? 'text-cyan-400' : 'text-slate-600'}">
                                    <i class="fa-solid ${p.enabled ? 'fa-toggle-on':'fa-toggle-off'} text-lg"></i>
                                </button>
                            </div>
                            <p class="text-[10px] text-slate-500 font-mono mt-1 leading-normal">${p.description}</p>
                        </div>
                        <div class="flex justify-between items-center border-t border-slate-900 pt-3">
                            <span class="text-[9px] text-slate-500 font-mono">PLUGIN // ${p.id.toUpperCase()}</span>
                            ${p.enabled ? 
                                `<button onclick="openPluginConfig('${p.id}')" class="px-2.5 py-1 bg-slate-900 border border-slate-800 hover:border-pink-500 text-pink-500 rounded text-[9px] font-mono font-bold uppercase transition-colors">Config</button>` :
                                `<span class="text-[9px] text-slate-600 font-mono">DISABLED</span>`
                            }
                        </div>
                    `;
                    grid.appendChild(card);
                });
            }

            async function togglePlugin(pluginId, enableState) {
                const res = await fetch(`/api/plugins/${pluginId}/toggle`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ enabled: enableState })
                });
                await fetchPlugins();
                if (selectedConfigPluginId === pluginId && !enableState) {
                    document.getElementById("plugin-params-container").innerHTML = `
                        <p class="text-[10px] text-slate-500 font-mono text-center py-4">Click "Config" on an enabled plugin to modify its settings.</p>
                    `;
                    document.getElementById("active-plugin-title").textContent = "Select a Plugin";
                    selectedConfigPluginId = null;
                }
            }

            function openPluginConfig(pluginId) {
                selectedConfigPluginId = pluginId;
                const plug = plugins.find(p => p.id === pluginId);
                if (!plug) return;

                document.getElementById("active-plugin-title").textContent = plug.name;
                const root = document.getElementById("plugin-params-container");
                root.innerHTML = "";

                Object.keys(plug.schema).forEach(key => {
                    const field = plug.schema[key];
                    const val = plug.params[key];
                    const wrap = document.createElement("div");
                    wrap.className = "flex flex-col gap-1.5";

                    if (field.type === "range") {
                        wrap.innerHTML = `
                            <div class="flex justify-between text-[11px] font-mono">
                                <span class="text-slate-400">${field.label}</span>
                                <span class="text-cyan-400 font-bold" id="p-val-${key}">${val}</span>
                            </div>
                            <input type="range" min="${field.min}" max="${field.max}" step="${field.step}" value="${val}"
                                oninput="updatePluginParamValue('${pluginId}', '${key}', this.value)" 
                                class="w-full accent-cyan-500 bg-slate-900 border border-slate-700 rounded-lg appearance-none h-1 cursor-pointer">
                        `;
                    } else if (field.type === "color") {
                        const rgbToHex = (r, g, b) => '#' + [r, g, b].map(x => {
                            const hex = x.toString(16);
                            return hex.length === 1 ? '0' + hex : hex;
                        }).join('');
                        const hexVal = rgbToHex(val[0], val[1], val[2]);

                        wrap.innerHTML = `
                            <div class="flex justify-between items-center text-[11px] font-mono">
                                <span class="text-slate-400">${field.label}</span>
                                <input type="color" value="${hexVal}" onchange="updatePluginColorParam('${pluginId}', '${key}', this.value)" class="bg-transparent border-0 outline-none w-8 h-6 cursor-pointer">
                            </div>
                        `;
                    }
                    root.appendChild(wrap);
                });
            }

            async function updatePluginParamValue(pluginId, key, val) {
                document.getElementById(`p-val-${key}`).textContent = val;
                await fetch(`/api/plugins/${pluginId}/param`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, value: parseFloat(val) })
                });
                await fetchPlugins();
            }

            async function updatePluginColorParam(pluginId, key, hexVal) {
                const hexToRgb = hex => hex.replace(/^#?([a-f\d])([a-f\d])([a-f\d])$/i, (m, r, g, b) => '#' + r + r + g + g + b + b)
                    .substring(1).match(/.{2}/g).map(x => parseInt(x, 16));
                
                const rgb = hexToRgb(hexVal);
                await fetch(`/api/plugins/${pluginId}/param`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, value: rgb })
                });
                await fetchPlugins();
            }
            
            // --- TAB: GIF Library Manager ---
            
            async function fetchGifLibrary() {
                try {
                    const res = await fetch('/api/gifs');
                    gifLibrary = await res.json();
                    renderGifLibraryList();
                } catch(e) {
                    console.error("Failed to load GIF library: ", e);
                }
            }
            
            function onGifSearch(val) {
                gifSearchQuery = val;
                renderGifLibraryList();
            }
            
            function renderGifLibraryList() {
                const list = document.getElementById("gif-library-list");
                list.innerHTML = "";
                
                const filtered = gifLibrary.filter(g => g.name.toLowerCase().includes(gifSearchQuery.toLowerCase()));
                filtered.forEach(g => {
                    const activeBorder = g.active ? 'border-pink-500 bg-slate-900/60 shadow-[0_0_15px_rgba(236,72,153,0.1)]' : 'border-slate-800 bg-slate-950/40';
                    const el = document.createElement("div");
                    el.className = `p-2 rounded border flex items-center justify-between gap-2 text-[10px] font-mono transition-all ${activeBorder}`;
                    
                    el.innerHTML = `
                        <div class="flex-1 overflow-hidden">
                            <span class="text-slate-300 font-bold block truncate cursor-pointer" onclick="selectGifAsset('${g.id}')">${g.name}</span>
                            <span class="text-[8px] text-slate-500 block truncate">${g.id}</span>
                        </div>
                        <div class="flex gap-2 text-slate-400">
                            <button onclick="renameGifPrompt('${g.id}', '${g.name}')" title="Rename"><i class="fa-solid fa-edit hover:text-cyan-400"></i></button>
                            ${g.id !== 'target.gif' ? 
                                `<button onclick="deleteGifAsset('${g.id}')" title="Delete"><i class="fa-solid fa-trash hover:text-pink-500"></i></button>` : ''
                            }
                        </div>
                    `;
                    list.appendChild(el);
                });
            }
            
            async function selectGifAsset(id) {
                const res = await fetch(`/api/gifs/${id}/select`, { method: "POST" });
                const data = await res.json();
                if (data.status === "ok") {
                    await fetchGifLibrary();
                    await fetchConfig();
                }
            }
            
            async function renameGifPrompt(id, currentName) {
                const newName = prompt(`Enter a custom display label for ${id}:`, currentName);
                if (newName && newName.trim() !== "") {
                    await fetch(`/api/gifs/${id}/rename`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ name: newName.trim() })
                    });
                    await fetchGifLibrary();
                }
            }
            
            async function deleteGifAsset(id) {
                if (confirm(`Are you sure you want to permanently delete ${id}?`)) {
                    await fetch(`/api/gifs/${id}`, { method: "DELETE" });
                    await fetchGifLibrary();
                }
            }

            // --- TAB: Navigation Controls ---

            function switchTab(tabId) {
                activeTab = tabId;
                document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
                document.getElementById(`tab-btn-${tabId}`).classList.add('active');

                document.getElementById('tab-view-layout').classList.add('hidden');
                document.getElementById('tab-view-shaders').classList.add('hidden');
                document.getElementById('tab-view-plugins').classList.add('hidden');
                document.getElementById('tab-view-devices').classList.add('hidden');
                document.getElementById('tab-view-settings').classList.add('hidden');
                
                document.getElementById(`tab-view-${tabId}`).classList.remove('hidden');

                if (tabId === "layout") renderWorkspaceDevices();
                if (tabId === "plugins") renderPluginsGrid();
                if (tabId === "devices") renderHardwareTab();
                if (tabId === "shaders") {
                    fetchGifLibrary();
                    const panel = document.getElementById("shader-gif-panel");
                    if (activeEffect === "GifPlayer") panel.classList.remove("hidden");
                    else panel.classList.add("hidden");
                }
            }

            // --- TAB 1: Draggable Workspace Layout Viewport ---

            function toggleLayoutCalibratorMode(mode) {
                calibratorMode = mode;
                const boundsRoot = document.getElementById("workspace-elements-root");
                const nodesRoot = document.getElementById("workspace-nodes-root");
                const svg = document.getElementById("link-svg");

                if (mode === "nodes") {
                    boundsRoot.classList.add("hidden");
                    nodesRoot.classList.remove("hidden");
                    svg.classList.remove("hidden");
                    renderWorkspaceNodesCalibrator();
                } else {
                    boundsRoot.classList.remove("hidden");
                    nodesRoot.classList.add("hidden");
                    svg.classList.add("hidden");
                    document.getElementById("layout-node-hud").classList.add("hidden");
                    renderWorkspaceDevices();
                }
            }

            function renderWorkspaceDevices() {
                const root = document.getElementById("workspace-elements-root");
                root.innerHTML = "";

                devices.forEach(dev => {
                    if (!dev.enabled) return;

                    const block = document.createElement("div");
                    block.className = "absolute border border-slate-700/80 rounded bg-slate-900/40 cursor-grab active:cursor-grabbing hover:border-pink-500 group transition-all z-20 overflow-hidden shadow-2xl";
                    block.style.left = `${dev.x * 100}%`;
                    block.style.top = `${dev.y * 100}%`;
                    block.style.width = `${dev.width * 100}%`;
                    block.style.height = `${dev.height * 100}%`;

                    // Generate distinct device appearance outlines depending on active profile
                    let innerHTML = "";
                    if (dev.form_type === "KEYBOARD") {
                        innerHTML = `<div class="grid grid-cols-[repeat(15,minmax(0,1fr))] grid-rows-[repeat(6,minmax(0,1fr))] h-[86%] w-full p-2 gap-1 opacity-70 bg-slate-950/60 rounded">`;
                        for (let i = 0; i < dev.led_count; i++) {
                            const rgb = dev.demo_colors ? dev.demo_colors[i] : [236,72,153];
                            innerHTML += `<div class="rounded bg-slate-900 border border-slate-800 flex items-center justify-center shadow-inner" style="box-shadow: 0 0 5px rgba(${rgb[0]},${rgb[1]},${rgb[2]},0.65)">
                                <div class="w-1.5 h-1.5 rounded-full" style="background-color: rgb(${rgb[0]},${rgb[1]},${rgb[2]})"></div>
                            </div>`;
                        }
                        innerHTML += `</div>`;
                    } else if (dev.form_type === "RAM") {
                        innerHTML = `<div class="flex flex-col h-[86%] w-full justify-around items-center p-2 border-l-4 border-cyan-400 bg-slate-950/80 rounded shadow-inner">`;
                        for (let i = 0; i < dev.led_count; i++) {
                            const rgb = dev.demo_colors ? dev.demo_colors[i] : [6,182,212];
                            innerHTML += `<div class="w-3 h-3 rounded shadow" style="background-color: rgb(${rgb[0]},${rgb[1]},${rgb[2]}); box-shadow: 0 0 8px rgb(${rgb[0]},${rgb[1]},${rgb[2]})"></div>`;
                        }
                        innerHTML += `</div>`;
                    } else if (dev.form_type.startsWith("STRIMER")) {
                        const numLines = dev.form_type === "STRIMER_24PIN" ? 12 : 8;
                        innerHTML = `<div class="flex h-[86%] w-full justify-around p-1.5 bg-slate-950/90 rounded border border-slate-800/60 overflow-hidden shadow-inner">`;
                        for (let l = 0; l < numLines; l++) {
                            const ledsPerLine = Math.floor(dev.led_count / numLines);
                            innerHTML += `<div class="flex flex-col h-full justify-around items-center flex-1 border-r border-slate-800/10 last:border-r-0">`;
                            for (let i = 0; i < ledsPerLine; i++) {
                                const ledIdx = l * ledsPerLine + i;
                                const rgb = (dev.demo_colors && dev.demo_colors[ledIdx]) ? dev.demo_colors[ledIdx] : [6, 182, 212];
                                innerHTML += `<div class="w-1.5 h-1.5 rounded-full" style="background-color: rgb(${rgb[0]},${rgb[1]},${rgb[2]}); box-shadow: 0 0 6px rgb(${rgb[0]},${rgb[1]},${rgb[2]})"></div>`;
                            }
                            innerHTML += `</div>`;
                        }
                        innerHTML += `</div>`;
                    } else {
                        innerHTML = `<div class="flex h-[86%] w-full justify-around items-center p-2 bg-slate-950/40 rounded border border-slate-900/60 shadow-inner">`;
                        for (let i = 0; i < dev.led_count; i++) {
                            const rgb = dev.demo_colors ? dev.demo_colors[i] : [34,197,94];
                            innerHTML += `<div class="w-2 h-2 rounded-full" style="background-color: rgb(${rgb[0]},${rgb[1]},${rgb[2]})"></div>`;
                        }
                        innerHTML += `</div>`;
                    }

                    innerHTML += `
                        <div class="absolute inset-x-0 bottom-0 bg-slate-950/90 border-t border-slate-900 px-1.5 py-0.5 text-[8px] font-mono tracking-wider text-slate-400 select-none pointer-events-none flex justify-between items-center z-10">
                            <span>${dev.name}</span>
                            <span>[${dev.led_count} L]</span>
                        </div>
                        <div class="absolute bottom-0 right-0 h-4 w-4 cursor-se-resize flex items-end justify-end p-0.5 z-30 group-hover:bg-cyan-500/30 transition-colors" onmousedown="startResize(event, '${dev.id}')">
                            <i class="fa-solid fa-arrows-alt text-[8px] text-cyan-400"></i>
                        </div>
                    `;

                    block.innerHTML = innerHTML;
                    block.onmousedown = (e) => {
                        if (e.target.closest('.cursor-se-resize')) return;
                        startDrag(e, dev.id);
                    };
                    root.appendChild(block);
                });
            }

            // --- Drag Operations ---

            function startDrag(e, devId) {
                e.preventDefault();
                const dev = devices.find(d => d.id === devId);
                if (!dev) return;

                const parent = document.getElementById("canvas-workspace").getBoundingClientRect();
                activeDragDevice = dev;
                
                dragOffset.x = (e.clientX - parent.left) / parent.width - dev.x;
                dragOffset.y = (e.clientY - parent.top) / parent.height - dev.y;

                document.onmousemove = moveDrag;
                document.onmouseup = stopDrag;
            }

            function moveDrag(e) {
                if (!activeDragDevice) return;
                const parent = document.getElementById("canvas-workspace").getBoundingClientRect();

                let x = (e.clientX - parent.left) / parent.width - dragOffset.x;
                let y = (e.clientY - parent.top) / parent.height - dragOffset.y;

                x = Math.max(0, Math.min(1 - activeDragDevice.width, x));
                y = Math.max(0, Math.min(1 - activeDragDevice.height, y));

                activeDragDevice.x = x;
                activeDragDevice.y = y;
                renderWorkspaceDevices();
            }

            async function stopDrag() {
                if (activeDragDevice) {
                    await fetch(`/api/devices/${activeDragDevice.id}/bounds`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            x: activeDragDevice.x,
                            y: activeDragDevice.y,
                            width: activeDragDevice.width,
                            height: activeDragDevice.height,
                            form_type: activeDragDevice.form_type,
                            active_profile: activeDragDevice.active_profile,
                            custom_profiles: activeDragDevice.custom_profiles
                        })
                    });
                }
                activeDragDevice = null;
                document.onmousemove = null;
                document.onmouseup = null;
            }

            // --- Resize Operations ---

            function startResize(e, devId) {
                e.preventDefault();
                e.stopPropagation();
                const dev = devices.find(d => d.id === devId);
                if (!dev) return;

                activeResizeDevice = dev;
                document.onmousemove = moveResize;
                document.onmouseup = stopResize;
            }

            function moveResize(e) {
                if (!activeResizeDevice) return;
                const parent = document.getElementById("canvas-workspace").getBoundingClientRect();

                let width = ((e.clientX - parent.left) / parent.width) - activeResizeDevice.x;
                let height = ((e.clientY - parent.top) / parent.height) - activeResizeDevice.y;

                width = Math.max(0.05, Math.min(1.0 - activeResizeDevice.x, width));
                height = Math.max(0.05, Math.min(1.0 - activeResizeDevice.y, height));

                activeResizeDevice.width = width;
                activeResizeDevice.height = height;
                renderWorkspaceDevices();
            }

            async function stopResize() {
                if (activeResizeDevice) {
                    await fetch(`/api/devices/${activeResizeDevice.id}/bounds`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            x: activeResizeDevice.x,
                            y: activeResizeDevice.y,
                            width: activeResizeDevice.width,
                            height: activeResizeDevice.height,
                            form_type: activeResizeDevice.form_type,
                            active_profile: activeResizeDevice.active_profile,
                            custom_profiles: activeResizeDevice.custom_profiles
                        })
                    });
                }
                activeResizeDevice = null;
                document.onmousemove = null;
                document.onmouseup = null;
            }

            // --- TAB 2: Effects Selection & Favorites Manager ---

            function renderEffectsList() {
                const grid = document.getElementById("effects-grid");
                grid.innerHTML = "";
                const search = document.getElementById("effect-search").value.toLowerCase();

                const sortedKeys = Object.keys(parameterSchema).sort((a, b) => {
                    const favA = favoritedEffects.includes(a) ? 1 : 0;
                    const favB = favoritedEffects.includes(b) ? 1 : 0;
                    return favB - favA || a.localeCompare(b);
                });

                sortedKeys.forEach(key => {
                    if (search && !key.toLowerCase().includes(search)) return;

                    const isFav = favoritedEffects.includes(key);
                    const isActive = activeEffect === key;
                    const activeBorder = isActive ? 'border-pink-500 bg-slate-900/60 shadow-[0_0_15px_rgba(236,72,153,0.15)]' : 'border-slate-900 hover:border-slate-700 bg-slate-950/40';

                    const card = document.createElement("div");
                    card.className = `glass-panel p-4 rounded-xl border flex flex-col justify-between h-36 relative transition-all ${activeBorder}`;
                    
                    card.innerHTML = `
                        <div>
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold font-mono text-slate-300 tracking-wide uppercase">${key.replace(/([A-Z])/g, ' $1').trim()}</span>
                                <button onclick="toggleFavorite(event, '${key}')" class="text-xs text-slate-500 hover:text-pink-500 transition-all">
                                    <i class="${isFav ? 'fa-solid text-pink-500':'fa-regular'} fa-heart"></i>
                                </button>
                            </div>
                            <p class="text-[10px] text-slate-500 font-mono mt-1 leading-normal">
                                Visual effect mapping module. Supports real-time coordinate transformations.
                            </p>
                        </div>
                        <div class="flex justify-between items-center border-t border-slate-900 pt-3">
                            <span class="text-[9px] text-slate-500 font-mono">Effect ID // ${key.toUpperCase()}</span>
                            ${isActive ? 
                                `<span class="px-2 py-0.5 bg-pink-500/10 border border-pink-500/20 text-pink-400 rounded text-[9px] font-mono">ACTIVE</span>` :
                                `<button onclick="changeEffect('${key}')" class="px-2.5 py-1 bg-slate-900 border border-slate-800 hover:border-cyan-500 text-cyan-400 rounded text-[9px] font-mono font-bold uppercase transition-colors">Select</button>`
                            }
                        </div>
                    `;
                    grid.appendChild(card);
                });
            }

            async function toggleFavorite(e, effectName) {
                e.stopPropagation();
                if (favoritedEffects.includes(effectName)) {
                    favoritedEffects = favoritedEffects.filter(x => x !== effectName);
                } else {
                    favoritedEffects.push(effectName);
                }
                
                await fetch('/api/effects/favorites', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ favorites: favoritedEffects })
                });

                renderEffectsList();
            }

            function renderEffectParameters(currentValues) {
                const root = document.getElementById("params-container");
                root.innerHTML = "";
                
                // Expose uploader conditionally [1]
                const uploader = document.getElementById("effect-upload-container");
                if (activeEffect === "GifPlayer") {
                    uploader.classList.remove("hidden");
                } else {
                    uploader.classList.add("hidden");
                }

                const schema = parameterSchema[activeEffect];
                if (!schema) return;

                Object.keys(schema).forEach(key => {
                    if (key.startsWith("_")) return; // Hide internal parameters
                    const field = schema[key];
                    const val = currentValues[key];
                    if (val === undefined) return;
                    
                    const wrap = document.createElement("div");
                    wrap.className = "flex flex-col gap-1.5";

                    if (field.type === "range") {
                        wrap.innerHTML = `
                            <div class="flex justify-between text-[11px] font-mono">
                                <span class="text-slate-400">${field.label}</span>
                                <span class="text-cyan-400 font-bold" id="val-${key}">${val}</span>
                            </div>
                            <input type="range" min="${field.min}" max="${field.max}" step="${field.step}" value="${val}"
                                oninput="updateParamValue('${key}', this.value)" 
                                class="w-full accent-cyan-500 bg-slate-900 border border-slate-700 rounded-lg appearance-none h-1 cursor-pointer">
                        `;
                    } else if (field.type === "color") {
                        const rgbToHex = (r, g, b) => '#' + [r, g, b].map(x => {
                            const hex = x.toString(16);
                            return hex.length === 1 ? '0' + hex : hex;
                        }).join('');
                        const hexVal = rgbToHex(val[0], val[1], val[2]);

                        wrap.innerHTML = `
                            <div class="flex justify-between items-center text-[11px] font-mono">
                                <span class="text-slate-400">${field.label}</span>
                                <input type="color" value="${hexVal}" onchange="updateColorParam('${key}', this.value)" class="bg-transparent border-0 outline-none w-8 h-6 cursor-pointer">
                            </div>
                        `;
                    } else if (field.type === "toggle") {
                        wrap.innerHTML = `
                            <div class="flex justify-between items-center text-[11px] font-mono">
                                <span class="text-slate-400">${field.label}</span>
                                <button onclick="updateToggleParam('${key}', ${!val})" class="text-cyan-400 text-lg">
                                    <i class="fa-solid ${val ? 'fa-toggle-on':'fa-toggle-off'}"></i>
                                </button>
                            </div>
                        `;
                    }
                    root.appendChild(wrap);
                });
            }

            async function updateParamValue(key, val) {
                document.getElementById(`val-${key}`).textContent = val;
                await fetch('/api/effects/param', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, value: parseFloat(val) })
                });
            }

            async function updateColorParam(key, hexVal) {
                const hexToRgb = hex => hex.replace(/^#?([a-f\d])([a-f\d])([a-f\d])$/i, (m, r, g, b) => '#' + r + r + g + g + b + b)
                    .substring(1).match(/.{2}/g).map(x => parseInt(x, 16));
                
                const rgb = hexToRgb(hexVal);
                await fetch('/api/effects/param', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, value: rgb })
                });
            }
            
            async function updateToggleParam(key, boolVal) {
                await fetch('/api/effects/param', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, value: boolVal })
                });
                await fetchEffects(); // reload form
            }

            async function changeEffect(effName) {
                const res = await fetch('/api/effects/select', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ effect_name: effName })
                });
                const data = await res.json();
                activeEffect = data.active;
                document.getElementById("active-shader-title").textContent = activeEffect.replace(/([A-Z])/g, ' $1').trim();
                
                const panel = document.getElementById("shader-gif-panel");
                if (activeEffect === "GifPlayer") panel.classList.remove("hidden");
                else panel.classList.add("hidden");
                
                renderEffectsList();
                renderEffectParameters(data.params);
            }
            
            // --- Custom drag-and-drop GIF upload parsing logic --- [1]
            
            async function handleGifSelect(input) {
                if (input.files && input.files[0]) {
                    await uploadGifToServer(input.files[0]);
                }
            }
            
            async function handleGifDrop(e) {
                e.preventDefault();
                if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                    await uploadGifToServer(e.dataTransfer.files[0]);
                }
            }
            
            async function uploadGifToServer(file) {
                try {
                    // Send raw bytes directly [1]
                    const res = await fetch('/api/upload/gif', {
                        method: 'POST',
                        headers: { 'Content-Type': 'image/gif' },
                        body: file
                    });
                    const data = await res.json();
                    if (data.status === "ok") {
                        alert("Custom calibration animation loaded successfully!"); [1]
                        await fetchGifLibrary();
                    }
                } catch(e) {
                    console.error("Failed to upload animation asset:", e);
                }
            }

            // --- TAB 3: Dynamic Plugins Manager ---

            async function fetchPlugins() {
                try {
                    const res = await fetch('/api/plugins');
                    plugins = await res.json();
                    if (activeTab === "plugins") {
                        renderPluginsGrid();
                    }
                } catch(e) {
                    console.error("Failed to load plugins: ", e);
                }
            }

            function renderPluginsGrid() {
                const grid = document.getElementById("plugins-grid");
                grid.innerHTML = "";
                
                plugins.forEach(p => {
                    const activeBorder = p.enabled ? 'border-pink-500 bg-slate-900/60 shadow-[0_0_15px_rgba(236,72,153,0.15)]' : 'border-slate-900 bg-slate-950/40';
                    const card = document.createElement("div");
                    card.className = `glass-panel p-4 rounded-xl border flex flex-col justify-between h-36 relative transition-all ${activeBorder}`;
                    
                    card.innerHTML = `
                        <div>
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold font-mono text-slate-300 tracking-wide uppercase">${p.name}</span>
                                <button onclick="togglePlugin('${p.id}', ${!p.enabled})" class="text-xs ${p.enabled ? 'text-cyan-400' : 'text-slate-600'}">
                                    <i class="fa-solid ${p.enabled ? 'fa-toggle-on':'fa-toggle-off'} text-lg"></i>
                                </button>
                            </div>
                            <p class="text-[10px] text-slate-500 font-mono mt-1 leading-normal">${p.description}</p>
                        </div>
                        <div class="flex justify-between items-center border-t border-slate-900 pt-3">
                            <span class="text-[9px] text-slate-500 font-mono">PLUGIN // ${p.id.toUpperCase()}</span>
                            ${p.enabled ? 
                                `<button onclick="openPluginConfig('${p.id}')" class="px-2.5 py-1 bg-slate-900 border border-slate-800 hover:border-pink-500 text-pink-500 rounded text-[9px] font-mono font-bold uppercase transition-colors">Config</button>` :
                                `<span class="text-[9px] text-slate-600 font-mono">DISABLED</span>`
                            }
                        </div>
                    `;
                    grid.appendChild(card);
                });
            }

            async function togglePlugin(pluginId, enableState) {
                const res = await fetch(`/api/plugins/${pluginId}/toggle`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ enabled: enableState })
                });
                await fetchPlugins();
                if (selectedConfigPluginId === pluginId && !enableState) {
                    document.getElementById("plugin-params-container").innerHTML = `
                        <p class="text-[10px] text-slate-500 font-mono text-center py-4">Click "Config" on an enabled plugin to modify its settings.</p>
                    `;
                    document.getElementById("active-plugin-title").textContent = "Select a Plugin";
                    selectedConfigPluginId = null;
                }
            }

            function openPluginConfig(pluginId) {
                selectedConfigPluginId = pluginId;
                const plug = plugins.find(p => p.id === pluginId);
                if (!plug) return;

                document.getElementById("active-plugin-title").textContent = plug.name;
                const root = document.getElementById("plugin-params-container");
                root.innerHTML = "";

                Object.keys(plug.schema).forEach(key => {
                    const field = plug.schema[key];
                    const val = plug.params[key];
                    const wrap = document.createElement("div");
                    wrap.className = "flex flex-col gap-1.5";

                    if (field.type === "range") {
                        wrap.innerHTML = `
                            <div class="flex justify-between text-[11px] font-mono">
                                <span class="text-slate-400">${field.label}</span>
                                <span class="text-cyan-400 font-bold" id="p-val-${key}">${val}</span>
                            </div>
                            <input type="range" min="${field.min}" max="${field.max}" step="${field.step}" value="${val}"
                                oninput="updatePluginParamValue('${pluginId}', '${key}', this.value)" 
                                class="w-full accent-cyan-500 bg-slate-900 border border-slate-700 rounded-lg appearance-none h-1 cursor-pointer">
                        `;
                    } else if (field.type === "color") {
                        const rgbToHex = (r, g, b) => '#' + [r, g, b].map(x => {
                            const hex = x.toString(16);
                            return hex.length === 1 ? '0' + hex : hex;
                        }).join('');
                        const hexVal = rgbToHex(val[0], val[1], val[2]);

                        wrap.innerHTML = `
                            <div class="flex justify-between items-center text-[11px] font-mono">
                                <span class="text-slate-400">${field.label}</span>
                                <input type="color" value="${hexVal}" onchange="updatePluginColorParam('${pluginId}', '${key}', this.value)" class="bg-transparent border-0 outline-none w-8 h-6 cursor-pointer">
                            </div>
                        `;
                    }
                    root.appendChild(wrap);
                });
            }

            async function updatePluginParamValue(pluginId, key, val) {
                document.getElementById(`p-val-${key}`).textContent = val;
                await fetch(`/api/plugins/${pluginId}/param`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, value: parseFloat(val) })
                });
                await fetchPlugins();
            }

            async function updatePluginColorParam(pluginId, key, hexVal) {
                const hexToRgb = hex => hex.replace(/^#?([a-f\d])([a-f\d])([a-f\d])$/i, (m, r, g, b) => '#' + r + r + g + g + b + b)
                    .substring(1).match(/.{2}/g).map(x => parseInt(x, 16));
                
                const rgb = hexToRgb(hexVal);
                await fetch(`/api/plugins/${pluginId}/param`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, value: rgb })
                });
                await fetchPlugins();
            }

            // --- TAB 4: Hardware Settings tab ---

            function renderHardwareTab() {
                const root = document.getElementById("hardware-cards-container");
                root.innerHTML = "";

                devices.forEach(dev => {
                    const el = document.createElement("div");
                    el.className = "glass-panel p-4 rounded-xl border border-slate-900 flex flex-col justify-between gap-4";
                    
                    // Generate list of dropdown select items dynamically (including both standard procedurals and named profiles) [1]
                    let shapeOptions = `
                        <option value="procedural" ${dev.active_profile === 'procedural' ? 'selected':''}>Procedural Auto Shape</option>
                    `;
                    Object.keys(dev.custom_profiles).forEach(profName => {
                        shapeOptions += `<option value="profile:${profName}" ${dev.active_profile === 'profile:'+profName ? 'selected':''}>Custom: ${profName}</option>`;
                    });

                    el.innerHTML = `
                        <div class="flex items-center justify-between">
                            <div class="flex items-center gap-3">
                                <div class="p-2 bg-slate-950 border border-slate-800 text-cyan-400 rounded-lg">
                                    <i class="fa-solid ${dev.form_type.startsWith('KEYBOARD') ? 'fa-keyboard' : (dev.form_type.startsWith('RAM') ? 'fa-memory' : (dev.form_type.startsWith('STRIMER') ? 'fa-lines-leaning':'fa-fan'))}"></i>
                                </div>
                                <div>
                                    <h4 class="text-xs font-bold text-slate-300 font-mono tracking-tight">${dev.name}</h4>
                                    <p class="text-[10px] text-slate-500 font-mono">Form Factor: ${dev.form_type}</p>
                                </div>
                            </div>
                            <button onclick="toggleDevice('${dev.id}')" class="text-xs ${dev.enabled ? 'text-cyan-400':'text-slate-600'}">
                                <i class="fa-solid ${dev.enabled ? 'fa-toggle-on':'fa-toggle-off'} text-xl"></i>
                            </button>
                        </div>

                        <div class="flex flex-col gap-2 border-t border-slate-900 pt-3">
                            <span class="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Spatial Auto-Ordering</span>
                            <div class="grid grid-cols-3 gap-2 font-mono text-[10px]">
                                <button onclick="autoOrderDevice('${dev.id}', 'left_to_right')" class="py-1 bg-slate-900 border border-slate-800 rounded hover:border-cyan-500/40 text-slate-300">Left-Right</button>
                                <button onclick="autoOrderDevice('${dev.id}', 'top_to_bottom')" class="py-1 bg-slate-900 border border-slate-800 rounded hover:border-cyan-500/40 text-slate-300">Top-Bottom</button>
                                <button onclick="autoOrderDevice('${dev.id}', 'clockwise')" class="py-1 bg-slate-900 border border-slate-800 rounded hover:border-cyan-500/40 text-slate-300">Radial</button>
                            </div>
                        </div>

                        <!-- Dynamic Form Profile Switcher -->
                        <div class="flex flex-col gap-1.5 border-t border-slate-900 pt-2 text-[10px] font-mono">
                            <label class="text-slate-400">Transform Form profile Appearance</label>
                            <select onchange="updateDeviceProfile('${dev.id}', this.value)" class="w-full bg-slate-900 border border-slate-800 rounded py-1 px-2 outline-none text-slate-300">
                                <option value="KEYBOARD" ${dev.form_type === 'KEYBOARD' ? 'selected':''}>Keyboard</option>
                                <option value="RAM" ${dev.form_type === 'RAM' ? 'selected':''}>RAM Module</option>
                                <option value="STRIMER_8PIN" ${dev.form_type === 'STRIMER_8PIN' ? 'selected':''}>Lian Li Strimer (8-Pin Ribbon)</option>
                                <option value="STRIMER_24PIN" ${dev.form_type === 'STRIMER_24PIN' ? 'selected':''}>Lian Li Strimer (24-Pin Ribbon)</option>
                                <option value="STRIP" ${dev.form_type === 'STRIP' ? 'selected':''}>Linear LED Strip</option>
                                <option value="FAN" ${dev.form_type === 'FAN' ? 'selected':''}>Cooling Fan Ring</option>
                            </select>
                        </div>
                        
                        <!-- Named Profile Database Swapper [1] -->
                        <div class="flex flex-col gap-1.5 border-t border-slate-900/60 pt-2 text-[10px] font-mono">
                            <label class="text-slate-400">Current Mapping Coordinates Array</label>
                            <div class="flex gap-2">
                                <select onchange="onSelectNamedProfile('${dev.id}', this.value)" class="flex-1 bg-slate-900 border border-slate-800 rounded py-1 px-2 outline-none text-slate-300 font-mono text-[9px]">
                                    ${shapeOptions}
                                </select>
                                ${dev.active_profile.startsWith('profile:') ? 
                                    `<button onclick="deleteNamedProfilePrompt('${dev.id}', '${dev.active_profile.replace('profile:', '')}')" class="px-2 bg-slate-950 border border-slate-800 hover:border-pink-500 text-pink-500 rounded text-[10px]"><i class="fa-solid fa-trash"></i></button>` : ''
                                }
                            </div>
                        </div>

                        <div class="flex items-center justify-between text-[10px] font-mono border-t border-slate-900 pt-3">
                            <span class="text-slate-500">Total Indexing Count: ${dev.led_count}</span>
                            <button onclick="openCalibrationModal('${dev.id}')" class="px-3 py-1 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded hover:bg-cyan-500 hover:text-slate-950 font-bold transition-all">
                                <i class="fa-solid fa-arrows-spin mr-1"></i> manual Pin mapping
                            </button>
                        </div>
                    `;
                    root.appendChild(el);
                });
            }

            async function updateDeviceProfile(id, formType) {
                const dev = devices.find(d => d.id === id);
                if (!dev) return;
                dev.form_type = formType;
                
                await fetch(`/api/devices/${id}/bounds`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        x: dev.x,
                        y: dev.y,
                        width: dev.width,
                        height: dev.height,
                        form_type: formType,
                        active_profile: dev.active_profile,
                        custom_profiles: dev.custom_profiles
                    })
                });
                await fetchDevices();
            }
            
            async function onSelectNamedProfile(deviceId, targetValue) {
                let apiPath = `/api/devices/${deviceId}/profile/${targetValue.replace('profile:', '')}/select`;
                if (targetValue === "procedural") {
                    apiPath = `/api/devices/${deviceId}/profile/procedural/select`;
                }
                
                await fetch(apiPath, { method: "POST" });
                await fetchDevices();
            }
            
            async function deleteNamedProfilePrompt(deviceId, profileName) {
                if (confirm(`Are you sure you want to delete custom profile "${profileName}"?`)) {
                    await fetch(`/api/devices/${deviceId}/profile/${profileName}`, { method: "DELETE" });
                    await fetchDevices();
                }
            }

            async function toggleDevice(id) {
                const res = await fetch(`/api/devices/${id}/toggle`, { method: "POST" });
                const data = await res.json();
                const dev = devices.find(d => d.id === id);
                if (dev) dev.enabled = data.enabled;
                renderHardwareTab();
            }

            async function autoOrderDevice(deviceId, mode) {
                const res = await fetch(`/api/devices/${deviceId}/auto_order?mode=${mode}`, { method: "POST" });
                const data = await res.json();
                const dev = devices.find(d => d.id === deviceId);
                if (dev) dev.led_order = data.led_order;
                alert(`Calculated spatial ordering sequence: [${data.led_order.slice(0, 5)}...]`);
            }

            // --- TAB 5: Engine Settings Configuration ---

            async function saveGlobalSettings() {
                const host = document.getElementById("setting-host").value;
                const port = parseInt(document.getElementById("setting-port").value);
                const fps = parseInt(document.getElementById("setting-fps").value);
                const audioMode = document.getElementById("setting-audio-mode").value;
                const audioDeviceId = document.getElementById("setting-audio-device").value;
                const canvasRes = parseInt(document.getElementById("setting-canvas-res").value);
                const noiseGate = parseFloat(document.getElementById("setting-noise-gate").value);

                await fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        openrgb_host: host,
                        openrgb_port: port,
                        target_fps: fps,
                        canvas_width: canvasRes,
                        audio_mode: audioMode,
                        audio_device_id: audioDeviceId,
                        audio_emulation: audioEmulatedState,
                        audio_noise_gate: noiseGate
                    })
                });

                document.getElementById("active-fps-display").textContent = `Target: ${fps} FPS`;
                alert("Core server configuration modified.");
                await fetchAudioHardware();
                await fetchConfig();
                await fetchDevices();
            }

            // --- Manual Pin mapping Modal Logic ---

            async function highlightPhysicalLed(deviceId, ledIndex) {
                await fetch(`/api/devices/${deviceId}/highlight/${ledIndex}`, { method: "POST" });
            }

            async function clearDeviceHighlight() {
                await fetch('/api/devices/highlight/clear', { method: "POST" });
            }

            // --- NEW: Local Calibration Modal Studio Engine [1] ---

            function openCalibrationModal(deviceId) {
                currentCalibratorDeviceId = deviceId;
                const dev = devices.find(d => d.id === deviceId);
                if (!dev) return;

                document.getElementById("cal-modal-title").textContent = dev.name;
                
                // Read coordinate array. Check if active profile is custom [1]
                if (dev.active_profile.startsWith("profile:") && dev.custom_profiles[dev.active_profile.replace("profile:", "")]) {
                    localCalCoords = JSON.parse(JSON.stringify(dev.custom_profiles[dev.active_profile.replace("profile:", "")]));
                } else {
                    localCalCoords = JSON.parse(JSON.stringify(dev.local_coords));
                }

                // Initialize snap interface variables
                calGridLockEnabled = false;
                calGridDivisions = 16;
                document.getElementById("cal-setting-divisions").value = 16;
                document.getElementById("cal-val-divisions").textContent = 16;
                updateCalGridLockUI();

                renderCalLedList();
                renderCalWorkspace();

                document.getElementById("calibration-modal").style.display = "flex";
            }

            function toggleCalibrationGridLock() {
                calGridLockEnabled = !calGridLockEnabled;
                updateCalGridLockUI();
                renderCalWorkspace();
            }

            function updateCalGridLockUI() {
                const btn = document.getElementById("cal-grid-lock-btn");
                if (calGridLockEnabled) {
                    btn.className = "text-cyan-400 text-lg";
                    btn.innerHTML = '<i class="fa-solid fa-toggle-on"></i>';
                } else {
                    btn.className = "text-slate-600 text-lg";
                    btn.innerHTML = '<i class="fa-solid fa-toggle-off"></i>';
                }
            }

            function onCalDivisionsChange(val) {
                calGridDivisions = parseInt(val);
                document.getElementById("cal-val-divisions").textContent = val;
                renderCalWorkspace();
            }

            function onCalLedSearch(val) {
                calLedSearchQuery = val;
                renderCalLedList();
            }

            function renderCalLedList() {
                const container = document.getElementById("cal-led-list-container");
                container.innerHTML = "";

                localCalCoords.forEach((coord, i) => {
                    if (calLedSearchQuery && !`led ${i}`.includes(calLedSearchQuery.toLowerCase())) return;

                    const activeBorder = activeHighlightNodeIdx === i ? 'border-cyan-500 bg-slate-900' : 'border-slate-900 bg-slate-950/40';
                    const item = document.createElement("div");
                    item.className = `p-2 rounded border flex flex-col gap-1.5 font-mono text-[9px] transition-all ${activeBorder}`;
                    
                    item.innerHTML = `
                        <div class="flex justify-between items-center text-slate-400">
                            <span class="font-bold text-slate-300">LED #${i}</span>
                            <span class="text-[7px]">PIN ADDRESS</span>
                        </div>
                        <div class="grid grid-cols-2 gap-2 text-slate-200">
                            <div class="flex items-center gap-1">
                                <span class="text-slate-500">X:</span>
                                <input type="number" step="0.001" min="0" max="1" value="${coord[0].toFixed(3)}" 
                                    onfocus="focusCalLedNode(${i})" 
                                    onchange="updateCalNodeCoordsFromInput(${i}, 'x', this.value)"
                                    class="w-full bg-slate-950 border border-slate-800 rounded px-1.5 py-0.5 text-cyan-400 outline-none focus:border-cyan-500">
                            </div>
                            <div class="flex items-center gap-1">
                                <span class="text-slate-500">Y:</span>
                                <input type="number" step="0.001" min="0" max="1" value="${coord[1].toFixed(3)}" 
                                    onfocus="focusCalLedNode(${i})" 
                                    onchange="updateCalNodeCoordsFromInput(${i}, 'y', this.value)"
                                    class="w-full bg-slate-950 border border-slate-800 rounded px-1.5 py-0.5 text-cyan-400 outline-none focus:border-cyan-500">
                            </div>
                        </div>
                    `;
                    container.appendChild(item);
                });
            }

            function focusCalLedNode(ledIndex) {
                activeHighlightNodeIdx = ledIndex;
                highlightPhysicalLed(currentCalibratorDeviceId, ledIndex);
                renderCalWorkspace();
            }

            // Snapping slider limit expanded to 100
            function updateCalNodeCoordsFromInput(ledIndex, axis, val) {
                let parsed = parseFloat(val);
                if (isNaN(parsed)) parsed = 0.0;
                parsed = Math.max(0, Math.min(1, parsed));

                if (axis === 'x') localCalCoords[ledIndex][0] = parsed;
                else localCalCoords[ledIndex][1] = parsed;

                renderCalWorkspace();
            }

            function startDragCalNode(e, ledIndex) {
                e.preventDefault();
                e.stopPropagation();
                activeDragCalNodeIdx = ledIndex;
                activeHighlightNodeIdx = ledIndex;
                highlightPhysicalLed(currentCalibratorDeviceId, ledIndex);
                
                document.onmousemove = moveDragCalNode;
                document.onmouseup = stopDragCalNode;
            }

            function moveDragCalNode(e) {
                if (activeDragCalNodeIdx === null) return;
                const parent = document.getElementById("cal-workspace-bounds").getBoundingClientRect();
                
                let x = (e.clientX - parent.left) / parent.width;
                let y = (e.clientY - parent.top) / parent.height;

                x = Math.max(0, Math.min(1, x));
                y = Math.max(0, Math.min(1, y));

                // Apply snapping divisions if grid lock toggled [1]
                if (calGridLockEnabled) {
                    const divs = calGridDivisions;
                    x = Math.round(x * divs) / divs;
                    y = Math.round(y * divs) / divs;
                }

                localCalCoords[activeDragCalNodeIdx] = [x, y];
                renderCalLedList();
                renderCalWorkspace();
            }

            function stopDragCalNode() {
                activeDragCalNodeIdx = null;
                document.onmousemove = null;
                document.onmouseup = null;
            }

            function renderCalWorkspace() {
                const root = document.getElementById("cal-nodes-root");
                const svg = document.getElementById("cal-svg");
                root.innerHTML = "";
                svg.innerHTML = "";

                const parent = document.getElementById("cal-workspace-bounds").getBoundingClientRect();
                
                // Draw snappings overlay
                renderCalGridOverlay();

                let pathData = "";
                localCalCoords.forEach((coord, i) => {
                    const pxX = coord[0] * parent.width;
                    const pxY = coord[1] * parent.height;
                    
                    if (i === 0) pathData += `M ${pxX} ${pxY}`;
                    else pathData += ` L ${pxX} ${pxY}`;

                    const node = document.createElement("div");
                    const isSelected = activeHighlightNodeIdx === i;
                    const glowClass = isSelected ? 'border-cyan-400 bg-cyan-400 shadow-[0_0_8px_#06b6d4]' : 'border-slate-950 bg-pink-500 hover:bg-cyan-400';
                    node.className = `absolute h-2.5 w-2.5 rounded-full border cursor-grab active:cursor-grabbing transition-all z-20 ${glowClass}`;
                    node.style.left = `${coord[0]*100}%`;
                    node.style.top = `${coord[1]*100}%`;
                    node.style.transform = "translate(-50%, -50%)";

                    node.onmousedown = (e) => startDragCalNode(e, i);
                    
                    node.onmouseenter = () => {
                        activeHighlightNodeIdx = i;
                        highlightPhysicalLed(currentCalibratorDeviceId, i);
                        renderCalWorkspace();
                    };
                    node.onmouseleave = () => {
                        activeHighlightNodeIdx = null;
                        clearDeviceHighlight();
                        renderCalWorkspace();
                    };

                    root.appendChild(node);
                });

                if (localCalCoords.length > 1) {
                    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
                    path.setAttribute("d", pathData);
                    path.setAttribute("fill", "none");
                    path.setAttribute("stroke", "rgba(6,182,212,0.2)");
                    path.setAttribute("stroke-width", "1");
                    svg.appendChild(path);
                }
            }

            function renderCalGridOverlay() {
                const overlay = document.getElementById("cal-grid-overlay");
                overlay.innerHTML = "";
                if (!calGridLockEnabled) return;

                const parent = document.getElementById("cal-workspace-bounds").getBoundingClientRect();
                let gridHTML = "";

                // Horizontal subdivisions
                for (let i = 1; i < calGridDivisions; i++) {
                    const y = (i / calGridDivisions) * 100;
                    gridHTML += `<div class="absolute inset-x-0 border-t border-slate-800" style="top: ${y}%"></div>`;
                }
                // Vertical subdivisions
                for (let i = 1; i < calGridDivisions; i++) {
                    const x = (i / calGridDivisions) * 100;
                    gridHTML += `<div class="absolute inset-y-0 border-l border-slate-800" style="left: ${x}%"></div>`;
                }

                overlay.innerHTML = gridHTML;
            }

            async function resetCalibrationToDefault() {
                if (confirm("Reset current pins map to standard auto shape?")) {
                    const dev = devices.find(d => d.id === currentCalibratorDeviceId);
                    if (!dev) return;
                    
                    await fetch(`/api/devices/${dev.id}/profile/procedural/select`, { method: "POST" });
                    await closeCalibrationModal();
                    await fetchDevices();
                }
            }

            async function saveCalibrationAndClose() {
                // Prompt user for named configuration [1]
                const profileName = prompt("Enter a name for this custom layout profile:", "Custom Curve");
                if (!profileName || profileName.trim() === "") {
                    return; // Abort save if name empty
                }
                
                const sanitizedName = profileName.trim();
                const dev = devices.find(d => d.id === currentCalibratorDeviceId);
                if (!dev) return;

                await fetch(`/api/devices/${dev.id}/profile/${sanitizedName}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(localCalCoords)
                });
                
                await closeCalibrationModal();
                await fetchDevices();
            }

            async function closeCalibrationModal() {
                document.getElementById("calibration-modal").style.display = "none";
                currentCalibratorDeviceId = "";
                localCalCoords = [];
                activeDragCalNodeIdx = null;
                activeHighlightNodeIdx = null;
                await clearDeviceHighlight();
            }

            // --- WebSocket Frame Preview & Telemetry Sync ---

            function setupWebSocket() {
                const loc = window.location;
                const wsUrl = "ws://" + loc.host + "/ws/canvas_frame";
                const ws = new WebSocket(wsUrl);
                const canvas = document.getElementById("stream-preview");
                const ctx = canvas.getContext("2d");

                ws.onmessage = async (event) => {
                    // Parse packetized JSON telemetry frames [1]
                    const packet = JSON.parse(event.data);
                    
                    // Render canvas preview frame
                    const img = new Image();
                    img.onload = () => {
                        canvas.width = img.width;
                        canvas.height = img.height;
                        ctx.drawImage(img, 0, 0);
                    };
                    img.src = "data:image/jpeg;base64," + packet.image;
                    
                    // Render live active audio level meters [1]
                    if (packet.audio) {
                        document.getElementById("telemetry-bar-lows").style.width = `${packet.audio.lows * 100}%`;
                        document.getElementById("telemetry-bar-mids").style.width = `${packet.audio.mids * 100}%`;
                        document.getElementById("telemetry-bar-highs").style.width = `${packet.audio.highs * 100}%`;
                    }
                    
                    if (activeTab === "layout") {
                        fetchDevicesColors();
                    }
                };

                ws.onclose = () => {
                    setTimeout(setupWebSocket, 2000);
                };
            }

            async function fetchDevicesColors() {
                const res = await fetch('/api/devices');
                const updated = await res.json();
                devices.forEach(d => {
                    const found = updated.find(u => u.id === d.id);
                    if (found && found.demo_colors) {
                        d.demo_colors = found.demo_colors;
                    }
                });
                renderWorkspaceDevices();
            }

            function updateRefOpacity(val) {
                document.getElementById("stream-preview").style.opacity = parseFloat(val);
            }

            window.onload = init;
        </script>
    </body>
    </html>
'''
""".strip()

# 11. API Routes
files["api/routes.py"] = """
import os
import time
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from api.templates import INDEX_HTML
from core.config import AppSettings
from audio.discovery import discover_system_audio_devices

router = APIRouter()

# Global core reference injected on start
engine_ref = None

class EffectSelectPayload(BaseModel):
    effect_name: str

class ParamUpdatePayload(BaseModel):
    key: str
    value: Any

class DeviceCoordsPayload(BaseModel):
    x: float
    y: float
    width: float
    height: float
    form_type: str
    active_profile: str = "procedural"
    custom_profiles: Dict[str, List[List[float]]] = None

class DeviceOrderPayload(BaseModel):
    led_order: List[int]

class FavoritesUpdatePayload(BaseModel):
    favorites: List[str]

class SettingsUpdatePayload(BaseModel):
    openrgb_host: str
    openrgb_port: int
    target_fps: int
    canvas_width: int
    audio_mode: str
    audio_device_id: str
    audio_emulation: bool
    audio_noise_gate: float

class PluginTogglePayload(BaseModel):
    enabled: bool

class PluginParamPayload(BaseModel):
    key: str
    value: Any


@router.get("/", response_class=HTMLResponse)
def index_page():
    return HTMLResponse(content=INDEX_HTML)

@router.get("/api/config")
def get_config():
    return engine_ref.cm.config

@router.get("/api/effects")
def get_effects():
    return {
        "active": engine_ref.active_effect_name,
        "params": engine_ref.effect_params,
        "library": {name: eff.get_parameter_schema() for name, eff in engine_ref.effect_manager.effects.items()},
        "favorites": engine_ref.cm.config.favorited_effects
    }

@router.post("/api/effects/select")
async def select_effect(payload: EffectSelectPayload):
    await engine_ref.update_active_effect(payload.effect_name)
    return {"status": "ok", "active": engine_ref.active_effect_name, "params": engine_ref.effect_params}

@router.post("/api/effects/param")
async def update_param(payload: ParamUpdatePayload):
    await engine_ref.update_parameter(payload.key, payload.value)
    return {"status": "ok"}

@router.post("/api/effects/favorites")
def update_favorites(payload: FavoritesUpdatePayload):
    engine_ref.cm.config.favorited_effects = payload.favorites
    engine_ref.cm.save_config()
    return {"status": "ok"}

@router.get("/api/audio/devices")
def get_audio_devices():
    return discover_system_audio_devices()

@router.get("/api/gifs")
def list_gifs():
    result = []
    cfg = engine_ref.cm.config
    if os.path.exists("./gifs"):
        for file in os.listdir("./gifs"):
            if file.endswith(".gif"):
                display_name = cfg.gif_library_names.get(file, file.replace("_", " ").title()[:-4])
                result.append({
                    "id": file,
                    "name": display_name,
                    "active": file == cfg.active_gif_filename
                })
    return result

@router.post("/api/gifs/{filename}/rename")
def rename_gif_label(filename: str, payload: Dict[str, str]):
    if "name" not in payload:
        raise HTTPException(status_code=400, detail="Missing custom name field")
    engine_ref.cm.config.gif_library_names[filename] = payload["name"]
    engine_ref.cm.save_config()
    return {"status": "ok"}

@router.post("/api/gifs/{filename}/select")
async def select_active_gif(filename: str):
    if not os.path.exists(f"./gifs/{filename}"):
        raise HTTPException(status_code=404, detail="Target GIF not found")
    engine_ref.cm.config.active_gif_filename = filename
    engine_ref.cm.save_config()
    if "GifPlayer" in engine_ref.effect_manager.effects:
        engine_ref.effect_params["_active_gif_file"] = filename
        engine_ref.cm.config.effect_parameters["_active_gif_file"] = filename
        engine_ref.cm.save_config()
        engine_ref.effect_manager.effects["GifPlayer"].loaded = False
    return {"status": "ok"}

@router.delete("/api/gifs/{filename}")
def delete_gif_asset(filename: str):
    if filename == "target.gif":
        raise HTTPException(status_code=403, detail="Default alignment GIF cannot be deleted!")
    target_path = f"./gifs/{filename}"
    if os.path.exists(target_path): os.remove(target_path)
    if filename in engine_ref.cm.config.gif_library_names:
        del engine_ref.cm.config.gif_library_names[filename]
    if engine_ref.cm.config.active_gif_filename == filename:
        engine_ref.cm.config.active_gif_filename = "target.gif"
        if "GifPlayer" in engine_ref.effect_manager.effects:
            engine_ref.effect_params["_active_gif_file"] = "target.gif"
            engine_ref.cm.config.effect_parameters["_active_gif_file"] = "target.gif"
            engine_ref.effect_manager.effects["GifPlayer"].loaded = False
    engine_ref.cm.save_config()
    return {"status": "ok"}

@router.post("/api/upload/gif")
async def upload_gif_file(request: Request):
    os.makedirs("./gifs", exist_ok=True)
    safe_filename = f"upload_{int(time.time())}.gif"
    gif_path = f"./gifs/{safe_filename}"
    try:
        contents = await request.body()
        if not contents: raise HTTPException(status_code=400, detail="Empty request payload received")
        with open(gif_path, "wb") as f: f.write(contents)
        engine_ref.cm.config.gif_library_names[safe_filename] = f"Upload ({time.strftime('%H:%M:%S')})"
        engine_ref.cm.config.active_gif_filename = safe_filename
        if "GifPlayer" in engine_ref.effect_manager.effects:
            engine_ref.effect_params["_active_gif_file"] = safe_filename
            engine_ref.cm.config.effect_parameters["_active_gif_file"] = safe_filename
            engine_ref.effect_manager.effects["GifPlayer"].loaded = False
        engine_ref.cm.save_config()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process media file: {e}")

@router.get("/api/plugins")
def get_plugins():
    result = []
    for plug_id, data in engine_ref.plugin_manager.plugins.items():
        result.append({
            "id": plug_id, "name": data["name"], "description": data["description"],
            "enabled": data["enabled"], "params": data["params"], "schema": data["schema"]
        })
    return result

@router.post("/api/plugins/{plugin_id}/toggle")
def toggle_plugin(plugin_id: str, payload: PluginTogglePayload):
    if plugin_id not in engine_ref.plugin_manager.plugins:
        raise HTTPException(status_code=404, detail="Plugin not found")
    engine_ref.plugin_manager.plugins[plugin_id]["enabled"] = payload.enabled
    cfg = engine_ref.cm.config
    if payload.enabled and plugin_id not in cfg.enabled_plugins: cfg.enabled_plugins.append(plugin_id)
    elif not payload.enabled and plugin_id in cfg.enabled_plugins: cfg.enabled_plugins.remove(plugin_id)
    engine_ref.cm.save_config()
    return {"status": "ok", "enabled": payload.enabled}

@router.post("/api/plugins/{plugin_id}/param")
def update_plugin_param(plugin_id: str, payload: PluginParamPayload):
    if plugin_id not in engine_ref.plugin_manager.plugins:
         raise HTTPException(status_code=404, detail="Plugin not found")
    engine_ref.plugin_manager.plugins[plugin_id]["params"][payload.key] = payload.value
    cfg = engine_ref.cm.config
    if plugin_id not in cfg.plugin_parameters: cfg.plugin_parameters[plugin_id] = {}
    cfg.plugin_parameters[plugin_id][payload.key] = payload.value
    engine_ref.cm.save_config()
    return {"status": "ok"}

@router.get("/api/devices")
def list_devices():
    devs = []
    for d in engine_ref.devices:
        dev_data = {
            "id": d.device_id, "name": d.name, "led_count": d.led_count, "enabled": d.enabled,
            "form_type": d.form_type, "x": d.x, "y": d.y, "width": d.width, "height": d.height,
            "active_profile": d.active_profile, "custom_profiles": d.custom_profiles,
            "coordinates": d.coordinates.tolist(), "local_coords": d.local_coords.tolist(), "led_order": d.led_order_mapping.tolist()
        }
        if hasattr(d, "last_sent_colors"): dev_data["demo_colors"] = d.last_sent_colors
        devs.append(dev_data)
    return devs

@router.post("/api/devices/{device_id}/toggle")
def toggle_device(device_id: str):
    for d in engine_ref.devices:
        if d.device_id == device_id:
            d.enabled = not d.enabled
            engine_ref.cm.config.devices_layout[d.device_id] = d.export_layout()
            engine_ref.cm.save_config()
            return {"status": "ok", "enabled": d.enabled}
    raise HTTPException(status_code=404, detail="Device not found")

@router.post("/api/devices/{device_id}/bounds")
def update_device_bounds(device_id: str, payload: DeviceCoordsPayload):
    for d in engine_ref.devices:
        if d.device_id == device_id:
            d.x = payload.x
            d.y = payload.y
            d.width = payload.width
            d.height = payload.height
            d.form_type = payload.form_type
            d.active_profile = payload.active_profile
            if payload.custom_profiles is not None: d.custom_profiles = payload.custom_profiles
            d._build_local_layout()
            d.recompute_global_coordinates()
            engine_ref.cm.config.devices_layout[d.device_id] = d.export_layout()
            engine_ref.cm.save_config()
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Device not found")

@router.post("/api/devices/{device_id}/reorder")
def update_device_ordering(device_id: str, payload: DeviceOrderPayload):
    for d in engine_ref.devices:
        if d.device_id == device_id:
            if len(payload.led_order) != d.led_count: raise HTTPException(status_code=400, detail="Size mismatch")
            d.led_order_mapping = np.array(payload.led_order, dtype=np.int32)
            engine_ref.cm.config.devices_layout[d.device_id] = d.export_layout()
            engine_ref.cm.save_config()
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Device not found")

@router.post("/api/devices/{device_id}/auto_order")
def auto_order_device(device_id: str, mode: str):
    for d in engine_ref.devices:
        if d.device_id == device_id:
            coords = d.local_coords
            if mode == "left_to_right": new_order = np.argsort(coords[:, 0])
            elif mode == "top_to_bottom": new_order = np.argsort(coords[:, 1])
            elif mode == "clockwise":
                center = np.mean(coords, axis=0)
                angles = np.arctan2(coords[:, 1] - center[1], coords[:, 0] - center[0])
                new_order = np.argsort(angles)
            else: raise HTTPException(status_code=400, detail="Invalid sorting heuristic")
            d.led_order_mapping = new_order.astype(np.int32)
            engine_ref.cm.config.devices_layout[d.device_id] = d.export_layout()
            engine_ref.cm.save_config()
            return {"status": "ok", "led_order": d.led_order_mapping.tolist()}
    raise HTTPException(status_code=404, detail="Device not found")

@router.post("/api/devices/{device_id}/highlight/{led_index}")
def set_device_highlight(device_id: str, led_index: int):
    engine_ref.highlight_device_id = device_id
    engine_ref.highlight_led_index = led_index
    return {"status": "ok"}

@router.post("/api/devices/highlight/clear")
def clear_device_highlight():
    engine_ref.highlight_device_id = None
    engine_ref.highlight_led_index = -1
    return {"status": "ok"}

@router.post("/api/settings")
async def update_settings(payload: SettingsUpdatePayload):
    engine_ref.cm.config.openrgb_host = payload.openrgb_host
    engine_ref.cm.config.openrgb_port = payload.openrgb_port
    engine_ref.cm.config.target_fps = payload.target_fps
    engine_ref.cm.config.canvas_width = payload.canvas_width
    engine_ref.cm.config.audio_mode = payload.audio_mode
    engine_ref.cm.config.audio_device_id = payload.audio_device_id
    engine_ref.cm.config.audio_emulation = payload.audio_emulation
    engine_ref.cm.config.audio_noise_gate = payload.audio_noise_gate
    engine_ref.cm.save_config()
    await engine_ref.canvas.resize(payload.canvas_width)
    await engine_ref.stop()
    engine_ref.start()
    return {"status": "ok"}

# --- Layout custom coordinate profile endpoints --- [1]

@router.post("/api/devices/{device_id}/profile/{profile_name}")
def save_named_layout_profile(device_id: str, profile_name: str, payload: List[List[float]]):
    for d in engine_ref.devices:
        if d.device_id == device_id:
            d.custom_profiles[profile_name] = payload
            d.active_profile = f"profile:{profile_name}"
            d.recompute_global_coordinates()
            engine_ref.cm.config.devices_layout[d.device_id] = d.export_layout()
            engine_ref.cm.save_config()
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Device not found")

@router.post("/api/devices/{device_id}/profile/{profile_name}/select")
def select_named_profile(device_id: str, profile_name: str):
    for d in engine_ref.devices:
        if d.device_id == device_id:
            if profile_name == "procedural": d.active_profile = "procedural"
            else:
                target_key = profile_name.replace("profile:", "")
                if target_key not in d.custom_profiles: raise HTTPException(status_code=404, detail="Target profile key not found")
                d.active_profile = f"profile:{target_key}"
            d.recompute_global_coordinates()
            engine_ref.cm.config.devices_layout[d.device_id] = d.export_layout()
            engine_ref.cm.save_config()
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Device not found")

@router.delete("/api/devices/{device_id}/profile/{profile_name}")
def delete_named_profile(device_id: str, profile_name: str):
    for d in engine_ref.devices:
        if d.device_id == device_id:
            if profile_name in d.custom_profiles: del d.custom_profiles[profile_name]
            if d.active_profile == f"profile:{profile_name}": d.active_profile = "procedural"
            d.recompute_global_coordinates()
            engine_ref.cm.config.devices_layout[d.device_id] = d.export_layout()
            engine_ref.cm.save_config()
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Device not found")
""".strip()

# 12. Main Orchestrator Execution
files["main.py"] = """
import os
from fastapi import FastAPI
from core.config import ConfigManager
from core.engine import EngineCore
import api.routes as routes

# Initialize State configuration
config_manager = ConfigManager()
engine = EngineCore(config_manager)

# Inject active engine reference into router module
routes.engine_ref = engine

# Initialize FastAPI router lifecycle
app = FastAPI(title="Lumina Spatial Calibration Engine")
app.include_router(routes.router)

@app.on_event("startup")
async def startup_event():
    engine.start()

@app.on_event("shutdown")
async def shutdown_event():
    await engine.stop()

@app.websocket("/ws/canvas_frame")
async def ws_canvas_frame_endpoint(websocket: any):
    await routes.ws_canvas_frame(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
""".strip()

# Write files programmatically
for path, content in files.items():
    # Split file directory
    dir_name = os.path.dirname(path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    
    # Write safe UTF-8 file contents
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        
    print(f"[+] Programmatically wrote module: {path}")

print("\n" + "="*50)
print("[*] Project structural layout bootstrap successful!")
print("[*] Run the following commands to install dependencies and launch:")
print("    1. pip install -r requirements.txt")
print("    2. python main.py")
print("="*50)
