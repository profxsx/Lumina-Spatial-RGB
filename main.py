"""
Lumina Main Entry Point
Launches the background FastAPI server on standard port 8000 and opens the browser.
"""

import os
import sys
import shutil
import webbrowser
import threading
import time

# --- Setup Writable Directory Context (Copies Project Assets to ~/.config/lumina) ---
base_dir = os.path.dirname(os.path.abspath(__file__))

home_dir = os.path.expanduser("~")
lumina_dir = os.path.join(home_dir, ".config", "lumina")
os.makedirs(lumina_dir, exist_ok=True)

# Copy default directories (effects, plugins, gifs) from local project to ~/.config/lumina
for folder in ["effects", "plugins", "gifs"]:
    src = os.path.join(base_dir, folder)
    dst = os.path.join(lumina_dir, folder)
    if os.path.exists(src):
        if not os.path.exists(dst):
            shutil.copytree(src, dst)
        else:
            for item in os.listdir(src):
                s_file = os.path.join(src, item)
                d_file = os.path.join(dst, item)
                if os.path.isfile(s_file) and not os.path.exists(d_file):
                    shutil.copy2(s_file, d_file)

# Inject ~/.config/lumina into sys.path so Python can dynamically import local files
sys.path.insert(0, lumina_dir)

# Shift active working directory of the process to the config path
os.chdir(lumina_dir)

# --- Standard Server Initialization ---
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI

import api.routes
from api.routes import router as api_router, ws_canvas_frame
from core.config import ConfigManager
from core.engine import EngineCore

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the lifecycle of the core engine alongside the FastAPI server.
    """
    try:
        config_manager = ConfigManager()
        engine = EngineCore(config_manager)
        api.routes.engine_ref = engine
        engine.start()
    except Exception as e:
        import traceback
        print("[*] Critical Error during Lumina Engine startup:")
        traceback.print_exc()
        raise e
    yield
    await engine.stop()

# Initialize FastAPI application
app = FastAPI(title="Lumina Spatial Studio", lifespan=lifespan)

# Allow CORS so that standard web pages can talk to localhost:8000
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.add_api_websocket_route("/ws/canvas_frame", ws_canvas_frame)

def main():
    host_addr = "127.0.0.1"
    host_port = 8000
    url = f"http://{host_addr}:{host_port}/"
    
    # Automatically trigger your default system browser (Firefox, Chrome, Brave, etc.) to open
    threading.Thread(target=lambda: (time.sleep(0.5), webbrowser.open(url)), daemon=True).start()
    
    print(f"[*] Active working directory: {os.getcwd()}")
    print(f"[*] Starting Lumina Spatial Core on {url}")
    uvicorn.run(app, host=host_addr, port=host_port, log_level="warning")

if __name__ == "__main__":
    main()