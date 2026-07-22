import numpy as np
import asyncio

class CanvasRenderer:
    def __init__(self, width: int):
        self.width = width
        self.height = int(width * 10 // 16)
        self._buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        self._lock = asyncio.Lock()

    async def resize(self, width: int):
        async with self._lock:
            self.width = width
            self.height = int(width * 10 // 16)
            self._buffer = np.zeros((self.height, self.width, 3), dtype=np.uint8)

    @property
    def buffer(self) -> np.ndarray:
        return self._buffer

class LEDSampler:
    @staticmethod
    def sample(canvas_buffer: np.ndarray, coordinates: np.ndarray) -> np.ndarray:
        h, w, _ = canvas_buffer.shape
        if coordinates.size == 0:
            return np.zeros((0, 3), dtype=np.uint8)
        x_indices = np.clip((coordinates[:, 0] * (w - 1)), 0, w - 1).astype(np.int32)
        y_indices = np.clip((coordinates[:, 1] * (h - 1)), 0, h - 1).astype(np.int32)
        return canvas_buffer[y_indices, x_indices]