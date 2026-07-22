import time
import math
import numpy as np
from effects.base_effect import BaseEffect

class RadialAudioPulsar(BaseEffect):
    def render(self, canvas, dt, params, audio_bands):
        h, w, _ = canvas.shape
        canvas.fill(0)
        
        speed = params.get("speed", 2.0)
        base_thickness = params.get("thickness", 0.06)
        lows_reactivity = params.get("bass_react", 1.5)
        
        # Create aspect-corrected grid coordinates centered at origin
        y_grid, x_grid = np.mgrid[0:h, 0:w]
        yn = y_grid / max(1, h - 1) - 0.5
        xn = (x_grid / max(1, w - 1) - 0.5) * (16.0 / 10.0) # aspect-ratio lock
        
        pixel_distance = np.sqrt(xn**2 + yn**2)
        
        # Modulate pulsar radius expansion via bass metrics
        bass = audio_bands.get("lows", 0.0)
        t = time.time() * speed + (bass * lows_reactivity)
        
        target_radius = (t % 1.2) * 0.5
        pulse_thickness = base_thickness + (bass * base_thickness * 2.0)
        
        # Isolate ring elements using Gaussian filter curve
        ring_intensity = np.exp(-((pixel_distance - target_radius) / pulse_thickness) ** 2)
        
        color = np.array(params.get("color", [236, 72, 153]))
        canvas[:, :] = (color * ring_intensity[:, :, np.newaxis]).astype(np.uint8)
        
        return canvas

    def get_parameter_schema(self):
        return {
            "speed": {"label": "Expansion Speed", "type": "range", "min": 0.5, "max": 4.5, "default": 2.0, "step": 0.1},
            "thickness": {"label": "Base Ring Thickness", "type": "range", "min": 0.02, "max": 0.2, "default": 0.06, "step": 0.01},
            "bass_react": {"label": "Bass Dynamic Kick", "type": "range", "min": 0.0, "max": 3.0, "default": 1.5, "step": 0.1},
            "color": {"label": "Ring Flare", "type": "color", "default": [236, 72, 153]}
        }
