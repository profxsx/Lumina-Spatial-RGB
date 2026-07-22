import os
import time
import numpy as np
from PIL import Image
from effects.base_effect import BaseEffect

class GifPlayer(BaseEffect):
    def __init__(self):
        self.gif_path = "./gifs/target.gif"
        self.frames = []
        self.last_time = time.time()
        self.current_frame = 0
        self.loaded = False
        self.last_path = ""

    def load_gif(self, active_filename):
        target_path = f"./gifs/{active_filename}"
        if not os.path.exists(target_path):
            target_path = "./gifs/target.gif"
            
        if self.loaded and target_path == self.last_path:
            return
            
        try:
            img = Image.open(target_path)
            self.frames = []
            while True:
                self.frames.append(img.convert("RGB"))
                try:
                    img.seek(img.tell() + 1)
                except EOFError:
                    break
            self.last_path = target_path
            self.loaded = True
        except Exception as e:
            print(f"[*] Failed to parse GIF file {target_path}: {e}")
            self.loaded = False

    def render(self, canvas, dt, params, audio_bands):
        active_file = params.get("_active_gif_file", "target.gif")
        self.load_gif(active_file)
        
        if not self.loaded or not self.frames:
            canvas.fill(10)
            canvas[10:-10, 10:-10] = [236, 72, 153]
            return canvas

        h, w, _ = canvas.shape
        speed = params.get("playback_speed", 1.0)
        grayscale_mode = params.get("grayscale", False)
        
        now = time.time()
        if now - self.last_time > (0.15 / speed):
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_time = now

        frame_img = self.frames[self.current_frame].resize((w, h))
        raw_frame = np.array(frame_img)
        
        if grayscale_mode:
            gray = np.dot(raw_frame[..., :3], [0.299, 0.587, 0.114]).astype(np.uint8)
            canvas[..., 0] = gray
            canvas[..., 1] = gray
            canvas[..., 2] = gray
        else:
            canvas[:, :] = raw_frame
            
        return canvas

    def get_parameter_schema(self):
        return {
            "playback_speed": {"label": "GIF Playback Speed", "type": "range", "min": 0.1, "max": 5.0, "default": 1.0, "step": 0.1},
            "grayscale": {"label": "Grayscale (Black & White)", "type": "toggle", "default": False},
            "_active_gif_file": {"label": "Internal File Binding", "type": "hidden", "default": "target.gif"}
        }