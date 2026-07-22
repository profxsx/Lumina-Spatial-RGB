import time
import math
import numpy as np
from effects.base_effect import BaseEffect

class StarlightTwinkle(BaseEffect):
    def render(self, canvas, dt, params, audio_bands):
        h, w, _ = canvas.shape
        canvas.fill(0)
        
        density = params.get("density", 0.03)
        twinkle_speed = params.get("speed", 4.0)
        highs_boost = params.get("treble_react", 1.5)
        star_color = np.array(params.get("color", [255, 255, 255]))
        
        t = time.time() * twinkle_speed
        
        # Deterministic star distribution via seeded NumPy generator
        generator = np.random.default_rng(2026)
        num_stars = max(1, int(w * h * density))
        
        star_x = generator.integers(0, w, size=num_stars)
        star_y = generator.integers(0, h, size=num_stars)
        star_phases = generator.random(size=num_stars) * 2.0 * math.pi
        
        treble = audio_bands.get("highs", 0.0)
        
        for i in range(num_stars):
            # Compute underlying periodic twinkle phase
            base_fade = math.sin(t + star_phases[i]) * 0.5 + 0.5
            
            # Incorporate high audio bands
            effective_brightness = base_fade + (treble * highs_boost)
            brightness = max(0.0, min(1.0, effective_brightness))
            
            canvas[star_y[i], star_x[i]] = (star_color * brightness).astype(np.uint8)
            
        return canvas

    def get_parameter_schema(self):
        return {
            "density": {"label": "Star Matrix Density", "type": "range", "min": 0.005, "max": 0.1, "default": 0.03, "step": 0.005},
            "speed": {"label": "Twinkle Frequency", "type": "range", "min": 1.0, "max": 8.0, "default": 4.0, "step": 0.2},
            "treble_react": {"label": "Treble/Highs Sparkle Reactivity", "type": "range", "min": 0.0, "max": 3.0, "default": 1.5, "step": 0.1},
            "color": {"label": "Starlight Color", "type": "color", "default": [255, 255, 255]}
        }
