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