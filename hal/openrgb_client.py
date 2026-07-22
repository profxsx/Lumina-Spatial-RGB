"""
Lumina OpenRGB Client Device Wrapper Module
Discovers physical USB controllers and maps them to spatial target profiles.
"""

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
        
        # Enhanced keyword matching for automatic form-factor classification
        if "KEYBOARD" in name or "BOARD" in name:
            form = "KEYBOARD"
        elif any(k in name for k in ["RAM", "DRAM", "DDR", "MEMORY", "VENGEANCE", "DOMINATOR", "TRIDENT", "G.SKILL"]):
            form = "RAM"
        elif any(k in name for k in ["FAN", "COOLER", "LIGHTWINGS", "LL120", "QL120"]):
            form = "FAN"
        elif "STRIMER" in name:
            form = "STRIMER_24PIN"
        else:
            form = "STRIP"
            
        super().__init__(dev_id, orbg_device.name, len(orbg_device.leds), form)
        self._raw_device = orbg_device

    async def push_colors(self, color_array: np.ndarray):
        if not self.enabled or not OPENRGB_AVAILABLE: 
            return
        mapped_colors = color_array[self.led_order_mapping]
        
        def _sync_write():
            self._raw_device.set_colors([RGBColor(c[0], c[1], c[2]) for c in mapped_colors], fast=True)
            
        await asyncio.to_thread(_sync_write)