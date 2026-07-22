import os
import inspect
import importlib.util
from typing import Dict, Any
from core.config import ConfigManager

def ensure_plugins_directory():
    os.makedirs("./plugins", exist_ok=True)

class PluginManager:
    def __init__(self, config_manager: ConfigManager):
        self.cm = config_manager
        self.plugins: Dict[str, Dict[str, Any]] = {}
        ensure_plugins_directory()
        self.load_all_plugins()

    def load_all_plugins(self):
        self.plugins.clear()
        cfg = self.cm.config
        if not os.path.exists("./plugins"): return
        for file in os.listdir("./plugins"):
            if file.endswith(".py") and not file.startswith("__"):
                module_name = file[:-3]
                module_path = os.path.join("./plugins", file)
                try:
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    if spec and spec.loader:
                        module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module)
                        for name, cls in inspect.getmembers(module, inspect.isclass):
                            if cls.__module__ == module_name and hasattr(cls, "render_frame") and hasattr(cls, "get_settings_schema"):
                                instance = cls()
                                is_enabled = module_name in cfg.enabled_plugins
                                saved_params = cfg.plugin_parameters.get(module_name, {})
                                resolved_params = self._resolve_params(instance, saved_params)
                                self.plugins[module_name] = {
                                    "id": module_name,
                                    "name": getattr(instance, "name", module_name),
                                    "description": getattr(instance, "description", "Custom plugin"),
                                    "class_name": name,
                                    "instance": instance,
                                    "enabled": is_enabled,
                                    "params": resolved_params,
                                    "schema": instance.get_settings_schema()
                                }
                                print(f"[*] Registered Plugin: {name}")
                except Exception as e:
                    print(f"[*] Failed to import plugin {file}: {e}")
        for plug_id in self.plugins:
            if plug_id not in cfg.plugin_parameters:
                cfg.plugin_parameters[plug_id] = self.plugins[plug_id]["params"]
        self.cm.save_config()

    def _resolve_params(self, instance: Any, saved_params: Dict[str, Any]) -> Dict[str, Any]:
        resolved = {}
        schema = instance.get_settings_schema()
        for k, v in schema.items():
            resolved[k] = saved_params.get(k, v["default"])
        return resolved