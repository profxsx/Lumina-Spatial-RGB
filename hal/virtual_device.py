import numpy as np
from hal.base import AbstractRGBDevice

class VirtualDemoDevice(AbstractRGBDevice):
    def __init__(self, device_id: str, name: str, led_count: int, form_type: str):
        super().__init__(device_id, name, led_count, form_type)
        self.last_sent_colors = [[0, 0, 0] for _ in range(led_count)]

    async def push_colors(self, color_array: np.ndarray):
        if not self.enabled: return
        self.last_sent_colors = color_array[self.led_order_mapping].tolist()