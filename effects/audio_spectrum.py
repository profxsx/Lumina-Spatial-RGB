import numpy as np
from effects.base_effect import BaseEffect

class AudioSpectrumBlast(BaseEffect):
    def render(self, canvas, dt, params, audio_bands):
        h, w, _ = canvas.shape
        canvas.fill(0)

        gain = params.get("gain", 1.2)
        lows_bar = int(audio_bands["lows"] * gain * h)
        mids_bar = int(audio_bands["mids"] * gain * h)
        highs_bar = int(audio_bands["highs"] * gain * h)

        seg_w = w // 3
        if lows_bar > 0:
            canvas[-lows_bar:, :seg_w] = [236, 72, 153]
        if mids_bar > 0:
            canvas[-mids_bar:, seg_w:2*seg_w] = [6, 182, 212]
        if highs_bar > 0:
            canvas[-highs_bar:, 2*seg_w:] = [34, 197, 94]

        return canvas

    def get_parameter_schema(self):
        return {
            "gain": {"label": "System Reactivity Gain", "type": "range", "min": 0.5, "max": 5.0, "default": 1.5, "step": 0.1}
        }