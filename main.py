"""
Lumina Main Entry Point
Launches the background FastAPI server on standard port 8000.
"""

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
    # 1. Instantiate the Configuration Manager
    config_manager = ConfigManager()

    # 2. Instantiate the core state engine, passing the required config manager
    engine = EngineCore(config_manager)
    
    # 3. Inject the reference into the REST API routing context
    api.routes.engine_ref = engine
    
    # 4. Spin up the background loop
    engine.start()
    
    yield
    
    # 5. Clean shutdown on server exit
    await engine.stop()

# Initialize FastAPI application
app = FastAPI(title="Lumina Spatial Studio", lifespan=lifespan)

# Allow CORS so that Tauri's assets can talk to localhost:8000
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
    print(f"[*] Starting Lumina Spatial Core on http://{host_addr}:{host_port}")
    uvicorn.run(app, host=host_addr, port=host_port, log_level="warning")

if __name__ == "__main__":
    main()