
"""
Lumina Hardware Abstraction Layer Base Module
Defines abstract hardware contracts and manages relative-to-global spatial conversions.
"""

import numpy as np
import math
import time
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
        self.rotation: float = 0.0
        self.hidden_in_layout: bool = False
        self.identify_until: float = 0.0

        self.local_coords: np.ndarray = np.zeros((led_count, 2), dtype=np.float32)
        
        # User defined named custom layout profiles database
        self.custom_profiles: Dict[str, List[List[float]]] = {}
        self.active_profile: str = "procedural" # "procedural" or custom named profile key
        
        # Global transformed coordinates mapped onto the panoramic workspace
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
        """Maps local shapes within rotated, translated bounds on the panoramic workspace."""
        active_local = self.local_coords
        
        profile_key = self.active_profile
        if profile_key.startswith("profile:"):
            profile_key = profile_key.replace("profile:", "")

        if profile_key != "procedural" and profile_key in self.custom_profiles:
            active_local = np.array(self.custom_profiles[profile_key], dtype=np.float32)

        # Base translations
        gx = self.x + active_local[:, 0] * self.width
        gy = self.y + active_local[:, 1] * self.height

        # Calculate rotation around bounding box midpoint
        if hasattr(self, "rotation") and self.rotation != 0.0:
            cx = self.x + self.width / 2.0
            cy = self.y + self.height / 2.0
            rad = math.radians(self.rotation)
            cos_val = math.cos(rad)
            sin_val = math.sin(rad)
            
            dx = gx - cx
            dy = gy - cy
            
            self.coordinates[:, 0] = cx + dx * cos_val - dy * sin_val
            self.coordinates[:, 1] = cy + dx * sin_val + dy * cos_val
        else:
            self.coordinates[:, 0] = gx
            self.coordinates[:, 1] = gy

        self.coordinates = np.clip(self.coordinates, 0.0, 1.0)

    def load_layout(self, layout: Dict[str, Any]):
        self.x = layout.get("x", self.x)
        self.y = layout.get("y", self.y)
        self.width = layout.get("width", self.width)
        self.height = layout.get("height", self.height)
        self.rotation = layout.get("rotation", 0.0)
        self.hidden_in_layout = layout.get("hidden_in_layout", False)
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
            "rotation": self.rotation,
            "hidden_in_layout": self.hidden_in_layout,
            "enabled": self.enabled,
            "form_type": self.form_type,
            "active_profile": self.active_profile,
            "custom_profiles": self.custom_profiles,
            "led_order": self.led_order_mapping.tolist()
        }

    def get_effective_colors(self, sampled_colors: np.ndarray) -> np.ndarray:
        """Applies diagnostic blinking blue pattern overrides during active identification windows."""
        if hasattr(self, 'identify_until') and time.time() < self.identify_until:
            pulse = int(time.time() * 8) % 2
            if pulse == 0:
                blink_colors = np.zeros_like(sampled_colors)
                blink_colors[:, 2] = 255  # Solid Blue
                return blink_colors
            else:
                return np.zeros_like(sampled_colors)  # Black (Off)
        return sampled_colors

    @abstractmethod
    async def push_colors(self, color_array: np.ndarray):
        pass
