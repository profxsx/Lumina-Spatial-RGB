import numpy as np

class AudioPulsarPlugin:
    def __init__(self):
        self.name = "Audio Pulsar"
        self.description = "Creates a pulsating ring mapped to live system bass output."
        
    def render_frame(self, canvas, dt, params, audio_bands):
        h, w, _ = canvas.shape
        bass = audio_bands["lows"] * params.get("multiplier", 1.5)
        glow_color = params.get("glow_color", [6, 182, 212])
        
        cx, cy = w // 2, h // 2
        radius = int(min(w, h) * 0.15 + bass * min(w, h) * 0.3)
        radius = max(2, min(radius, min(w, h) // 2 - 1))
        
        y, x = np.ogrid[:h, :w]
        dist_from_center = np.sqrt((x - cx)**2 + (y - cy)**2)
        mask = (dist_from_center >= radius - 3) & (dist_from_center <= radius + 3)
        canvas[mask] = glow_color
        return canvas

    def get_settings_schema(self):
        return {
            "multiplier": {"label": "React Limit", "type": "range", "min": 0.5, "max": 5.0, "default": 1.5, "step": 0.1},
            "glow_color": {"label": "Neon Color", "type": "color", "default": [6, 182, 212]}
        }