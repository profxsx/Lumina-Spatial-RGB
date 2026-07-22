import time
import math
import numpy as np
from effects.base_effect import BaseEffect

class PlasmaFlow(BaseEffect):
    def render(self, canvas, dt, params, audio_bands):
        h, w, _ = canvas.shape
        
        speed = params.get("speed", 1.5)
        scale = params.get("scale", 3.0)
        audio_react = params.get("audio_react", 1.0)
        
        # Incorporate audio telemetry directly into the temporal drift
        bass_boost = audio_bands.get("lows", 0.0) * audio_react * 4.0
        t = time.time() * speed + bass_boost
        
        # Fast vectorized grid
        y_grid, x_grid = np.mgrid[0:h, 0:w]
        yn = y_grid / max(1, h - 1) - 0.5
        xn = x_grid / max(1, w - 1) - 0.5
        
        # Complex multi-harmonic interference equations
        v1 = np.sin(xn * scale + t)
        v2 = np.sin(scale * (yn * math.cos(t / 2.0) + xn * math.sin(t / 3.0)) + t)
        v3 = np.sin(np.sqrt(xn**2 + yn**2) * scale * 2.0 - t)
        
        # Average variables and map output array within [0, 1]
        raw_plasma = (v1 + v2 + v3) / 3.0
        intensity = np.clip(raw_plasma * 0.5 + 0.5, 0.0, 1.0)
        
        primary = np.array(params.get("primary", [236, 72, 153]))
        secondary = np.array(params.get("secondary", [6, 182, 212]))
        
        canvas[:, :] = (primary * intensity[:, :, np.newaxis] + secondary * (1.0 - intensity[:, :, np.newaxis])).astype(np.uint8)
        return canvas

    def get_parameter_schema(self):
        return {
            "speed": {"label": "Drift Speed", "type": "range", "min": 0.2, "max": 4.0, "default": 1.5, "step": 0.1},
            "scale": {"label": "Resolution Scale", "type": "range", "min": 1.0, "max": 10.0, "default": 3.0, "step": 0.2},
            "audio_react": {"label": "Lows/Bass Frequency Boost", "type": "range", "min": 0.0, "max": 2.0, "default": 1.0, "step": 0.1},
            "primary": {"label": "Primary Flare", "type": "color", "default": [236, 72, 153]},
            "secondary": {"label": "Secondary Flare", "type": "color", "default": [6, 182, 212]}
        }
