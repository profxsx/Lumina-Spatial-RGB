import os
import inspect
import importlib.util
from typing import Dict
from effects.base_effect import BaseEffect
from core.config import ConfigManager

def ensure_effects_directory():
    os.makedirs("./effects", exist_ok=True)
    os.makedirs("./assets", exist_ok=True)
    os.makedirs("./gifs", exist_ok=True)

class EffectManager:
    def __init__(self, config_manager: ConfigManager):
        self.cm = config_manager
        self.effects: Dict[str, BaseEffect] = {}
        ensure_effects_directory()
        self.load_all_effects()

    def load_all_effects(self):
        self.effects.clear()
        if not os.path.exists("./effects"): return
        for file in os.listdir("./effects"):
            if file.endswith(".py") and file != "base_effect.py" and not file.startswith("__"):
                module_name = file[:-3]
                module_path = os.path.join("./effects", file)
                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        for name, cls in inspect.getmembers(module, inspect.isclass):
                            if cls.__module__ == module_name and hasattr(cls, "render") and hasattr(cls, "get_parameter_schema"):
                                self.effects[name] = cls()
                                print(f"[*] Registered Effect: {name}")
                except Exception as e:
                    print(f"[*] Failed to import effect {file}: {e}")