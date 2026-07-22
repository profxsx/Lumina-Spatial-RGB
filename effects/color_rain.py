import time
import math
import numpy as np
from effects.base_effect import BaseEffect

class CyberRain(BaseEffect):
    def render(self, canvas, dt, params, audio_bands):
        h, w, _ = canvas.shape
        canvas.fill(0)
        
        speed = params.get("speed", 3.0)
        length_ratio = params.get("length", 0.5)
        rain_color = np.array(params.get("color", [34, 197, 94]))
        
        t = time.time() * speed
        
        # Deterministic psuedo-random offsets and velocities per vertical column
        cols = np.arange(w)
        offsets = np.sin(cols * 12.9898) * 43758.5453 % 1.0
        col_speeds = 0.6 + (np.cos(cols * 7.123) * 0.5 + 0.5) * 1.4
        
        # Calculate active drop positions
        lead_positions = (t * col_speeds + offsets * 6.0) % 1.6 - 0.3
        
        for x in range(w):
            lead_y = int(lead_positions[x] * h)
            drop_len = max(2, int(length_ratio * h))
            
            for i in range(drop_len):
                y = lead_y - i
                if 0 <= y < h:
                    # Decay brightness linearly down the tail length
                    intensity = 1.0 - (i / drop_len)
                    canvas[y, x] = (rain_color * intensity).astype(np.uint8)
                    
        return canvas

    def get_parameter_schema(self):
        return {
            "speed": {"label": "Rain Drop Speed", "type": "range", "min": 1.0, "max": 8.0, "default": 3.0, "step": 0.2},
            "length": {"label": "Tail Length", "type": "range", "min": 0.1, "max": 0.9, "default": 0.5, "step": 0.05},
            "color": {"label": "Droplet Color", "type": "color", "default": [34, 197, 94]}
        }
