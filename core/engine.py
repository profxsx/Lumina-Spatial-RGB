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