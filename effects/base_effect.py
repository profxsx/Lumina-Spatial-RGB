from abc import ABC, abstractmethod
import numpy as np
from typing import Dict, Any

class BaseEffect(ABC):
    @abstractmethod
    def render(self, canvas: np.ndarray, dt: float, params: Dict[str, Any], audio_bands: Dict[str, float]) -> np.ndarray:
        pass
    @abstractmethod
    def get_parameter_schema(self) -> Dict[str, Any]:
        pass