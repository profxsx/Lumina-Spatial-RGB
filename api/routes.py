"""
Lumina API Router Module
Handles all REST operations and packetized WebSocket telemetry streams.
"""

import os
import io
import json
import time
import base64
import asyncio
from typing import List, Dict, Any
from fastapi import APIRouter, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from PIL import Image
import numpy as np

from api.templates import INDEX_HTML
from audio.discovery import discover_system_audio_devices

router = APIRouter()

# Global core reference injected on start
engine_ref = None

class EffectSelectPayload(BaseModel):
    effect_name: str

class ParamUpdatePayload(BaseModel):
    key: str
    value: Any

class DeviceCoordsPayload(BaseModel):
    x: float
    y: float
    width: float
    height: float
    form_type: str
    active_profile: str = "procedural"
    custom_profiles: Dict[str, List[List[float]]] = None
    rotation: float = 0.0
    hidden_in_layout: bool = False

class DeviceOrderPayload(BaseModel):
    led_order: List[int]

class FavoritesUpdatePayload(BaseModel):
    favorites: List[str]

class SettingsUpdatePayload(BaseModel):
    openrgb_host: str
    openrgb_port: int
    target_fps: int
    canvas_width: int
    audio_mode: str
    audio_device_id: str
    audio_emulation: bool
    audio_noise_gate: float

class PluginTogglePayload(BaseModel):
    enabled: bool

class PluginParamPayload(BaseModel):
    key: str
    value: Any


@router.get("/", response_class=HTMLResponse)
def index_page():
    return HTMLResponse(content=INDEX_HTML)

@router.get("/api/config")
def get_config():
    return engine_ref.cm.config

@router.get("/api/effects")
def get_effects():
    return {
        "active": engine_ref.active_effect_name,
        "params": engine_ref.effect_params,
        "library": {name: eff.get_parameter_schema() for name, eff in engine_ref.effect_manager.effects.items()},
        "favorites": engine_ref.cm.config.favorited_effects
    }

@router.post("/api/effects/select")
async def select_effect(payload: EffectSelectPayload):
    await engine_ref.update_active_effect(payload.effect_name)
    return {"status": "ok", "active": engine_ref.active_effect_name, "params": engine_ref.effect_params}

@router.post("/api/effects/param")
async def update_param(payload: ParamUpdatePayload):
    await engine_ref.update_parameter(payload.key, payload.value)
    return {"status": "ok"}

@router.post("/api/effects/favorites")
def update_favorites(payload: FavoritesUpdatePayload):
    engine_ref.cm.config.favorited_effects = payload.favorites
    engine_ref.cm.save_config()
    return {"status": "ok"}

@router.get("/api/audio/devices")
def get_audio_devices():
    return discover_system_audio_devices()

@router.get("/api/gifs")
def list_gifs():
    result = []
    cfg = engine_ref.cm.config
    if os.path.exists("./gifs"):
        for file in os.listdir("./gifs"):
            if file.endswith(".gif"):
                display_name = cfg.gif_library_names.get(file, file.replace("_", " ").title()[:-4])
                result.append({
                    "id": file,
                    "name": display_name,
                    "active": file == cfg.active_gif_filename
                })
    return result

@router.post("/api/gifs/{filename}/rename")
def rename_gif_label(filename: str, payload: Dict[str, str]):
    if "name" not in payload:
        raise HTTPException(status_code=400, detail="Missing custom name field")
    engine_ref.cm.config.gif_library_names[filename] = payload["name"]
    engine_ref.cm.save_config()
    return {"status": "ok"}

@router.post("/api/gifs/{filename}/select")
async def select_active_gif(filename: str):
    if not os.path.exists(f"./gifs/{filename}"):
        raise HTTPException(status_code=404, detail="Target GIF not found")
    engine_ref.cm.config.active_gif_filename = filename
    engine_ref.cm.save_config()
    if "GifPlayer" in engine_ref.effect_manager.effects:
        engine_ref.effect_params["_active_gif_file"] = filename
        engine_ref.cm.config.effect_parameters["_active_gif_file"] = filename
        engine_ref.cm.save_config()
        engine_ref.effect_manager.effects["GifPlayer"].loaded = False
    return {"status": "ok"}

