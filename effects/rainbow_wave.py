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