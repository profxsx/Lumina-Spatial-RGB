"""
Lumina Frontend Extractor Utility
Extracts INDEX_HTML from api/templates.py and formats it for Tauri static assets.
"""

import os
from api.templates import INDEX_HTML

def main():
    os.makedirs("frontend", exist_ok=True)
    html = INDEX_HTML

    # 1. Convert relative API paths to absolute backend server URLs
    html = html.replace("fetch('/api/", "fetch('http://127.0.0.1:8000/api/")
    html = html.replace("fetch(`/api/", "fetch(`http://127.0.0.1:8000/api/")
    html = html.replace("url: '/api/", "url: 'http://127.0.0.1:8000/api/")

    # 2. Convert WebSocket host references to point to localhost:8000
    html = html.replace('"ws://" + loc.host + "/ws/canvas_frame"', '"ws://127.0.0.1:8000/ws/canvas_frame"')

    # 3. Inject Tauri native window actions to the custom titlebar buttons
    old_bridges = """
            // --- Native Titlebar Bridges ---
            function minimizeWindow() {
                if (window.pywebview && window.pywebview.api) {
                    window.pywebview.api.minimize();
                }
            }
            function maximizeWindow() {
                if (window.pywebview && window.pywebview.api) {
                    window.pywebview.api.maximize();
                }
            }
            function closeWindow() {
                if (window.pywebview && window.pywebview.api) {
                    window.pywebview.api.close();
                }
            }
"""

    tauri_bridges = """
            // --- Native Tauri v2 Titlebar Bridges ---
            function minimizeWindow() {
                if (window.__TAURI__) {
                    window.__TAURI__.core.invoke('minimize_window');
                }
            }
            function maximizeWindow() {
                if (window.__TAURI__) {
                    window.__TAURI__.core.invoke('maximize_window');
                }
            }
            function closeWindow() {
                if (window.__TAURI__) {
                    window.__TAURI__.core.invoke('close_window');
                }
            }
"""
    html = html.replace(old_bridges, tauri_bridges)

    # 4. Remove the pywebview custom resize handle element if present
    old_resize_handle = """        <!-- Custom Frame Resize Handle -->
        <div id="window-resize-handle" class="absolute bottom-0 right-0 h-4 w-4 cursor-se-resize z-50 flex items-end justify-end p-0.5" onmousedown="onResizeHandleMouseDown(event)">
            <svg class="h-3 w-3 text-slate-600 hover:text-cyan-400" viewBox="0 0 10 10" fill="currentColor">
                <path d="M10,0 L0,10 L10,10 Z" />
            </svg>
        </div>"""
    html = html.replace(old_resize_handle, "")

    # 5. Apply native tauri drag region attribute to the custom header
    html = html.replace('pywebview-drag-region', 'data-tauri-drag-region')

    with open("frontend/index.html", "w") as f:
        f.write(html)
    print("[*] Successfully extracted static assets to frontend/index.html")

if __name__ == "__main__":
    main()