@router.delete("/api/gifs/{filename}")
def delete_gif_asset(filename: str):
    if filename == "target.gif":
        raise HTTPException(status_code=403, detail="Default alignment GIF cannot be deleted!")
    target_path = f"./gifs/{filename}"
    if os.path.exists(target_path): os.remove(target_path)
    if filename in engine_ref.cm.config.gif_library_names:
        del engine_ref.cm.config.gif_library_names[filename]
    if engine_ref.cm.config.active_gif_filename == filename:
        engine_ref.cm.config.active_gif_filename = "target.gif"
        if "GifPlayer" in engine_ref.effect_manager.effects:
            engine_ref.effect_params["_active_gif_file"] = "target.gif"
            engine_ref.cm.config.effect_parameters["_active_gif_file"] = "target.gif"
            engine_ref.effect_manager.effects["GifPlayer"].loaded = False
    engine_ref.cm.save_config()
    return {"status": "ok"}

@router.post("/api/upload/gif")
async def upload_gif_file(request: Request):
    os.makedirs("./gifs", exist_ok=True)
    safe_filename = f"upload_{int(time.time())}.gif"
    gif_path = f"./gifs/{safe_filename}"
    try:
        contents = await request.body()
        if not contents: raise HTTPException(status_code=400, detail="Empty request payload received")
        with open(gif_path, "wb") as f: f.write(contents)
        engine_ref.cm.config.gif_library_names[safe_filename] = f"Upload ({time.strftime('%H:%M:%S')})"
        engine_ref.cm.config.active_gif_filename = safe_filename
        if "GifPlayer" in engine_ref.effect_manager.effects:
            engine_ref.effect_params["_active_gif_file"] = safe_filename
            engine_ref.cm.config.effect_parameters["_active_gif_file"] = safe_filename
            engine_ref.effect_manager.effects["GifPlayer"].loaded = False
        engine_ref.cm.save_config()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process media file: {e}")

@router.get("/api/plugins")
def get_plugins():
    result = []
    for plug_id, data in engine_ref.plugin_manager.plugins.items():
        result.append({
            "id": plug_id, "name": data["name"], "description": data["description"],
            "enabled": data["enabled"], "params": data["params"], "schema": data["schema"]
        })
    return result

@router.post("/api/plugins/{plugin_id}/toggle")
def toggle_plugin(plugin_id: str, payload: PluginTogglePayload):
    if plugin_id not in engine_ref.plugin_manager.plugins:
        raise HTTPException(status_code=404, detail="Plugin not found")
    engine_ref.plugin_manager.plugins[plugin_id]["enabled"] = payload.enabled
    cfg = engine_ref.cm.config
    if payload.enabled and plugin_id not in cfg.enabled_plugins: cfg.enabled_plugins.append(plugin_id)
    elif not payload.enabled and plugin_id in cfg.enabled_plugins: cfg.enabled_plugins.remove(plugin_id)
    engine_ref.cm.save_config()
    return {"status": "ok", "enabled": payload.enabled}

@router.post("/api/plugins/{plugin_id}/param")
def update_plugin_param(plugin_id: str, payload: PluginParamPayload):
    if plugin_id not in engine_ref.plugin_manager.plugins:
         raise HTTPException(status_code=404, detail="Plugin not found")
    engine_ref.plugin_manager.plugins[plugin_id]["params"][payload.key] = payload.value
    cfg = engine_ref.cm.config
    if plugin_id not in cfg.plugin_parameters: cfg.plugin_parameters[plugin_id] = {}
    cfg.plugin_parameters[plugin_id][payload.key] = payload.value
    engine_ref.cm.save_config()
    return {"status": "ok"}

