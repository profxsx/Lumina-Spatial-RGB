import time
import math
import numpy as np
from effects.base_effect import BaseEffect

class SingleWave(BaseEffect):
    def render(self, canvas, dt, params, audio_bands):
        h, w, _ = canvas.shape
        
        # Configure mathematical parameters
        speed = params.get("speed", 2.0)
        frequency = params.get("frequency", 4.0)
        width = params.get("width", 0.4)
        angle_deg = params.get("angle", 45.0)
        
        # Unit vector from degree angle
        theta = math.radians(angle_deg)
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        
        # Vectorized coordinate grid generation
        y_grid, x_grid = np.mgrid[0:h, 0:w]
        yn = y_grid / max(1, h - 1)
        xn = x_grid / max(1, w - 1)
        
        # Project 2D coordinates onto wave movement vector
        projection = xn * cos_t + yn * sin_t
        
        # Scrolling phase shift
        t = time.time() * speed
        phase = (projection * frequency - t) % (2.0 * math.pi)
        
        # Create single Gaussian wave peak centered around pi
        wave_intensity = np.exp(-((phase - math.pi) / width) ** 2)
        
        wave_color = np.array(params.get("wave_color", [6, 182, 212]))
        bg_color = np.array(params.get("bg_color", [13, 19, 35]))
        
        # Smooth interpolation between background and wave peak
        canvas[:, :] = (bg_color + (wave_color - bg_color) * wave_intensity[:, :, np.newaxis]).astype(np.uint8)
        return canvas

    def get_parameter_schema(self):
        return {
            "angle": {"label": "Wave Direction (Degrees)", "type": "range", "min": 0.0, "max": 360.0, "default": 45.0, "step": 5.0},
            "speed": {"label": "Scroll Speed", "type": "range", "min": 0.5, "max": 6.0, "default": 2.0, "step": 0.1},
            "frequency": {"label": "Wave Frequency", "type": "range", "min": 1.0, "max": 10.0, "default": 4.0, "step": 0.5},
            "width": {"label": "Peak Width Thickness", "type": "range", "min": 0.1, "max": 1.5, "default": 0.4, "step": 0.05},
            "wave_color": {"label": "Peak Color", "type": "color", "default": [6, 182, 212]},
            "bg_color": {"label": "Background Color", "type": "color", "default": [5, 8, 17]}
        }
