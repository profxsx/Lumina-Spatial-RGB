"""
Lumina Configuration Module
Manages persistent state settings, layout profiles, and disk JSON serialization.
"""

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