@router.get("/api/devices")
def list_devices():
    devs = []
    for d in engine_ref.devices:
        dev_data = {
            "id": d.device_id, "name": d.name, "led_count": d.led_count, "enabled": d.enabled,
            "form_type": d.form_type, "x": d.x, "y": d.y, "width": d.width, "height": d.height,
            "rotation": getattr(d, "rotation", 0.0), "hidden_in_layout": getattr(d, "hidden_in_layout", False),
            "active_profile": d.active_profile, "custom_profiles": d.custom_profiles,
            "coordinates": d.coordinates.tolist(), "local_coords": d.local_coords.tolist(), "led_order": d.led_order_mapping.tolist()
        }
        
        if hasattr(d, "last_sent_colors"):
            if hasattr(d, "identify_until") and time.time() < d.identify_until:
                pulse = int(time.time() * 8) % 2
                if pulse == 0:
                    dev_data["demo_colors"] = [[0, 0, 255]] * d.led_count
                else:
                    dev_data["demo_colors"] = [[0, 0, 0]] * d.led_count
            else:
                dev_data["demo_colors"] = d.last_sent_colors
        devs.append(dev_data)
    return devs

@router.post("/api/devices/{device_id}/toggle")
def toggle_device(device_id: str):
    for d in engine_ref.devices:
        if d.device_id == device_id:
            d.enabled = not d.enabled
            engine_ref.cm.config.devices_layout[d.device_id] = d.export_layout()
            engine_ref.cm.save_config()
            return {"status": "ok", "enabled": d.enabled}
    raise HTTPException(status_code=404, detail="Device not found")

@router.post("/api/devices/{device_id}/bounds")
def update_device_bounds(device_id: str, payload: DeviceCoordsPayload):
    for d in engine_ref.devices:
        if d.device_id == device_id:
            d.x = payload.x
            d.y = payload.y
            d.width = payload.width
            d.height = payload.height
            d.form_type = payload.form_type
            d.active_profile = payload.active_profile
            d.rotation = payload.rotation
            d.hidden_in_layout = payload.hidden_in_layout
            if payload.custom_profiles is not None: d.custom_profiles = payload.custom_profiles
            d._build_local_layout()
            d.recompute_global_coordinates()
            engine_ref.cm.config.devices_layout[d.device_id] = d.export_layout()
            engine_ref.cm.save_config()
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Device not found")

@router.post("/api/devices/{device_id}/reorder")
def update_device_ordering(device_id: str, payload: DeviceOrderPayload):
    for d in engine_ref.devices:
        if d.device_id == device_id:
            if len(payload.led_order) != d.led_count: raise HTTPException(status_code=400, detail="Size mismatch")
            d.led_order_mapping = np.array(payload.led_order, dtype=np.int32)
            engine_ref.cm.config.devices_layout[d.device_id] = d.export_layout()
            engine_ref.cm.save_config()
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Device not found")

@router.post("/api/devices/{device_id}/auto_order")
def auto_order_device(device_id: str, mode: str):
    for d in engine_ref.devices:
        if d.device_id == device_id:
            coords = d.local_coords
            if mode == "left_to_right": new_order = np.argsort(coords[:, 0])
            elif mode == "top_to_bottom": new_order = np.argsort(coords[:, 1])
            elif mode == "clockwise":
                center = np.mean(coords, axis=0)
                angles = np.arctan2(coords[:, 1] - center[1], coords[:, 0] - center[0])
                new_order = np.argsort(angles)
            else: raise HTTPException(status_code=400, detail="Invalid sorting heuristic")
            d.led_order_mapping = new_order.astype(np.int32)
            engine_ref.cm.config.devices_layout[d.device_id] = d.export_layout()
            engine_ref.cm.save_config()
            return {"status": "ok", "led_order": d.led_order_mapping.tolist()}
    raise HTTPException(status_code=404, detail="Device not found")

@router.post("/api/devices/{device_id}/highlight/{led_index}")
def set_device_highlight(device_id: str, led_index: int):
    engine_ref.highlight_device_id = device_id
    engine_ref.highlight_led_index = led_index
    return {"status": "ok"}

@router.post("/api/devices/highlight/clear")
def clear_device_highlight():
    engine_ref.highlight_device_id = None
    engine_ref.highlight_led_index = -1
    return {"status": "ok"}

@router.post("/api/devices/{device_id}/identify")
def identify_device(device_id: str):
    for d in engine_ref.devices:
        if d.device_id == device_id:
            d.identify_until = time.time() + 3.0
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Device not found")

@router.post("/api/engine/restart")
async def restart_engine():
    """Triggers a clean core engine restart safely inside the ASGI loop."""
    if engine_ref:
        await engine_ref.stop()
        engine_ref.start()
    return {"status": "ok"}

@router.post("/api/settings")
async def update_settings(payload: SettingsUpdatePayload):
    engine_ref.cm.config.openrgb_host = payload.openrgb_host
    engine_ref.cm.config.openrgb_port = payload.openrgb_port
    engine_ref.cm.config.target_fps = payload.target_fps
    engine_ref.cm.config.canvas_width = payload.canvas_width
    engine_ref.cm.config.audio_mode = payload.audio_mode
    engine_ref.cm.config.audio_device_id = payload.audio_device_id
    engine_ref.cm.config.audio_emulation = payload.audio_emulation
    engine_ref.cm.config.audio_noise_gate = payload.audio_noise_gate
    engine_ref.cm.save_config()
    await engine_ref.canvas.resize(payload.canvas_width)
    await engine_ref.stop()
    engine_ref.start()
    return {"status": "ok"}

@router.post("/api/devices/{device_id}/profile/{profile_name}")
def save_named_layout_profile(device_id: str, profile_name: str, payload: List[List[float]]):
    for d in engine_ref.devices:
        if d.device_id == device_id:
            d.custom_profiles[profile_name] = payload
            d.active_profile = f"profile:{profile_name}"
            d.recompute_global_coordinates()
            engine_ref.cm.config.devices_layout[d.device_id] = d.export_layout()
            engine_ref.cm.save_config()
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Device not found")

@router.post("/api/devices/{device_id}/profile/{profile_name}/select")
def select_named_profile(device_id: str, profile_name: str):
    for d in engine_ref.devices:
        if d.device_id == device_id:
            if profile_name == "procedural": d.active_profile = "procedural"
            else:
                target_key = profile_name.replace("profile:", "")
                if target_key not in d.custom_profiles: raise HTTPException(status_code=404, detail="Target profile key not found")
                d.active_profile = f"profile:{target_key}"
            d.recompute_global_coordinates()
            engine_ref.cm.config.devices_layout[d.device_id] = d.export_layout()
            engine_ref.cm.save_config()
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Device not found")

@router.delete("/api/devices/{device_id}/profile/{profile_name}")
def delete_named_profile(device_id: str, profile_name: str):
    for d in engine_ref.devices:
        if d.device_id == device_id:
            if profile_name in d.custom_profiles: del d.custom_profiles[profile_name]
            if d.active_profile == f"profile:{profile_name}": d.active_profile = "procedural"
            d.recompute_global_coordinates()
            engine_ref.cm.config.devices_layout[d.device_id] = d.export_layout()
            engine_ref.cm.save_config()
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Device not found")

import subprocess

@router.post("/api/open-dir/{folder_name}")
def open_directory_in_file_manager(folder_name: str):
    """Launches the standard Linux file manager pointing to the active effects/plugins folders."""
    # Since we use os.chdir(lumina_dir) on startup, relative paths automatically
    # map to write-enabled system folders (~/.config/lumina/effects etc.)
    target_path = os.path.abspath(f"./{folder_name}")
    os.makedirs(target_path, exist_ok=True)
    
    try:
        # Launch default file manager using standard xdg-open
        subprocess.Popen(["xdg-open", target_path])
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to open directory: {e}")

async def ws_canvas_frame(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            async with engine_ref.canvas._lock:
                raw_rgb = engine_ref.canvas.buffer.copy()
            
            img = Image.fromarray(raw_rgb)
            fp = io.BytesIO()
            img.save(fp, format="JPEG", quality=60)
            data_bytes = fp.getvalue()
            img_b64 = base64.b64encode(data_bytes).decode("utf-8")
            
            payload = {
                "image": img_b64,
                "audio": {
                    "lows": engine_ref.audio.lows,
                    "mids": engine_ref.audio.mids,
                    "highs": engine_ref.audio.highs
                }
            }
            await websocket.send_text(json.dumps(payload))
            await asyncio.sleep(1.0 / engine_ref.cm.config.target_fps)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"[*] WebSocket pipeline interrupted: {e}")