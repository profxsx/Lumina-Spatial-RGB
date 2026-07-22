"""
Lumina Web Portal Templates Module
Stores raw HTML and responsive JavaScript frameworks for the calibration interface.
"""

INDEX_HTML = r'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Lumina Control Panel</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            body {
                background-color: #050811;
                color: #e2e8f0;
                font-family: ui-sans-serif, system-ui, sans-serif;
            }
            .glass-panel {
                background: rgba(13, 19, 35, 0.7);
                backdrop-filter: blur(14px);
                border: 1px solid rgba(255, 255, 255, 0.06);
            }
            .cyber-tab {
                border-bottom: 2px solid transparent;
            }
            .cyber-tab.active {
                border-bottom: 2px solid #ec4899;
                color: #ec4899;
            }
            input[type="range"] {
                -webkit-appearance: none;
                background: #1e293b;
            }
            input[type="range"]::-webkit-slider-thumb {
                -webkit-appearance: none;
                height: 12px;
                width: 12px;
                border-radius: 50%;
                background: #06b6d4;
                cursor: pointer;
                box-shadow: 0 0 10px #06b6d4;
            }
            ::-webkit-scrollbar { width: 6px; }
            ::-webkit-scrollbar-track { background: rgba(0,0,0,0.1); }
            ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 3px; }
            ::-webkit-scrollbar-thumb:hover { background: #06b6d4; }

            /* Modern Select Dropdown Styles (Bypasses Native GTK Theme) */
            select {
                -webkit-appearance: none !important;
                -moz-appearance: none !important;
                appearance: none !important;
                background-image: url("data:image/svg+xml;charset=UTF-8,%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2024%2024'%20fill='none'%20stroke='%2306b6d4'%20stroke-width='2'%20stroke-linecap='round'%20stroke-linejoin='round'%3E%3Cpolyline%20points='6%209%2012%2015%2018%209'%3E%3C/polyline%3E%3C/svg%3E") !important;
                background-repeat: no-repeat !important;
                background-position: right 0.75rem center !important;
                background-size: 1em !important;
                padding-right: 2.25rem !important;
                background-color: #0d1527 !important;
                border: 1px solid #1e293b !important;
                color: #94a3b8 !important;
                border-radius: 0.375rem !important;
            }
            select:focus {
                border-color: #06b6d4 !important;
                color: #e2e8f0 !important;
                outline: none !important;
            }
            select option {
                background-color: #0d1527 !important;
                color: #e2e8f0 !important;
                padding: 8px !important;
            }
        </style>
    </head>
    <body class="h-screen w-screen overflow-hidden flex flex-col font-sans select-none relative">

        <!-- Header (Custom Window Titlebar) -->
        <header id="titlebar" class="h-16 border-b border-slate-900 bg-slate-950/80 backdrop-blur-md flex items-center justify-between px-6 z-10 select-none cursor-default">
            <div class="flex items-center gap-3">
                <div class="h-8 w-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-pink-500 flex items-center justify-center animate-pulse">
                    <i class="fa-solid fa-wand-magic-sparkles text-slate-950 text-sm"></i>
                </div>
                <div>
                    <h1 class="text-md font-bold tracking-wider text-slate-100 uppercase">Lumina <span class="text-cyan-400 font-black text-xs tracking-tighter">Spatial Studio</span></h1>
                    <p class="text-[9px] text-slate-500 font-mono tracking-widest uppercase">Arch Linux Edition // V4.10</p>
                </div>
            </div>

            <!-- Tab Navigation Control Bar -->
            <nav class="flex gap-6 h-full items-center text-xs font-mono tracking-wider uppercase font-bold text-slate-400">
                <button onclick="switchTab('layout')" id="tab-btn-layout" class="cyber-tab h-full px-2 transition-all flex items-center gap-2 hover:text-slate-200">
                    <i class="fa-solid fa-map-location-dot"></i> Layout Canvas
                </button>
                <button onclick="switchTab('shaders')" id="tab-btn-shaders" class="cyber-tab h-full px-2 transition-all flex items-center gap-2 hover:text-slate-200">
                    <i class="fa-solid fa-wand-magic-sparkles"></i> Effects
                </button>
                <button onclick="switchTab('devices')" id="tab-btn-devices" class="cyber-tab h-full px-2 transition-all flex items-center gap-2 hover:text-slate-200">
                    <i class="fa-solid fa-microchip"></i> Hardware
                </button>
                <button onclick="switchTab('plugins')" id="tab-btn-plugins" class="cyber-tab h-full px-2 transition-all flex items-center gap-2 hover:text-slate-200">
                    <i class="fa-solid fa-puzzle-piece"></i> Plugins
                </button>
                <button onclick="switchTab('settings')" id="tab-btn-settings" class="cyber-tab h-full px-2 transition-all flex items-center gap-2 hover:text-slate-200">
                    <i class="fa-solid fa-sliders"></i> Settings
                </button>
            </nav>

            <!-- Status Indicator & Window Actions Cluster -->
            <div class="flex items-center gap-4 text-xs font-mono">
                <span id="active-fps-display" class="text-slate-500">Connecting to Core...</span>
                
                <!-- Modern Frameless Custom Controls -->
                <div class="flex items-center gap-3 border-l border-slate-800 pl-4">
                    <button onclick="minimizeWindow()" class="text-slate-400 hover:text-cyan-400 transition-colors py-1 cursor-pointer" title="Minimize Window">
                        <i class="fa-solid fa-minus text-xs"></i>
                    </button>
                    <button onclick="maximizeWindow()" class="text-slate-400 hover:text-cyan-400 transition-colors py-1 cursor-pointer" title="Maximize Window">
                        <i class="fa-solid fa-expand text-xs"></i>
                    </button>
                    <button onclick="closeWindow()" class="text-slate-400 hover:text-pink-500 transition-colors py-1 cursor-pointer" title="Close / Hide to Tray">
                        <i class="fa-solid fa-xmark text-sm font-bold"></i>
                    </button>
                </div>
            </div>
        </header>

        <!-- Dynamic Content Tabs -->
        <div class="flex-1 flex overflow-hidden">

            <!-- TAB 1: Draggable Workspace Layout Viewport -->
            <div id="tab-view-layout" class="flex-1 flex overflow-hidden">
                <!-- Workspace Side Options Column (Layout Settings) -->
                <aside class="w-80 border-r border-slate-900 bg-slate-950/30 p-4 flex flex-col gap-4 overflow-y-auto z-10">
                    
                    <!-- Section A: Device Directory -->
                    <div>
                        <h2 class="text-xs font-bold font-mono tracking-widest uppercase text-slate-400 mb-2">Device Directory</h2>
                        <div id="layout-device-list" class="flex flex-col gap-2 max-h-48 overflow-y-auto pr-1">
                            <!-- Populated dynamically via JS -->
                        </div>
                    </div>

                    <!-- Section B: Selected Device Inspector -->
                    <div id="device-inspector-panel" class="hidden flex flex-col gap-3">
                        <h2 class="text-xs font-bold font-mono tracking-widest uppercase text-slate-400">Device Inspector</h2>
                        <div class="glass-panel p-4 rounded-xl border border-slate-900 flex flex-col gap-4">
                            <div class="flex items-center justify-between border-b border-slate-900 pb-2">
                                <span id="inspect-device-name" class="text-xs font-bold font-mono uppercase text-slate-200 truncate pr-1">No Device Selected</span>
                                <button onclick="identifySelectedDevice()" class="px-2 py-0.5 bg-blue-600 hover:bg-blue-500 text-white rounded font-mono text-[9px] font-bold uppercase transition-all flex items-center gap-1" title="Identify (Blink Blue)">
                                    <i class="fa-solid fa-lightbulb text-[9px]"></i> Identify
                                </button>
                            </div>
                            
                            <div class="flex flex-col gap-3 font-mono text-[10px]">
                                <!-- Position X -->
                                <div class="flex flex-col gap-1">
                                    <div class="flex justify-between">
                                        <label class="text-slate-400">Position X</label>
                                        <span id="inspect-val-x" class="text-cyan-400 font-bold">0.00</span>
                                    </div>
                                    <input type="range" id="inspect-range-x" min="0.0" max="1.0" step="0.01" class="w-full" oninput="updateInspectorDeviceBounds()">
                                </div>
                                <!-- Position Y -->
                                <div class="flex flex-col gap-1">
                                    <div class="flex justify-between">
                                        <label class="text-slate-400">Position Y</label>
                                        <span id="inspect-val-y" class="text-cyan-400 font-bold">0.00</span>
                                    </div>
                                    <input type="range" id="inspect-range-y" min="0.0" max="1.0" step="0.01" class="w-full" oninput="updateInspectorDeviceBounds()">
                                </div>
                                <!-- Width Scale -->
                                <div class="flex flex-col gap-1">
                                    <div class="flex justify-between">
                                        <label class="text-slate-400">Width Scale</label>
                                        <span id="inspect-val-w" class="text-cyan-400 font-bold">0.10</span>
                                    </div>
                                    <input type="range" id="inspect-range-w" min="0.05" max="1.0" step="0.01" class="w-full" oninput="updateInspectorDeviceBounds()">
                                </div>
                                <!-- Height Scale -->
                                <div class="flex flex-col gap-1">
                                    <div class="flex justify-between">
                                        <label class="text-slate-400">Height Scale</label>
                                        <span id="inspect-val-h" class="text-cyan-400 font-bold">0.10</span>
                                    </div>
                                    <input type="range" id="inspect-range-h" min="0.05" max="1.0" step="0.01" class="w-full" oninput="updateInspectorDeviceBounds()">
                                </div>
                                <!-- Rotation -->
                                <div class="flex flex-col gap-1">
                                    <div class="flex justify-between">
                                        <label class="text-slate-400">Rotation Angle</label>
                                        <span id="inspect-val-rot" class="text-cyan-400 font-bold">0°</span>
                                    </div>
                                    <input type="range" id="inspect-range-rot" min="0" max="360" step="5" class="w-full" oninput="updateInspectorDeviceBounds()">
                                </div>
                                <!-- Hide in Layout Toggle -->
                                <div class="flex items-center justify-between pt-2 border-t border-slate-900/60">
                                    <label class="text-slate-400">Hide on Canvas</label>
                                    <button id="inspect-btn-hide" onclick="toggleInspectorDeviceHide()" class="text-slate-600 text-lg">
                                        <i class="fa-solid fa-toggle-off"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Section C: Canvas Options -->
                    <div>
                        <h2 class="text-xs font-bold font-mono tracking-widest uppercase text-slate-400 mb-2">Canvas Options</h2>
                        <div class="glass-panel p-4 rounded-xl border border-slate-900 flex flex-col gap-4">
                            <div class="flex items-center gap-2 border-b border-slate-900 pb-2">
                                <i class="fa-solid fa-arrows-alt text-cyan-400"></i>
                                <span class="text-xs font-bold font-mono uppercase text-slate-200">Node Calibration</span>
                            </div>
                            <div class="flex flex-col gap-2 font-mono text-[10px]">
                                <p class="text-slate-500 leading-normal mb-2">Switch layout edit targets to calibrate coordinate grids or fine-tune individual LED pins.</p>
                                <div class="flex flex-col gap-1.5">
                                    <label class="text-slate-400">Calibrator Targeting</label>
                                    <select id="layout-edit-mode" onchange="toggleLayoutCalibratorMode(this.value)" class="w-full bg-slate-900 border border-slate-800 rounded py-1.5 px-3 outline-none text-slate-300">
                                        <option value="bounds">Device Boundaries (Standard Block Drag)</option>
                                        <option value="nodes" disabled>Fine-Grain Pins (Use Hardware Modal Instead)</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    </div>
                </aside>

                <div class="flex-1 flex flex-col bg-[#03050a] p-6 relative">
                    <div class="flex items-center justify-between mb-4 font-mono text-[11px] text-slate-400">
                        <span><i class="fa-solid fa-expand mr-2"></i>Canvas is locked to panoramic widescreen (16:10 standard)</span>
                        <div class="flex items-center gap-2">
                            <span>Overlay Opacity:</span>
                            <input id="ref-opacity" type="range" min="0.0" max="1.0" step="0.1" value="0.3" class="w-16" oninput="updateRefOpacity(this.value)">
                        </div>
                    </div>
                    <!-- Layout Grid Viewport -->
                    <div class="flex-1 relative rounded-xl border border-slate-900/80 bg-slate-950/20 overflow-hidden shadow-inner flex items-center justify-center" id="canvas-workspace" onclick="clearWorkspaceSelection(event)">
                        <canvas id="stream-preview" class="absolute w-full h-full object-cover select-none pointer-events-none opacity-85 z-0" style="filter: blur(2px);"></canvas>
                        <div class="absolute inset-0 bg-[linear-gradient(to_right,#0d1324_1px,transparent_1px),linear-gradient(to_bottom,#0d1324_1px,transparent_1px)] bg-[size:32px_32px] pointer-events-none opacity-60 z-10"></div>
                        <div id="workspace-elements-root" class="absolute inset-0 z-20"></div>
                    </div>
                </div>
            </div>

            <!-- TAB 2: Effects Selection & Favorites Manager -->
            <div id="tab-view-shaders" class="flex-1 flex overflow-hidden hidden">
                <!-- Sidebar Parameters Card -->
                <aside class="w-80 border-r border-slate-900 bg-slate-950/30 p-4 flex flex-col gap-4 overflow-y-auto">
                    
                    <!-- Dynamic GIF Library Panel (Placed on the left of effect configurations) -->
                    <div id="shader-gif-panel" class="hidden flex flex-col gap-3">
                        <h2 class="text-xs font-bold font-mono tracking-widest uppercase text-slate-400">GIF Library Manager</h2>
                        <div class="glass-panel p-3 rounded-xl border border-slate-900 flex flex-col gap-3">
                            <input type="text" id="gif-library-search" oninput="onGifSearch(this.value)" placeholder="Search animations..." class="w-full bg-slate-950 border border-slate-800 rounded py-1 px-2.5 text-[10px] text-slate-300 outline-none focus:border-cyan-500 font-mono font-bold">
                            <div id="gif-library-list" class="flex flex-col gap-2 max-h-48 overflow-y-auto border-b border-slate-900 pb-2"></div>
                            
                            <!-- Drag-and-Drop Custom GIF File Upload Panel -->
                            <div id="effect-upload-container" class="flex flex-col gap-1.5 text-[10px] font-mono">
                                <label class="text-slate-400 uppercase tracking-widest text-[9px]"><i class="fa-solid fa-upload"></i> Upload Custom GIF</label>
                                <div class="border border-dashed border-slate-800 rounded-lg p-3 text-center cursor-pointer hover:border-pink-500/40 transition-colors"
                                     onclick="document.getElementById('gif-uploader-input').click()"
                                     ondragover="event.preventDefault()"
                                     ondrop="handleGifDrop(event)">
                                    <span class="text-slate-500 text-[9px]">Drop .gif file here or click to browse</span>
                                    <input type="file" id="gif-uploader-input" accept="image/gif" class="hidden" onchange="handleGifSelect(this)">
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Sidebar Parameters Header & File Reveal trigger -->
                    <div class="flex flex-col gap-4">
                        <div class="flex items-center justify-between text-xs font-mono tracking-widest uppercase text-slate-400">
                            <span>Effect Controls</span>
                            <button onclick="openDirectory('effects')" class="px-2 py-1 border border-cyan-500/20 bg-cyan-500/5 hover:bg-cyan-500 hover:text-slate-950 text-cyan-400 font-mono text-[9px] rounded transition-all" title="Open Effects Directory">
                                <i class="fa-solid fa-folder-open"></i> Open Dir
                            </button>
                        </div>
                        <div class="glass-panel p-4 rounded-xl border border-slate-900 flex flex-col gap-4">
                            <div class="flex items-center gap-2 border-b border-slate-900 pb-2">
                                <i class="fa-solid fa-palette text-cyan-400"></i>
                                <span id="active-shader-title" class="text-xs font-bold font-mono uppercase text-slate-200">No Active Effect</span>
                            </div>
                            <div id="params-container" class="flex flex-col gap-4"></div>
                        </div>
                    </div>
                </aside>
                <!-- Main Grid Options Content -->
                <main class="flex-1 bg-[#03050a] p-6 flex flex-col gap-4 overflow-y-auto">
                    <div class="flex items-center gap-4">
                        <!-- Search Box -->
                        <div class="relative flex-1 max-w-md">
                            <i class="fa-solid fa-magnifying-glass absolute left-3 top-2.5 text-slate-500 text-xs"></i>
                            <input type="text" id="effect-search" oninput="renderEffectsList()" placeholder="Search effects (e.g. Wave, Pulse...)" class="w-full bg-slate-950 border border-slate-800 rounded-lg py-2 pl-9 pr-4 text-xs text-slate-300 outline-none focus:border-cyan-500">
                        </div>
                    </div>
                    
                    <!-- Shader Matrix Cards -->
                    <div id="effects-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>
                </main>
            </div>

            <!-- TAB 3: Plugins Manager -->
            <div id="tab-view-plugins" class="flex-1 flex overflow-hidden hidden">
                <!-- Sidebar Parameters Card -->
                <aside class="w-80 border-r border-slate-900 bg-slate-950/30 p-4 flex flex-col gap-4 overflow-y-auto">
                    <!-- Sidebar Parameters Header & File Reveal trigger -->
                    <div class="flex flex-col gap-4">
                        <div class="flex items-center justify-between text-xs font-mono tracking-widest uppercase text-slate-400">
                            <span>Plugin Settings</span>
                            <button onclick="openDirectory('plugins')" class="px-2 py-1 border border-pink-500/20 bg-pink-500/5 hover:bg-pink-500 hover:text-slate-950 text-pink-500 font-mono text-[9px] rounded transition-all" title="Open Plugins Directory">
                                <i class="fa-solid fa-folder-open"></i> Open Dir
                            </button>
                        </div>
                        <div class="glass-panel p-4 rounded-xl border border-slate-900 flex flex-col gap-4">
                            <div class="flex items-center gap-2 border-b border-slate-900 pb-2">
                                <i class="fa-solid fa-sliders text-pink-500"></i>
                                <span id="active-plugin-title" class="text-xs font-bold font-mono uppercase text-slate-200">Select a Plugin</span>
                            </div>
                            <div id="plugin-params-container" class="flex flex-col gap-4">
                                <p class="text-[10px] text-slate-500 font-mono text-center py-4">Click "Config" on an enabled plugin to modify its settings.</p>
                            </div>
                        </div>
                    </div>
                </aside>
                <!-- Main Grid Options Content -->
                <main class="flex-1 bg-[#03050a] p-6 flex flex-col gap-4 overflow-y-auto">
                    <h2 class="text-xs font-bold font-mono tracking-widest uppercase text-slate-400">Discovered Extensions</h2>
                    <div id="plugins-grid" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"></div>
                </main>
            </div>

            <!-- TAB 4: Device Calibration Index Ordering -->
            <div id="tab-view-devices" class="flex-1 flex overflow-hidden hidden">
                <main class="flex-1 bg-[#03050a] p-6 flex flex-col gap-4 overflow-y-auto">
                    <h2 class="text-xs font-bold font-mono tracking-widest uppercase text-slate-400">Active Controllers & Modules</h2>
                    <div id="hardware-cards-container" class="grid grid-cols-1 md:grid-cols-2 gap-4"></div>
                </main>
            </div>

            <!-- TAB 5: Engine Global Settings Configuration -->
            <div id="tab-view-settings" class="flex-1 flex items-center justify-center bg-[#03050a] p-6 overflow-y-auto hidden">
                <div class="glass-panel p-6 rounded-xl border border-slate-800 w-full max-w-md shadow-2xl flex flex-col gap-5">
                    <h2 class="text-sm font-bold font-mono tracking-wider uppercase text-slate-200 border-b border-slate-900 pb-3">
                        <i class="fa-solid fa-gears text-cyan-400 mr-2"></i> System Configuration
                    </h2>
                    
                    <div class="flex flex-col gap-4 text-xs font-mono">
                        <div class="flex flex-col gap-1.5">
                            <label class="text-slate-400">OpenRGB Server Host</label>
                            <input type="text" id="setting-host" class="w-full bg-slate-900 border border-slate-700 rounded-md py-2 px-3 text-slate-200 outline-none focus:border-cyan-500">
                        </div>
                        <div class="flex flex-col gap-1.5">
                            <label class="text-slate-400">OpenRGB Server Port</label>
                            <input type="number" id="setting-port" class="w-full bg-slate-900 border border-slate-700 rounded-md py-2 px-3 text-slate-200 outline-none focus:border-cyan-500">
                        </div>
                        
                        <!-- Cascading Audio Settings Dropdowns -->
                        <div class="flex flex-col gap-1.5 border-t border-slate-900/60 pt-3">
                            <label class="text-slate-400">Audio capture Mode</label>
                            <select id="setting-audio-mode" onchange="onAudioModeChange(this.value)" class="w-full bg-slate-900 border border-slate-700 rounded-md py-2 px-3 text-slate-200 outline-none focus:border-cyan-500">
                                <option value="input">Input (Microphones / Physical Inputs)</option>
                                <option value="output">Output (System Sound Monitors / Loopback)</option>
                            </select>
                        </div>
                        <div class="flex flex-col gap-1.5">
                            <label class="text-slate-400">Target Sound Interface</label>
                            <select id="setting-audio-device" class="w-full bg-slate-900 border border-slate-700 rounded-md py-2 px-3 text-slate-200 outline-none focus:border-cyan-500"></select>
                        </div>
                        
                        <!-- Calibration Audio Noise Gate and Demo Toggles -->
                        <div class="flex flex-col gap-1.5 border-t border-slate-900/60 pt-3">
                            <div class="flex items-center justify-between">
                                <label class="text-slate-400">Mute Real Audio (Enable Demo waves)</label>
                                <button onclick="toggleAudioEmulation()" id="setting-audio-emulation-btn" class="text-cyan-400 text-lg">
                                    <i class="fa-solid fa-toggle-off"></i>
                                </button>
                            </div>
                        </div>
                        <div class="flex flex-col gap-1.5">
                            <div class="flex justify-between">
                                <label class="text-slate-400">Noise Gate Threshold</label>
                                <span id="val-noise-gate" class="text-pink-500 font-bold">0.02</span>
                            </div>
                            <input type="range" id="setting-noise-gate" min="0.00" max="0.20" step="0.01" value="0.02" class="w-full" oninput="document.getElementById('val-noise-gate').textContent=this.value">
                        </div>

                        <!-- Real-Time Decoupled Live Audio Telemetry Meter -->
                        <div class="flex flex-col gap-2 bg-slate-950 p-3 rounded-lg border border-slate-900">
                            <div class="flex items-center gap-3">
                                <span class="w-8 text-[9px] text-pink-400">LOWS</span>
                                <div class="flex-1 h-2 bg-slate-900 rounded-full overflow-hidden">
                                    <div id="telemetry-bar-lows" class="h-full bg-pink-500 shadow-[0_0_8px_#ec4899] transition-all duration-75" style="width: 0%"></div>
                                </div>
                            </div>
                            <div class="flex items-center gap-3">
                                <span class="w-8 text-[9px] text-cyan-400">MIDS</span>
                                <div class="flex-1 h-2 bg-slate-900 rounded-full overflow-hidden">
                                    <div id="telemetry-bar-mids" class="h-full bg-cyan-500 shadow-[0_0_8px_#06b6d4] transition-all duration-75" style="width: 0%"></div>
                                </div>
                            </div>
                            <div class="flex items-center gap-3">
                                <span class="w-8 text-[9px] text-green-400">HIGHS</span>
                                <div class="flex-1 h-2 bg-slate-900 rounded-full overflow-hidden">
                                    <div id="telemetry-bar-highs" class="h-full bg-green-500 shadow-[0_0_8px_#22c55e] transition-all duration-75" style="width: 0%"></div>
                                </div>
                            </div>
                        </div>

                        <!-- Dynamic Canvas Matrix Boundaries Scaling controls -->
                        <div class="flex flex-col gap-1.5 border-t border-slate-900/60 pt-3">
                            <div class="flex justify-between">
                                <label class="text-slate-400">Virtual Canvas Dimensions</label>
                                <span id="val-canvas-res" class="text-cyan-400 font-bold">320 px Width (16:10 Ratio)</span>
                            </div>
                            <input type="range" id="setting-canvas-res" min="160" max="480" step="16" class="w-full" oninput="document.getElementById('val-canvas-res').textContent=this.value">
                        </div>

                        <div class="flex flex-col gap-1.5 border-t border-slate-900/60 pt-3">
                            <div class="flex justify-between">
                                <label class="text-slate-400">Engine Output Target FPS</label>
                                <span id="val-target-fps" class="text-cyan-400 font-bold">30</span>
                            </div>
                            <input type="range" id="setting-fps" min="10" max="120" step="5" class="w-full" oninput="document.getElementById('val-target-fps').textContent=this.value">
                        </div>
                    </div>

                    <button onclick="saveGlobalSettings()" class="w-full py-2 bg-gradient-to-r from-cyan-500 to-pink-500 text-slate-950 font-extrabold rounded-lg hover:brightness-110 transition-all font-mono text-xs uppercase shadow-[0_0_15px_rgba(6,182,212,0.3)]">
                        Apply Settings
                    </button>
                </div>
            </div>

        </div>

        <!-- Custom Order Sequencer Pin Mapping Modal -->
        <div id="reorder-modal" class="fixed inset-0 bg-slate-950/85 backdrop-blur-md hidden items-center justify-center z-50 p-4">
            <div class="glass-panel p-6 rounded-xl border border-slate-800 w-full max-w-lg shadow-2xl flex flex-col gap-4">
                <div class="flex items-center justify-between border-b border-slate-800 pb-3">
                    <div>
                        <h3 class="text-sm font-bold tracking-wider font-mono uppercase text-slate-200">Reorder Diagnostics Map</h3>
                        <p class="text-[10px] text-pink-500 font-mono mt-0.5"><i class="fa-solid fa-lightbulb"></i> Non-target LEDs remain black on your desktop</p>
                    </div>
                    <button onclick="closeReorderModal()" class="text-slate-400 hover:text-slate-200 text-sm"><i class="fa-solid fa-xmark"></i></button>
                </div>
                <p class="text-xs text-slate-400 leading-relaxed font-mono">
                    Click physical nodes sequentially inside the pool. Each hovered button lights up that exact physical LED in <span class="text-cyan-400 font-bold">Cyan</span>, allowing you to instantly map the hardware pathway.
                </p>
                <div id="modal-node-pool" class="flex flex-wrap gap-2 py-4 justify-center bg-slate-950 rounded-lg p-4 border border-slate-900 shadow-inner max-h-60 overflow-y-auto"></div>
                <div class="flex items-center justify-between border-t border-slate-900 pt-3 mt-2 text-xs font-mono">
                    <div class="text-slate-500">Assigned Mapping: <span id="modal-sequence-preview" class="text-pink-500 font-bold">[]</span></div>
                    <div class="flex gap-2">
                        <button onclick="resetReorderSequence()" class="px-3 py-1 bg-slate-900 border border-slate-700 rounded text-slate-300 hover:bg-slate-800">Clear Map</button>
                        <button onclick="saveReorderSequence()" class="px-3 py-1 bg-cyan-500 text-slate-950 font-bold rounded hover:bg-cyan-400">Save Sequence</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- NEW: THREE-COLUMN DEDICATED CALIBRATION STUDIO WORKSPACE OVERLAY -->
        <div id="calibration-modal" class="fixed inset-0 bg-[#050811]/98 backdrop-blur-md hidden flex-col z-50 p-6 select-none font-sans">
            <!-- Modal Header -->
            <div class="h-12 border-b border-slate-900 flex items-center justify-between pb-3 flex-none">
                <button onclick="closeCalibrationModal()" class="text-xs font-mono font-bold text-slate-400 hover:text-slate-200 transition-colors uppercase flex items-center gap-1.5">
                    <i class="fa-solid fa-arrow-left"></i> Back to Device Directory
                </button>
                <div class="text-right">
                    <h3 class="text-xs font-bold font-mono uppercase text-slate-300 tracking-wider">
                        Calibrator Active: [<span id="cal-modal-title" class="text-cyan-400">Device</span>]
                    </h3>
                </div>
            </div>
            
            <!-- Modal Content - Three Column Layout -->
            <div class="flex-1 flex overflow-hidden py-4 gap-6 min-h-0">
                
                <!-- COLUMN A: SEARCHABLE SHAPE LIBRARY & PRESETS -->
                <div class="w-80 flex flex-col gap-4 overflow-hidden flex-none">
                    <div class="glass-panel p-4 rounded-xl border border-slate-900 flex flex-col gap-3 font-mono text-[10px] flex-none">
                        <label class="text-slate-400 uppercase tracking-widest text-[9px]"><i class="fa-solid fa-magnifying-glass mr-1"></i> Search Standard & Custom Shapes</label>
                        <input type="text" id="cal-shape-search" oninput="onShapeLibrarySearch(this.value)" placeholder="Search templates (TKL, Fan...)" class="w-full bg-slate-950 border border-slate-800 rounded py-2 px-3 text-slate-300 outline-none focus:border-cyan-500 font-mono text-[10px]">
                        
                        <!-- Shape Category Filter Pills -->
                        <div class="flex justify-between gap-1 border-t border-slate-900/60 pt-2 text-center text-slate-400">
                            <button onclick="filterShapeLibrary('all')" id="shape-pill-all" class="flex-1 py-1 rounded bg-slate-900 border border-slate-800 hover:border-pink-500 text-[10px] active">ALL</button>
                            <button onclick="filterShapeLibrary('KEYBOARD')" id="shape-pill-keyboard" class="flex-1 py-1 rounded bg-slate-900 border border-slate-800 hover:border-pink-500" title="Keyboards">⌨️</button>
                            <button onclick="filterShapeLibrary('FAN')" id="shape-pill-fan" class="flex-1 py-1 rounded bg-slate-900 border border-slate-800 hover:border-pink-500" title="Fans">❄️</button>
                            <button onclick="filterShapeLibrary('RAM')" id="shape-pill-ram" class="flex-1 py-1 rounded bg-slate-900 border border-slate-800 hover:border-pink-500" title="RAM Sticks">▒</button>
                            <button onclick="filterShapeLibrary('STRIMER')" id="shape-pill-strimer" class="flex-1 py-1 rounded bg-slate-900 border border-slate-800 hover:border-pink-500" title="Cables">⚡</button>
                        </div>
                    </div>
                    
                    <div class="flex-1 flex flex-col gap-3 bg-slate-950/40 p-4 rounded-xl border border-slate-900/60 overflow-hidden min-h-0">
                        <span class="text-xs font-bold font-mono tracking-widest uppercase text-slate-400 border-b border-slate-900 pb-2 flex items-center justify-between">
                            <span>Pre-Configured Schemas</span>
                        </span>
                        <div id="cal-shapes-container" class="flex-1 overflow-y-auto flex flex-col gap-2 pr-1 font-mono text-[10px]">
                            <!-- Dynamically populated searchable shape templates -->
                        </div>
                    </div>
                </div>
                
                <!-- COLUMN B: VECTOR CALIBRATION WORKSPACE -->
                <div class="flex-1 flex flex-col gap-4 min-h-0">
                    <div class="flex-none flex justify-between items-center text-[10px] font-mono text-slate-500 px-1">
                        <span>(0,0) ASPECT-RATIO PRESERVED WORKSPACE [16:10]</span>
                        <span id="cal-workspace-status">Grid: Disabled</span>
                    </div>
                    
                    <div class="flex-1 relative bg-slate-950/30 rounded-xl border border-slate-900/80 p-4 overflow-hidden flex items-center justify-center">
                        <div class="w-full h-full relative aspect-[16/10] border border-slate-800 bg-slate-950/40 rounded-lg overflow-hidden max-h-[70vh] shadow-inner" id="cal-workspace-bounds">
                            <!-- Low opacity real-time visualizer canvas stream playing behind nodes -->
                            <canvas id="cal-stream-preview" class="absolute inset-0 w-full h-full object-cover opacity-20 pointer-events-none select-none z-0" style="filter: blur(8px);"></canvas>
                            <div id="cal-grid-overlay" class="absolute inset-0 pointer-events-none opacity-25 z-10"></div>
                            <svg id="cal-svg" class="absolute inset-0 w-full h-full pointer-events-none z-10"></svg>
                            <div id="cal-nodes-root" class="absolute inset-0 z-20"></div>
                        </div>
                    </div>
                    
                    <!-- Real-time Level Telemetry Meters -->
                    <div class="flex-none glass-panel p-4 rounded-xl border border-slate-900 flex flex-col gap-2">
                        <span class="text-[9px] font-mono font-bold uppercase tracking-wider text-slate-400">Decoupled Audio Telemetry</span>
                        <div class="grid grid-cols-3 gap-4 font-mono text-[9px]">
                            <div class="flex items-center gap-2">
                                <span class="text-pink-400">LOWS</span>
                                <div class="flex-1 h-1.5 bg-slate-950 rounded-full overflow-hidden">
                                    <div id="cal-meter-lows" class="h-full bg-pink-500 shadow-[0_0_8px_#ec4899] transition-all duration-75" style="width: 0%"></div>
                                </div>
                            </div>
                            <div class="flex items-center gap-2">
                                <span class="text-cyan-400">MIDS</span>
                                <div class="flex-1 h-1.5 bg-slate-950 rounded-full overflow-hidden">
                                    <div id="cal-meter-mids" class="h-full bg-cyan-500 shadow-[0_0_8px_#06b6d4] transition-all duration-75" style="width: 0%"></div>
                                </div>
                            </div>
                            <div class="flex items-center gap-2">
                                <span class="text-green-400">HIGHS</span>
                                <div class="flex-1 h-1.5 bg-slate-950 rounded-full overflow-hidden">
                                    <div id="cal-meter-highs" class="h-full bg-green-500 shadow-[0_0_8px_#22c55e] transition-all duration-75" style="width: 0%"></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- COLUMN C: GEOMETRIC INSPECTOR & PROPERTIES -->
                <div class="w-80 flex flex-col gap-4 overflow-y-auto pr-1 flex-none z-10">
                    <h2 class="text-xs font-bold font-mono tracking-widest uppercase text-slate-400">Geometric Inspector</h2>
                    
                    <!-- Snapping & Alignments -->
                    <div class="glass-panel p-4 rounded-xl border border-slate-900 flex flex-col gap-3 font-mono text-[10px]">
                        <span class="text-cyan-400 font-bold uppercase border-b border-slate-900 pb-2 flex items-center gap-1.5"><i class="fa-solid fa-magnet"></i> SNAP & SYMMETRY</span>
                        <div class="flex items-center justify-between">
                            <span class="text-slate-400">GRID LOCK</span>
                            <button onclick="toggleCalibrationGridLock()" id="cal-grid-lock-btn" class="text-cyan-400 text-lg">
                                <i class="fa-solid fa-toggle-off"></i>
                            </button>
                        </div>
                        <div class="flex flex-col gap-1.5">
                            <div class="flex justify-between">
                                <label class="text-slate-400">GRID DIVISIONS</label>
                                <span id="cal-val-divisions" class="text-cyan-400 font-bold">16</span>
                            </div>
                            <input type="range" id="cal-setting-divisions" min="4" max="100" step="2" value="16" class="w-full" oninput="onCalDivisionsChange(val)">
                        </div>
                    </div>
                    
                    <!-- Generator Macros -->
                    <div class="glass-panel p-4 rounded-xl border border-slate-900 flex flex-col gap-3 font-mono text-[10px]">
                        <span class="text-cyan-400 font-bold uppercase border-b border-slate-900 pb-2 flex items-center gap-1.5"><i class="fa-solid fa-calculator"></i> PROCEDURAL GENERATORS</span>
                        <div class="flex flex-col gap-2">
                            <button onclick="triggerProceduralGenerator('linear')" class="w-full py-1.5 bg-slate-900 border border-slate-800 rounded hover:border-cyan-500/40 text-slate-200">✍️ Draw Path (Linear)</button>
                            <button onclick="triggerProceduralGenerator('radial')" class="w-full py-1.5 bg-slate-900 border border-slate-800 rounded hover:border-cyan-500/40 text-slate-200">◯ Radial Loop (Circle)</button>
                            <button onclick="triggerProceduralGenerator('matrix')" class="w-full py-1.5 bg-slate-900 border border-slate-800 rounded hover:border-cyan-500/40 text-slate-200">▤ Matrix Grid (Array)</button>
                        </div>
                    </div>
                    
                    <!-- Specific Nodes inspector -->
                    <div class="glass-panel p-4 rounded-xl border border-slate-900 flex flex-col gap-3 font-mono text-[10px]">
                        <span class="text-pink-500 font-bold uppercase border-b border-slate-900 pb-2 flex items-center gap-1.5"><i class="fa-solid fa-circle-dot"></i> INDIVIDUAL LED PINS</span>
                        <div class="relative flex-none mb-1">
                            <i class="fa-solid fa-magnifying-glass absolute left-3 top-2.5 text-slate-500 text-xs"></i>
                            <input type="text" id="cal-led-search" oninput="onCalLedSearch(this.value)" placeholder="Search index..." class="w-full bg-slate-950 border border-slate-800 rounded py-1.5 pl-9 pr-3 text-[10px] text-slate-300 outline-none focus:border-cyan-500 font-mono">
                        </div>
                        <div id="cal-led-list-container" class="flex flex-col gap-2 max-h-56 overflow-y-auto pr-1">
                            <!-- Injected LED list items -->
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- Modal Footer -->
            <div class="h-14 border-t border-slate-900 flex items-center justify-between pt-3 flex-none">
                <button onclick="resetCalibrationToDefault()" class="px-4 py-2 bg-slate-900 border border-slate-800 hover:border-pink-500 text-pink-500 rounded text-xs font-mono font-bold uppercase transition-colors">
                    Reset to Default Shape
                </button>
                <button onclick="saveCalibrationAndClose()" class="px-5 py-2 bg-gradient-to-r from-cyan-500 to-pink-500 text-slate-950 font-extrabold rounded-lg hover:brightness-110 transition-all font-mono text-xs uppercase shadow-[0_0_15px_rgba(6,182,212,0.3)]">
                    Save Mapping & Close
                </button>
            </div>
        </div>

        <!-- Custom Frame Resize Handle -->
        <div id="window-resize-handle" class="absolute bottom-0 right-0 h-4 w-4 cursor-se-resize z-50 flex items-end justify-end p-0.5" onmousedown="onResizeHandleMouseDown(event)">
            <svg class="h-3 w-3 text-slate-600 hover:text-cyan-400" viewBox="0 0 10 10" fill="currentColor">
                <path d="M10,0 L0,10 L10,10 Z" />
            </svg>
        </div>

        <script>
            let devices = [];
            let activeEffect = "";
            let parameterSchema = {};
            let favoritedEffects = [];
            let activeTab = "layout";
            let activeDragDevice = null;
            let dragOffset = { x: 0, y: 0 };
            let activeResizeDevice = null;
            let resizeAnchor = { x: 0, y: 0 };
            let selectedDeviceId = null;
            
            // Audio hardware options cache
            let audioHardware = { inputs: [], outputs: [] };

            // Plugins state cache
            let plugins = [];
            let selectedConfigPluginId = null;
            
            // GIF Library state cache
            let gifLibrary = [];
            let gifSearchQuery = "";

            // Reordering modal states
            let currentReorderDeviceId = "";
            let currentReorderSequence = [];
            
            // Fine-grained LED Pin calibration state
            let currentCalibratorDeviceId = "";
            let localCalCoords = [];
            let calGridLockEnabled = false;
            let calGridDivisions = 16;
            let activeDragCalNodeIdx = null;
            let activeHighlightNodeIdx = null;
            let calLedSearchQuery = "";
            let calShapeLibrarySearchQuery = "";
            let calShapeLibraryCategory = "all";
            
            let audioEmulatedState = false;

            // Pre-configured geometric schema presets dictionary
            const standardLibraryPresets = {
                "Keyboard Full Size": { category: "KEYBOARD", size: 104, generator: "keyboard" },
                "Keyboard Tenkeyless (TKL)": { category: "KEYBOARD", size: 87, generator: "keyboard_tkl" },
                "Keyboard Compact 60%": { category: "KEYBOARD", size: 61, generator: "keyboard_60" },
                "Standard Cooling Ring": { category: "FAN", size: 12, generator: "ring_12" },
                "Dual-Concentric Fan (LL120)": { category: "FAN", size: 16, generator: "ring_16" },
                "Uni-Fan Border Array": { category: "FAN", size: 32, generator: "uni_fan" },
                "DRAM Stick Segmented Bar": { category: "RAM", size: 8, generator: "ram_inline" },
                "Dominator Premium Bar": { category: "RAM", size: 12, generator: "ram_inline" },
                "Lian Li Strimer Plus GPU": { category: "STRIMER", size: 36, generator: "strimer_8" },
                "Lian Li Strimer Plus MB": { category: "STRIMER", size: 120, generator: "strimer_24" },
                "Linear LED Strip Path": { category: "STRIP", size: 30, generator: "linear" }
            };

            // --- Connection Retry Wait Loop ---
            async function waitForBackend() {
                const statusDisplay = document.getElementById("active-fps-display");
                if (statusDisplay) statusDisplay.textContent = "Connecting to Core...";
                
                while (true) {
                    try {
                        const res = await fetch("http://127.0.0.1:8000/api/config");
                        if (res.ok) {
                            break; // Backend is active!
                        }
                    } catch (e) {
                        // Backend still loading, ignore and retry in 500ms
                    }
                    await new Promise(resolve => setTimeout(resolve, 500));
                }
                
                // Once backend port is responding, initialize DOM values
                await init();
            }

            async function init() {
                await fetchAudioHardware();
                await fetchConfig();
                await fetchDevices();
                await fetchEffects();
                await fetchPlugins();
                setupWebSocket();
                switchTab("layout");
            }

            // --- Open Directory API Bridge ---
            async function openDirectory(folderName) {
                await fetch(`/api/open-dir/${folderName}`, { method: "POST" });
            }

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

            // --- Drag & Resize Window Manual Handlers ---
            let isDragging = false;
            let startMouseX = 0;
            let startMouseY = 0;

            function startTauriDrag() {
                if (window.__TAURI__) {
                    const webviewWin = window.__TAURI__.webviewWindow;
                    if (webviewWin) {
                        webviewWin.getCurrentWebviewWindow().startDragging();
                    } else if (window.__TAURI__.window) {
                        window.__TAURI__.window.getCurrentWindow().startDragging();
                    }
                }
            }

            // Custom manual resize dragging
            let isResizing = false;
            let startResizeX = 0;
            let startResizeY = 0;

            function onResizeHandleMouseDown(e) {
                e.preventDefault();
                e.stopPropagation();
                isResizing = true;
                startResizeX = e.screenX;
                startResizeY = e.screenY;
                document.addEventListener('mousemove', onResizeHandleMouseMove);
                document.addEventListener('mouseup', onResizeHandleMouseUp);
            }

            function onResizeHandleMouseMove(e) {
                if (!isResizing) return;
                const dx = e.screenX - startResizeX;
                const dy = e.screenY - startResizeY;
                if (dx !== 0 || dy !== 0) {
                    startResizeX = e.screenX;
                    startResizeY = e.screenY;
                    if (window.__TAURI__) {
                        window.__TAURI__.core.invoke('resize_window', { dx, dy });
                    }
                }
            }

            function onResizeHandleMouseUp() {
                isResizing = false;
                document.removeEventListener('mousemove', onResizeHandleMouseMove);
                document.removeEventListener('mouseup', onResizeHandleMouseUp);
            }

            document.addEventListener('DOMContentLoaded', () => {
                document.getElementById('titlebar')?.addEventListener('mousedown', (e) => {
                    if (e.buttons === 1 && !e.target.closest('button') && !e.target.closest('nav') && !e.target.closest('input') && !e.target.closest('select')) {
                        startTauriDrag();
                    }
                });
            });

            // --- Navigation / Tab Controller ---
            function switchTab(tabId) {
                activeTab = tabId;
                const tabs = ["layout", "shaders", "devices", "plugins", "settings"];

                tabs.forEach(t => {
                    const btn = document.getElementById(`tab-btn-${t}`);
                    const view = document.getElementById(`tab-view-${t}`);
                    if (t === tabId) {
                        if (btn) btn.classList.add("active");
                        if (view) view.classList.remove("hidden");
                    } else {
                        if (btn) btn.classList.remove("active");
                        if (view) view.classList.add("hidden");
                    }
                });

                if (tabId === "layout") {
                    renderWorkspaceDevices();
                    renderLayoutDeviceDirectory();
                    updateInspectorUI();
                } else if (tabId === "devices") {
                    renderHardwareTab();
                } else if (tabId === "plugins") {
                    renderPluginsGrid();
                } else if (tabId === "shaders") {
                    renderEffectsList();
                }
            }

            async function fetchAudioHardware() {
                try {
                    const res = await fetch('/api/audio/devices');
                    audioHardware = await res.json();
                } catch(e) {
                    console.error("Failed fetching audio devices:", e);
                }
            }

            async function fetchConfig() {
                const res = await fetch('/api/config');
                const cfg = await res.json();
                
                // Load global settings panel inputs
                document.getElementById("setting-host").value = cfg.openrgb_host;
                document.getElementById("setting-port").value = cfg.openrgb_port;
                document.getElementById("setting-fps").value = cfg.target_fps;
                document.getElementById("val-target-fps").textContent = cfg.target_fps;
                document.getElementById("active-fps-display").textContent = `Target: ${cfg.target_fps} FPS`;

                // Set canvas and audio parameters
                document.getElementById("setting-canvas-res").value = cfg.canvas_width;
                document.getElementById("val-canvas-res").textContent = `${cfg.canvas_width} px Width (16:10 Ratio)`;
                document.getElementById("setting-noise-gate").value = cfg.audio_noise_gate;
                document.getElementById("val-noise-gate").textContent = cfg.audio_noise_gate;
                
                audioEmulatedState = cfg.audio_emulation;
                updateEmulationToggleUI();

                const audioModeSelect = document.getElementById("setting-audio-mode");
                audioModeSelect.value = cfg.audio_mode || "input";
                populateAudioDevicesDropdown(cfg.audio_mode || "input", cfg.audio_device_id || "default");
            }

            function populateAudioDevicesDropdown(mode, selectedDeviceId) {
                const deviceSelect = document.getElementById("setting-audio-device");
                deviceSelect.innerHTML = "";
                
                // Read from cache depending on target filter category
                const list = mode === "input" ? audioHardware.inputs : audioHardware.outputs;
                list.forEach(dev => {
                    const opt = document.createElement("option");
                    opt.value = dev.id;
                    opt.textContent = dev.name;
                    if (dev.id === selectedDeviceId) {
                        opt.selected = true;
                    }
                    deviceSelect.appendChild(opt);
                });
            }

            // --- GIF Library search & filters ---
            function onGifSearch(val) {
                gifSearchQuery = val;
                renderGifLibraryList();
            }

            function onAudioModeChange(mode) {
                populateAudioDevicesDropdown(mode, null);
            }
            
            function toggleAudioEmulation() {
                audioEmulatedState = !audioEmulatedState;
                updateEmulationToggleUI();
            }
            
            function updateEmulationToggleUI() {
                const btn = document.getElementById("setting-audio-emulation-btn");
                if (audioEmulatedState) {
                    btn.className = "text-cyan-400 text-lg";
                    btn.innerHTML = '<i class="fa-solid fa-toggle-on"></i>';
                } else {
                    btn.className = "text-slate-600 text-lg";
                    btn.innerHTML = '<i class="fa-solid fa-toggle-off"></i>';
                }
            }

            async function fetchDevices() {
                try {
                    const res = await fetch('/api/devices');
                    devices = await res.json();
                    if (activeTab === "layout") {
                        renderWorkspaceDevices();
                        renderLayoutDeviceDirectory();
                        updateInspectorUI();
                    }
                    if (activeTab === "devices") renderHardwareTab();
                } catch(e) {
                    console.error("Failed fetching hardware layouts: ", e);
                }
            }

            async function fetchEffects() {
                try {
                    const res = await fetch('/api/effects');
                    const data = await res.json();
                    activeEffect = data.active;
                    parameterSchema = data.library;
                    favoritedEffects = data.favorites || [];
                    
                    document.getElementById("active-shader-title").textContent = activeEffect.replace(/([A-Z])/g, ' $1').trim();
                    renderEffectsList();
                    renderEffectParameters(data.params);
                } catch(e) {
                    console.error("Failed loading shader maps: ", e);
                }
            }

            // --- TAB: Plugins Manager ---
            async function fetchPlugins() {
                try {
                    const res = await fetch('/api/plugins');
                    plugins = await res.json();
                    if (activeTab === "plugins") {
                        renderPluginsGrid();
                    }
                } catch(e) {
                    console.error("Failed to load plugins: ", e);
                }
            }

            function renderPluginsGrid() {
                const grid = document.getElementById("plugins-grid");
                grid.innerHTML = "";
                
                plugins.forEach(p => {
                    const activeBorder = p.enabled ? 'border-pink-500 bg-slate-900/60 shadow-[0_0_15px_rgba(236,72,153,0.15)]' : 'border-slate-900 bg-slate-950/40';
                    const card = document.createElement("div");
                    card.className = `glass-panel p-4 rounded-xl border flex flex-col justify-between h-36 relative transition-all ${activeBorder}`;
                    
                    card.innerHTML = `
                        <div>
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold font-mono text-slate-300 tracking-wide uppercase">${p.name}</span>
                                <button onclick="togglePlugin('${p.id}', ${!p.enabled})" class="text-xs ${p.enabled ? 'text-cyan-400' : 'text-slate-600'}">
                                    <i class="fa-solid ${p.enabled ? 'fa-toggle-on':'fa-toggle-off'} text-lg"></i>
                                </button>
                            </div>
                            <p class="text-[10px] text-slate-500 font-mono mt-1 leading-normal">${p.description}</p>
                        </div>
                        <div class="flex justify-between items-center border-t border-slate-900 pt-3">
                            <span class="text-[9px] text-slate-500 font-mono">PLUGIN // ${p.id.toUpperCase()}</span>
                            ${p.enabled ? 
                                `<button onclick="openPluginConfig('${p.id}')" class="px-2.5 py-1 bg-slate-900 border border-slate-800 hover:border-pink-500 text-pink-500 rounded text-[9px] font-mono font-bold uppercase transition-colors">Config</button>` :
                                `<span class="text-[9px] text-slate-600 font-mono">DISABLED</span>`
                            }
                        </div>
                    `;
                    grid.appendChild(card);
                });
            }

            async function togglePlugin(pluginId, enableState) {
                const res = await fetch(`/api/plugins/${pluginId}/toggle`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ enabled: enableState })
                });
                await fetchPlugins();
                if (selectedConfigPluginId === pluginId && !enableState) {
                    document.getElementById("plugin-params-container").innerHTML = `
                        <p class="text-[10px] text-slate-500 font-mono text-center py-4">Click "Config" on an enabled plugin to modify its settings.</p>
                    `;
                    document.getElementById("active-plugin-title").textContent = "Select a Plugin";
                    selectedConfigPluginId = null;
                }
            }

            function openPluginConfig(pluginId) {
                selectedConfigPluginId = pluginId;
                const plug = plugins.find(p => p.id === pluginId);
                if (!plug) return;

                document.getElementById("active-plugin-title").textContent = plug.name;
                const root = document.getElementById("plugin-params-container");
                root.innerHTML = "";

                Object.keys(plug.schema).forEach(key => {
                    const field = plug.schema[key];
                    const val = plug.params[key];
                    const wrap = document.createElement("div");
                    wrap.className = "flex flex-col gap-1.5";

                    if (field.type === "range") {
                        wrap.innerHTML = `
                            <div class="flex justify-between text-[11px] font-mono">
                                <span class="text-slate-400">${field.label}</span>
                                <span class="text-cyan-400 font-bold" id="p-val-${key}">${val}</span>
                            </div>
                            <input type="range" min="${field.min}" max="${field.max}" step="${field.step}" value="${val}"
                                oninput="updatePluginParamValue('${pluginId}', '${key}', this.value)" 
                                class="w-full accent-cyan-500 bg-slate-900 border border-slate-700 rounded-lg appearance-none h-1 cursor-pointer">
                        `;
                    } else if (field.type === "color") {
                        const rgbToHex = (r, g, b) => '#' + [r, g, b].map(x => {
                            const hex = x.toString(16);
                            return hex.length === 1 ? '0' + hex : hex;
                        }).join('');
                        const hexVal = rgbToHex(val[0], val[1], val[2]);

                        wrap.innerHTML = `
                            <div class="flex justify-between items-center text-[11px] font-mono">
                                <span class="text-slate-400">${field.label}</span>
                                <input type="color" value="${hexVal}" onchange="updatePluginColorParam('${pluginId}', '${key}', this.value)" class="bg-transparent border-0 outline-none w-8 h-6 cursor-pointer">
                            </div>
                        `;
                    }
                    root.appendChild(wrap);
                });
            }

            async function updatePluginParamValue(pluginId, key, val) {
                document.getElementById(`p-val-${key}`).textContent = val;
                await fetch(`/api/plugins/${pluginId}/param`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, value: parseFloat(val) })
                });
                await fetchPlugins();
            }

            async function updatePluginColorParam(pluginId, key, hexVal) {
                const hexToRgb = hex => hex.replace(/^#?([a-f\d])([a-f\d])([a-f\d])$/i, (m, r, g, b) => '#' + r + r + g + g + b + b)
                    .substring(1).match(/.{2}/g).map(x => parseInt(x, 16));
                
                const rgb = hexToRgb(hexVal);
                await fetch(`/api/plugins/${pluginId}/param`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, value: rgb })
                });
                await fetchPlugins();
            }
            
            // --- TAB: GIF Library Manager ---
            async function fetchGifLibrary() {
                try {
                    const res = await fetch('/api/gifs');
                    gifLibrary = await res.json();
                    renderGifLibraryList();
                } catch(e) {
                    console.error("Failed to load GIF library: ", e);
                }
            }
            
            function renderGifLibraryList() {
                const list = document.getElementById("gif-library-list");
                list.innerHTML = "";
                
                const filtered = gifLibrary.filter(g => g.name.toLowerCase().includes(gifSearchQuery.toLowerCase()));
                filtered.forEach(g => {
                    const activeBorder = g.active ? 'border-pink-500 bg-slate-900/60 shadow-[0_0_15px_rgba(236,72,153,0.1)]' : 'border-slate-800 bg-slate-950/40';
                    const el = document.createElement("div");
                    el.className = `p-2 rounded border flex items-center justify-between gap-2 text-[10px] font-mono transition-all ${activeBorder}`;
                    
                    el.innerHTML = `
                        <div class="flex-1 overflow-hidden">
                            <span class="text-slate-300 font-bold block truncate cursor-pointer" onclick="selectGifAsset('${g.id}')">${g.name}</span>
                            <span class="text-[8px] text-slate-500 block truncate">${g.id}</span>
                        </div>
                        <div class="flex gap-2 text-slate-400">
                            <button onclick="renameGifPrompt('${g.id}', '${g.name}')" title="Rename"><i class="fa-solid fa-edit hover:text-cyan-400"></i></button>
                            ${g.id !== 'target.gif' ? 
                                `<button onclick="deleteGifAsset('${g.id}')" title="Delete"><i class="fa-solid fa-trash hover:text-pink-500"></i></button>` : ''
                            }
                        </div>
                    `;
                    list.appendChild(el);
                });
            }
            
            async function selectGifAsset(id) {
                const res = await fetch(`/api/gifs/${id}/select`, { method: "POST" });
                const data = await res.json();
                if (data.status === "ok") {
                    await fetchGifLibrary();
                    await fetchConfig();
                }
            }
            
            async function renameGifPrompt(id, currentName) {
                const newName = prompt("Enter custom display name:", currentName);
                if (newName && newName.trim() !== "") {
                    await fetch(`/api/gifs/${id}/rename`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ name: newName.trim() })
                    });
                    await fetchGifLibrary();
                }
            }
            
            async function deleteGifAsset(id) {
                if (confirm(`Delete ${id}?`)) {
                    await fetch(`/api/gifs/${id}`, { method: "DELETE" });
                    await fetchGifLibrary();
                }
            }

            // --- TAB 1: Draggable Workspace Layout Viewport ---
            function renderWorkspaceDevices() {
                const root = document.getElementById("workspace-elements-root");
                root.innerHTML = "";

                devices.forEach(dev => {
                    if (!dev.enabled) return;
                    if (dev.hidden_in_layout) return;

                    const block = document.createElement("div");
                    let blockClasses = "absolute border border-slate-700/80 rounded bg-slate-900/40 cursor-grab active:cursor-grabbing hover:border-pink-500 group transition-all z-20 overflow-hidden shadow-2xl";
                    
                    const isSelected = selectedDeviceId === dev.id;
                    if (isSelected) {
                        blockClasses += " ring-2 ring-cyan-400 shadow-[0_0_15px_rgba(6,182,212,0.5)] border-cyan-400";
                    }
                    
                    block.className = blockClasses;
                    block.style.left = `${dev.x * 100}%`;
                    block.style.top = `${dev.y * 100}%`;
                    block.style.width = `${dev.width * 100}%`;
                    block.style.height = `${dev.height * 100}%`;
                    block.style.transform = `rotate(${dev.rotation || 0}deg)`;

                    // Generate distinct device appearance outlines depending on active profile
                    let innerHTML = "";
                    if (dev.active_profile === "procedural") {
                        if (dev.form_type === "KEYBOARD") {
                            innerHTML = `<div class="grid grid-cols-[repeat(15,minmax(0,1fr))] grid-rows-[repeat(6,minmax(0,1fr))] h-[86%] w-full p-2 gap-1 opacity-70 bg-slate-950/60 rounded">`;
                            for (let i = 0; i < dev.led_count; i++) {
                                const rgb = dev.demo_colors ? dev.demo_colors[i] : [236,72,153];
                                innerHTML += `<div class="rounded bg-slate-900 border border-slate-800 flex items-center justify-center shadow-inner" style="box-shadow: 0 0 5px rgba(${rgb[0]},${rgb[1]},${rgb[2]},0.65)">
                                    <div class="w-1.5 h-1.5 rounded-full" style="background-color: rgb(${rgb[0]},${rgb[1]},${rgb[2]})"></div>
                                </div>`;
                            }
                            innerHTML += `</div>`;
                        } else if (dev.form_type === "RAM") {
                            innerHTML = `<div class="flex flex-col h-[86%] w-full justify-around items-center p-2 border-l-4 border-cyan-400 bg-slate-950/80 rounded shadow-inner">`;
                            for (let i = 0; i < dev.led_count; i++) {
                                const rgb = dev.demo_colors ? dev.demo_colors[i] : [6,182,212];
                                innerHTML += `<div class="w-3 h-3 rounded shadow" style="background-color: rgb(${rgb[0]},${rgb[1]},${rgb[2]}); box-shadow: 0 0 8px rgb(${rgb[0]},${rgb[1]},${rgb[2]})"></div>`;
                            }
                            innerHTML += `</div>`;
                        } else if (dev.form_type.startsWith("STRIMER")) {
                            const numLines = dev.form_type === "STRIMER_24PIN" ? 12 : 8;
                            innerHTML = `<div class="flex h-[86%] w-full justify-around p-1.5 bg-slate-950/90 rounded border border-slate-800/60 overflow-hidden shadow-inner">`;
                            for (let l = 0; l < numLines; l++) {
                                const ledsPerLine = Math.floor(dev.led_count / numLines);
                                innerHTML += `<div class="flex flex-col h-full justify-around items-center flex-1 border-r border-slate-800/10 last:border-r-0">`;
                                for (let i = 0; i < ledsPerLine; i++) {
                                    const ledIdx = l * ledsPerLine + i;
                                    const rgb = (dev.demo_colors && dev.demo_colors[ledIdx]) ? dev.demo_colors[ledIdx] : [6, 182, 212];
                                    innerHTML += `<div class="w-1.5 h-1.5 rounded-full" style="background-color: rgb(${rgb[0]},${rgb[1]},${rgb[2]}); box-shadow: 0 0 6px rgb(${rgb[0]},${rgb[1]},${rgb[2]})"></div>`;
                                }
                                innerHTML += `</div>`;
                            }
                            innerHTML += `</div>`;
                        } else {
                            innerHTML = `<div class="flex h-[86%] w-full justify-around items-center p-2 bg-slate-950/40 rounded border border-slate-900/60 shadow-inner">`;
                            for (let i = 0; i < dev.led_count; i++) {
                                const rgb = dev.demo_colors ? dev.demo_colors[i] : [34,197,94];
                                innerHTML += `<div class="w-2 h-2 rounded-full" style="background-color: rgb(${rgb[0]},${rgb[1]},${rgb[2]})"></div>`;
                            }
                            innerHTML += `</div>`;
                        }
                    } else {
                        // Custom Named Profile Calibration Mode
                        // Draw individual LEDs at their exact custom layout coordinates inside the bounding block dynamically
                        innerHTML = `<div class="absolute inset-0 bg-slate-950/70 rounded border border-slate-800/40 overflow-hidden shadow-inner">`;
                        
                        dev.coordinates.forEach((coord, i) => {
                            // Convert absolute panoramic coordinates [0, 1] into relative box offsets
                            let lx = (coord[0] - dev.x) / dev.width;
                            let ly = (coord[1] - dev.y) / dev.height;
                            lx = Math.max(0, Math.min(1, lx));
                            ly = Math.max(0, Math.min(1, ly));
                            
                            const px = lx * 100;
                            const py = ly * 100;
                            
                            const rgb = dev.demo_colors ? dev.demo_colors[i] : [6, 182, 212];
                            innerHTML += `<div class="absolute h-2 w-2 rounded-full animate-pulse" style="left: ${px}%; top: ${py}%; background-color: rgb(${rgb[0]},${rgb[1]},${rgb[2]}); box-shadow: 0 0 6px rgb(${rgb[0]},${rgb[1]},${rgb[2]}); transform: translate(-50%, -50%);"></div>`;
                        });
                        innerHTML += `</div>`;
                    }

                    innerHTML += `
                        <div class="absolute inset-x-0 bottom-0 bg-slate-950/90 border-t border-slate-900 px-1.5 py-0.5 text-[8px] font-mono tracking-wider text-slate-400 select-none pointer-events-none flex justify-between items-center z-10">
                            <span>${dev.name}</span>
                            <span>[${dev.led_count} L]</span>
                        </div>
                        <div class="absolute bottom-0 right-0 h-4 w-4 cursor-se-resize flex items-end justify-end p-0.5 z-30 group-hover:bg-cyan-500/30 transition-colors" onmousedown="startResize(event, '${dev.id}')">
                            <i class="fa-solid fa-arrows-alt text-[8px] text-cyan-400"></i>
                        </div>
                    `;

                    block.innerHTML = innerHTML;
                    block.onmousedown = (e) => {
                        e.stopPropagation();
                        if (e.target.closest('.cursor-se-resize')) return;
                        selectDevice(dev.id);
                        startDrag(e, dev.id);
                    };
                    root.appendChild(block);
                });
            }

            // --- Device Selection Management ---
            function selectDevice(deviceId) {
                selectedDeviceId = deviceId;
                renderWorkspaceDevices();
                renderLayoutDeviceDirectory();
                updateInspectorUI();
            }

            function clearWorkspaceSelection(e) {
                if (e.target.id === "canvas-workspace" || e.target.id === "workspace-elements-root") {
                    selectedDeviceId = null;
                    renderWorkspaceDevices();
                    renderLayoutDeviceDirectory();
                    updateInspectorUI();
                }
            }

            function renderLayoutDeviceDirectory() {
                const root = document.getElementById("layout-device-list");
                if (!root) return;
                root.innerHTML = "";

                devices.forEach(dev => {
                    const isSelected = selectedDeviceId === dev.id;
                    const bgClass = isSelected ? "bg-cyan-500/10 border-cyan-500/30 text-cyan-400" : "bg-slate-950/40 border-slate-900 hover:border-slate-800 text-slate-300";
                    const eyeIcon = dev.hidden_in_layout ? "fa-eye-slash text-slate-600" : "fa-eye text-cyan-400";

                    const el = document.createElement("div");
                    el.className = `p-2 rounded border flex items-center justify-between font-mono text-[10px] transition-all cursor-pointer ${bgClass}`;
                    el.onclick = (e) => {
                        if (e.target.closest('.toggle-hide-btn')) return;
                        selectDevice(dev.id);
                    };

                    el.innerHTML = `
                        <div class="flex items-center gap-2 truncate flex-1 pr-2">
                            <span class="font-bold truncate">${dev.name}</span>
                            <span class="text-[8px] text-slate-500">[${dev.led_count} L]</span>
                        </div>
                        <button onclick="toggleDeviceLayoutHide('${dev.id}')" class="toggle-hide-btn px-1.5 py-1 hover:bg-slate-900 rounded text-slate-400 transition-colors" title="Toggle Layout Visibility">
                            <i class="fa-solid ${eyeIcon}"></i>
                        </button>
                    `;
                    root.appendChild(el);
                });
            }

            function updateInspectorUI() {
                const panel = document.getElementById("device-inspector-panel");
                if (!selectedDeviceId) {
                    panel.classList.add("hidden");
                    return;
                }

                const dev = devices.find(d => d.id === selectedDeviceId);
                if (!dev) {
                    panel.classList.add("hidden");
                    return;
                }

                panel.classList.remove("hidden");
                document.getElementById("inspect-device-name").textContent = dev.name;

                document.getElementById("inspect-range-x").value = dev.x;
                document.getElementById("inspect-val-x").textContent = dev.x.toFixed(2);

                document.getElementById("inspect-range-y").value = dev.y;
                document.getElementById("inspect-val-y").textContent = dev.y.toFixed(2);

                document.getElementById("inspect-range-w").value = dev.width;
                document.getElementById("inspect-val-w").textContent = dev.width.toFixed(2);

                document.getElementById("inspect-range-h").value = dev.height;
                document.getElementById("inspect-val-h").textContent = dev.height.toFixed(2);

                document.getElementById("inspect-range-rot").value = dev.rotation || 0;
                document.getElementById("inspect-val-rot").textContent = `${Math.round(dev.rotation || 0)}°`;

                const hideBtn = document.getElementById("inspect-btn-hide");
                if (dev.hidden_in_layout) {
                    hideBtn.className = "text-pink-500 text-lg";
                    hideBtn.innerHTML = '<i class="fa-solid fa-toggle-on"></i>';
                } else {
                    hideBtn.className = "text-slate-600 text-lg";
                    hideBtn.innerHTML = '<i class="fa-solid fa-toggle-off"></i>';
                }
            }

            async function updateInspectorDeviceBounds() {
                if (!selectedDeviceId) return;
                const dev = devices.find(d => d.id === selectedDeviceId);
                if (!dev) return;

                const x = parseFloat(document.getElementById("inspect-range-x").value);
                const y = parseFloat(document.getElementById("inspect-range-y").value);
                const w = parseFloat(document.getElementById("inspect-range-w").value);
                const h = parseFloat(document.getElementById("inspect-range-h").value);
                const rot = parseFloat(document.getElementById("inspect-range-rot").value);

                dev.x = x;
                dev.y = y;
                dev.width = w;
                dev.height = h;
                dev.rotation = rot;

                document.getElementById("inspect-val-x").textContent = x.toFixed(2);
                document.getElementById("inspect-val-y").textContent = y.toFixed(2);
                document.getElementById("inspect-val-w").textContent = w.toFixed(2);
                document.getElementById("inspect-val-h").textContent = h.toFixed(2);
                document.getElementById("inspect-val-rot").textContent = `${Math.round(rot)}°`;

                renderWorkspaceDevices();

                await fetch(`/api/devices/${selectedDeviceId}/bounds`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        x: dev.x,
                        y: dev.y,
                        width: dev.width,
                        height: dev.height,
                        form_type: dev.form_type,
                        active_profile: dev.active_profile,
                        custom_profiles: dev.custom_profiles,
                        rotation: dev.rotation,
                        hidden_in_layout: dev.hidden_in_layout || false
                    })
                });
            }

            async function toggleDeviceLayoutHide(deviceId) {
                const dev = devices.find(d => d.id === deviceId);
                if (!dev) return;

                dev.hidden_in_layout = !dev.hidden_in_layout;
                renderWorkspaceDevices();
                renderLayoutDeviceDirectory();
                
                if (selectedDeviceId === deviceId) {
                    updateInspectorUI();
                }

                await fetch(`/api/devices/${deviceId}/bounds`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        x: dev.x,
                        y: dev.y,
                        width: dev.width,
                        height: dev.height,
                        form_type: dev.form_type,
                        active_profile: dev.active_profile,
                        custom_profiles: dev.custom_profiles,
                        rotation: dev.rotation || 0,
                        hidden_in_layout: dev.hidden_in_layout
                    })
                });
            }

            function toggleInspectorDeviceHide() {
                if (!selectedDeviceId) return;
                toggleDeviceLayoutHide(selectedDeviceId);
            }

            async function identifySelectedDevice() {
                if (!selectedDeviceId) return;
                await fetch(`/api/devices/${selectedDeviceId}/identify`, { method: "POST" });
            }

            // --- Drag Operations ---
            function startDrag(e, devId) {
                e.preventDefault();
                const dev = devices.find(d => d.id === devId);
                if (!dev) return;

                const parent = document.getElementById("canvas-workspace").getBoundingClientRect();
                activeDragDevice = dev;
                
                dragOffset.x = (e.clientX - parent.left) / parent.width - dev.x;
                dragOffset.y = (e.clientY - parent.top) / parent.height - dev.y;

                document.onmousemove = moveDrag;
                document.onmouseup = stopDrag;
            }

            function moveDrag(e) {
                if (!activeDragDevice) return;
                const parent = document.getElementById("canvas-workspace").getBoundingClientRect();

                let x = (e.clientX - parent.left) / parent.width - dragOffset.x;
                let y = (e.clientY - parent.top) / parent.height - dragOffset.y;

                x = Math.max(0, Math.min(1 - activeDragDevice.width, x));
                y = Math.max(0, Math.min(1 - activeDragDevice.height, y));

                activeDragDevice.x = x;
                activeDragDevice.y = y;
                renderWorkspaceDevices();
                updateInspectorUI();
            }

            async function stopDrag() {
                if (activeDragDevice) {
                    await fetch(`/api/devices/${activeDragDevice.id}/bounds`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            x: activeDragDevice.x,
                            y: activeDragDevice.y,
                            width: activeDragDevice.width,
                            height: activeDragDevice.height,
                            form_type: activeDragDevice.form_type,
                            active_profile: activeDragDevice.active_profile,
                            custom_profiles: activeDragDevice.custom_profiles,
                            rotation: activeDragDevice.rotation || 0,
                            hidden_in_layout: activeDragDevice.hidden_in_layout || false
                        })
                    });
                }
                activeDragDevice = null;
                document.onmousemove = null;
                document.onmouseup = null;
            }

            // --- Resize Operations ---
            function startResize(e, devId) {
                e.preventDefault();
                e.stopPropagation();
                const dev = devices.find(d => d.id === devId);
                if (!dev) return;

                activeResizeDevice = dev;
                document.onmousemove = moveResize;
                document.onmouseup = stopResize;
            }

            function moveResize(e) {
                if (!activeResizeDevice) return;
                const parent = document.getElementById("canvas-workspace").getBoundingClientRect();

                let width = ((e.clientX - parent.left) / parent.width) - activeResizeDevice.x;
                let height = ((e.clientY - parent.top) / parent.height) - activeResizeDevice.y;

                width = Math.max(0.05, Math.min(1.0 - activeResizeDevice.x, width));
                height = Math.max(0.05, Math.min(1.0 - activeResizeDevice.y, height));

                activeResizeDevice.width = width;
                activeResizeDevice.height = height;
                renderWorkspaceDevices();
                updateInspectorUI();
            }

            async function stopResize() {
                if (activeResizeDevice) {
                    await fetch(`/api/devices/${activeResizeDevice.id}/bounds`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            x: activeResizeDevice.x,
                            y: activeResizeDevice.y,
                            width: activeResizeDevice.width,
                            height: activeResizeDevice.height,
                            form_type: activeResizeDevice.form_type,
                            active_profile: activeResizeDevice.active_profile,
                            custom_profiles: activeResizeDevice.custom_profiles,
                            rotation: activeResizeDevice.rotation || 0,
                            hidden_in_layout: activeResizeDevice.hidden_in_layout || false
                        })
                    });
                }
                activeResizeDevice = null;
                document.onmousemove = null;
                document.onmouseup = null;
            }

            // --- TAB 2: Effects Selection & Favorites Manager ---
            function renderEffectsList() {
                const grid = document.getElementById("effects-grid");
                grid.innerHTML = "";
                const search = document.getElementById("effect-search").value.toLowerCase();

                const sortedKeys = Object.keys(parameterSchema).sort((a, b) => {
                    const favA = favoritedEffects.includes(a) ? 1 : 0;
                    const favB = favoritedEffects.includes(b) ? 1 : 0;
                    return favB - favA || a.localeCompare(b);
                });

                sortedKeys.forEach(key => {
                    if (search && !key.toLowerCase().includes(search)) return;

                    const isFav = favoritedEffects.includes(key);
                    const isActive = activeEffect === key;
                    const activeBorder = isActive ? 'border-pink-500 bg-slate-900/60 shadow-[0_0_15px_rgba(236,72,153,0.15)]' : 'border-slate-900 hover:border-slate-700 bg-slate-950/40';

                    const card = document.createElement("div");
                    card.className = `glass-panel p-4 rounded-xl border flex flex-col justify-between h-36 relative transition-all ${activeBorder}`;
                    
                    card.innerHTML = `
                        <div>
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-bold font-mono text-slate-300 tracking-wide uppercase">${key.replace(/([A-Z])/g, ' $1').trim()}</span>
                                <button onclick="toggleFavorite(event, '${key}')" class="text-xs text-slate-500 hover:text-pink-500 transition-all">
                                    <i class="${isFav ? 'fa-solid text-pink-500':'fa-regular'} fa-heart"></i>
                                </button>
                            </div>
                            <p class="text-[10px] text-slate-500 font-mono mt-1 leading-normal">
                                Visual effect mapping module. Supports real-time coordinate transformations.
                            </p>
                        </div>
                        <div class="flex justify-between items-center border-t border-slate-900 pt-3">
                            <span class="text-[9px] text-slate-500 font-mono">Effect ID // ${key.toUpperCase()}</span>
                            ${isActive ? 
                                `<span class="px-2 py-0.5 bg-pink-500/10 border border-pink-500/20 text-pink-400 rounded text-[9px] font-mono">ACTIVE</span>` :
                                `<button onclick="changeEffect('${key}')" class="px-2.5 py-1 bg-slate-900 border border-slate-800 hover:border-cyan-500 text-cyan-400 rounded text-[9px] font-mono font-bold uppercase transition-colors">Select</button>`
                            }
                        </div>
                    `;
                    grid.appendChild(card);
                });
            }

            async function toggleFavorite(e, effectName) {
                e.stopPropagation();
                if (favoritedEffects.includes(effectName)) {
                    favoritedEffects = favoritedEffects.filter(x => x !== effectName);
                } else {
                    favoritedEffects.push(effectName);
                }
                
                await fetch('/api/effects/favorites', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ favorites: favoritedEffects })
                });

                renderEffectsList();
            }

            function renderEffectParameters(currentValues) {
                const root = document.getElementById("params-container");
                root.innerHTML = "";
                
                // Expose uploader conditionally
                const uploader = document.getElementById("effect-upload-container");
                if (activeEffect === "GifPlayer") {
                    uploader.classList.remove("hidden");
                } else {
                    uploader.classList.add("hidden");
                }

                const schema = parameterSchema[activeEffect];
                if (!schema) return;

                Object.keys(schema).forEach(key => {
                    if (key.startsWith("_")) return; // Hide internal parameters
                    const field = schema[key];
                    const val = currentValues[key];
                    if (val === undefined) return;
                    
                    const wrap = document.createElement("div");
                    wrap.className = "flex flex-col gap-1.5";

                    if (field.type === "range") {
                        wrap.innerHTML = `
                            <div class="flex justify-between text-[11px] font-mono">
                                <span class="text-slate-400">${field.label}</span>
                                <span class="text-cyan-400 font-bold" id="val-${key}">${val}</span>
                            </div>
                            <input type="range" min="${field.min}" max="${field.max}" step="${field.step}" value="${val}"
                                oninput="updateParamValue('${key}', this.value)" 
                                class="w-full accent-cyan-500 bg-slate-900 border border-slate-700 rounded-lg appearance-none h-1 cursor-pointer">
                        `;
                    } else if (field.type === "color") {
                        const rgbToHex = (r, g, b) => '#' + [r, g, b].map(x => {
                            const hex = x.toString(16);
                            return hex.length === 1 ? '0' + hex : hex;
                        }).join('');
                        const hexVal = rgbToHex(val[0], val[1], val[2]);

                        wrap.innerHTML = `
                            <div class="flex justify-between items-center text-[11px] font-mono">
                                <span class="text-slate-400">${field.label}</span>
                                <input type="color" value="${hexVal}" onchange="updateColorParam('${key}', this.value)" class="bg-transparent border-0 outline-none w-8 h-6 cursor-pointer">
                            </div>
                        `;
                    } else if (field.type === "toggle") {
                        wrap.innerHTML = `
                            <div class="flex justify-between items-center text-[11px] font-mono">
                                <span class="text-slate-400">${field.label}</span>
                                <button onclick="updateToggleParam('${key}', ${!val})" class="text-cyan-400 text-lg">
                                    <i class="fa-solid ${val ? 'fa-toggle-on':'fa-toggle-off'}"></i>
                                </button>
                            </div>
                        `;
                    }
                    root.appendChild(wrap);
                });
            }

            async function updateParamValue(key, val) {
                document.getElementById(`val-${key}`).textContent = val;
                await fetch('/api/effects/param', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, value: parseFloat(val) })
                });
            }

            async function updateColorParam(key, hexVal) {
                const hexToRgb = hex => hex.replace(/^#?([a-f\d])([a-f\d])([a-f\d])$/i, (m, r, g, b) => '#' + r + r + g + g + b + b)
                    .substring(1).match(/.{2}/g).map(x => parseInt(x, 16));
                
                const rgb = hexToRgb(hexVal);
                await fetch('/api/effects/param', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, value: rgb })
                });
            }
            
            async function updateToggleParam(key, boolVal) {
                await fetch('/api/effects/param', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ key, value: boolVal })
                });
                await fetchEffects(); // reload form
            }

            async function changeEffect(effName) {
                const res = await fetch('/api/effects/select', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ effect_name: effName })
                });
                const data = await res.json();
                activeEffect = data.active;
                document.getElementById("active-shader-title").textContent = activeEffect.replace(/([A-Z])/g, ' $1').trim();
                
                const panel = document.getElementById("shader-gif-panel");
                if (activeEffect === "GifPlayer") panel.classList.remove("hidden");
                else panel.classList.add("hidden");
                
                renderEffectsList();
                renderEffectParameters(data.params);
            }
            
            // --- Custom drag-and-drop GIF upload parsing logic ---
            async function handleGifSelect(input) {
                if (input.files && input.files[0]) {
                    await uploadGifToServer(input.files[0]);
                }
            }
            
            async function handleGifDrop(e) {
                e.preventDefault();
                if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                    await uploadGifToServer(e.dataTransfer.files[0]);
                }
            }
            
            async function uploadGifToServer(file) {
                try {
                    const res = await fetch('/api/upload/gif', {
                        method: 'POST',
                        headers: { 'Content-Type': 'image/gif' },
                        body: file
                    });
                    const data = await res.json();
                    if (data.status === "ok") {
                        alert("Custom calibration animation loaded successfully!");
                        await fetchGifLibrary();
                    }
                } catch(e) {
                    console.error("Failed to upload animation asset:", e);
                }
            }

            // --- TAB 4: Hardware Settings tab ---
            function renderHardwareTab() {
                const root = document.getElementById("hardware-cards-container");
                root.innerHTML = "";

                devices.forEach(dev => {
                    const el = document.createElement("div");
                    el.className = "glass-panel p-4 rounded-xl border border-slate-900 flex flex-col justify-between gap-4";
                    
                    let shapeOptions = `
                        <option value="procedural" ${dev.active_profile === 'procedural' ? 'selected':''}>Procedural Auto Shape</option>
                    `;
                    Object.keys(dev.custom_profiles).forEach(profName => {
                        shapeOptions += `<option value="profile:${profName}" ${dev.active_profile === 'profile:'+profName ? 'selected':''}>Custom: ${profName}</option>`;
                    });

                    el.innerHTML = `
                        <div class="flex items-center justify-between">
                            <div class="flex items-center gap-3">
                                <div class="p-2 bg-slate-950 border border-slate-800 text-cyan-400 rounded-lg">
                                    <i class="fa-solid ${dev.form_type.startsWith('KEYBOARD') ? 'fa-keyboard' : (dev.form_type.startsWith('RAM') ? 'fa-memory' : (dev.form_type.startsWith('STRIMER') ? 'fa-lines-leaning':'fa-fan'))}"></i>
                                </div>
                                <div>
                                    <h4 class="text-xs font-bold text-slate-300 font-mono tracking-tight">${dev.name}</h4>
                                    <p class="text-[10px] text-slate-500 font-mono">Form Factor: ${dev.form_type}</p>
                                </div>
                            </div>
                            <button onclick="toggleDevice('${dev.id}')" class="text-xs ${dev.enabled ? 'text-cyan-400':'text-slate-600'}">
                                <i class="fa-solid ${dev.enabled ? 'fa-toggle-on':'fa-toggle-off'} text-xl"></i>
                            </button>
                        </div>

                        <div class="flex flex-col gap-2 border-t border-slate-900 pt-3">
                            <span class="text-[10px] font-mono text-slate-400 uppercase tracking-wider">Spatial Auto-Ordering</span>
                            <div class="grid grid-cols-3 gap-2 font-mono text-[10px]">
                                <button onclick="autoOrderDevice('${dev.id}', 'left_to_right')" class="py-1 bg-slate-900 border border-slate-800 rounded hover:border-cyan-500/40 text-slate-300">Left-Right</button>
                                <button onclick="autoOrderDevice('${dev.id}', 'top_to_bottom')" class="py-1 bg-slate-900 border border-slate-800 rounded hover:border-cyan-500/40 text-slate-300">Top-Bottom</button>
                                <button onclick="autoOrderDevice('${dev.id}', 'clockwise')" class="py-1 bg-slate-900 border border-slate-800 rounded hover:border-cyan-500/40 text-slate-300">Radial</button>
                            </div>
                        </div>

                        <!-- Dynamic Form Profile Switcher -->
                        <div class="flex flex-col gap-1.5 border-t border-slate-900 pt-2 text-[10px] font-mono">
                            <label class="text-slate-400">Transform Form profile Appearance</label>
                            <select onchange="updateDeviceProfile('${dev.id}', this.value)" class="w-full bg-slate-900 border border-slate-800 rounded py-1 px-2 outline-none text-slate-300">
                                <option value="KEYBOARD" ${dev.form_type === 'KEYBOARD' ? 'selected':''}>Keyboard</option>
                                <option value="RAM" ${dev.form_type === 'RAM' ? 'selected':''}>RAM Module</option>
                                <option value="STRIMER_8PIN" ${dev.form_type === 'STRIMER_8PIN' ? 'selected':''}>Lian Li Strimer (8-Pin Ribbon)</option>
                                <option value="STRIMER_24PIN" ${dev.form_type === 'STRIMER_24PIN' ? 'selected':''}>Lian Li Strimer (24-Pin Ribbon)</option>
                                <option value="STRIP" ${dev.form_type === 'STRIP' ? 'selected':''}>Linear LED Strip</option>
                                <option value="FAN" ${dev.form_type === 'FAN' ? 'selected':''}>Cooling Fan Ring</option>
                            </select>
                        </div>
                        
                        <!-- Named Profile Database Swapper -->
                        <div class="flex flex-col gap-1.5 border-t border-slate-900/60 pt-2 text-[10px] font-mono">
                            <label class="text-slate-400">Current Mapping Coordinates Array</label>
                            <div class="flex gap-2">
                                <select onchange="onSelectNamedProfile('${dev.id}', this.value)" class="flex-1 bg-slate-900 border border-slate-800 rounded py-1 px-2 outline-none text-slate-300 font-mono text-[9px]">
                                    ${shapeOptions}
                                </select>
                                ${dev.active_profile.startsWith('profile:') ? 
                                    `<button onclick="deleteNamedProfilePrompt('${dev.id}', '${dev.active_profile.replace('profile:', '')}')" class="px-2 bg-slate-950 border border-slate-800 hover:border-pink-500 text-pink-500 rounded text-[10px]"><i class="fa-solid fa-trash"></i></button>` : ''
                                }
                            </div>
                        </div>

                        <div class="flex items-center justify-between text-[10px] font-mono border-t border-slate-900 pt-3">
                            <span class="text-slate-500">Total Indexing Count: ${dev.led_count}</span>
                            <button onclick="openCalibrationModal('${dev.id}')" class="px-3 py-1 bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 rounded hover:bg-cyan-500 hover:text-slate-950 font-bold transition-all">
                                <i class="fa-solid fa-arrows-spin mr-1"></i> manual Pin mapping
                            </button>
                        </div>
                    `;
                    root.appendChild(el);
                });
            }

            async function updateDeviceProfile(id, formType) {
                const dev = devices.find(d => d.id === id);
                if (!dev) return;
                dev.form_type = formType;
                
                await fetch(`/api/devices/${id}/bounds`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        x: dev.x,
                        y: dev.y,
                        width: dev.width,
                        height: dev.height,
                        form_type: formType,
                        active_profile: dev.active_profile,
                        custom_profiles: dev.custom_profiles,
                        rotation: dev.rotation || 0,
                        hidden_in_layout: dev.hidden_in_layout || false
                    })
                });
                await fetchDevices();
            }
            
            async function onSelectNamedProfile(deviceId, targetValue) {
                let apiPath = `/api/devices/${deviceId}/profile/${targetValue.replace('profile:', '')}/select`;
                if (targetValue === "procedural") {
                    apiPath = `/api/devices/${deviceId}/profile/procedural/select`;
                }
                
                await fetch(apiPath, { method: "POST" });
                await fetchDevices();
            }
            
            async function deleteNamedProfilePrompt(deviceId, profileName) {
                if (confirm(`Are you sure you want to delete custom profile "${profileName}"?`)) {
                    await fetch(`/api/devices/${deviceId}/profile/${profileName}`, { method: "DELETE" });
                    await fetchDevices();
                }
            }

            async function toggleDevice(id) {
                const res = await fetch(`/api/devices/${id}/toggle`, { method: "POST" });
                const data = await res.json();
                const dev = devices.find(d => d.id === id);
                if (dev) dev.enabled = data.enabled;
                renderHardwareTab();
            }

            async function autoOrderDevice(deviceId, mode) {
                const res = await fetch(`/api/devices/${deviceId}/auto_order?mode=${mode}`, { method: "POST" });
                const data = await res.json();
                const dev = devices.find(d => d.id === deviceId);
                if (dev) dev.led_order = data.led_order;
                alert(`Calculated spatial ordering sequence: [${data.led_order.slice(0, 5)}...]`);
            }

            // --- TAB 5: Engine Settings Configuration ---
            async function saveGlobalSettings() {
                const host = document.getElementById("setting-host").value;
                const port = parseInt(document.getElementById("setting-port").value);
                const fps = parseInt(document.getElementById("setting-fps").value);
                const audioMode = document.getElementById("setting-audio-mode").value;
                const audioDeviceId = document.getElementById("setting-audio-device").value;
                const canvasRes = parseInt(document.getElementById("setting-canvas-res").value);
                const noiseGate = parseFloat(document.getElementById("setting-noise-gate").value);

                await fetch('/api/settings', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        openrgb_host: host,
                        openrgb_port: port,
                        target_fps: fps,
                        canvas_width: canvasRes,
                        audio_mode: audioMode,
                        audio_device_id: audioDeviceId,
                        audio_emulation: audioEmulatedState,
                        audio_noise_gate: noiseGate
                    })
                });

                document.getElementById("active-fps-display").textContent = `Target: ${fps} FPS`;
                alert("Core server configuration modified.");
                await fetchAudioHardware();
                await fetchConfig();
                await fetchDevices();
            }

            // --- Manual Pin mapping Modal Logic ---
            async function highlightPhysicalLed(deviceId, ledIndex) {
                await fetch(`/api/devices/${deviceId}/highlight/${ledIndex}`, { method: "POST" });
            }

            async function clearDeviceHighlight() {
                await fetch('/api/devices/highlight/clear', { method: "POST" });
            }

            // --- Local Calibration Modal Studio Engine ---
            function openCalibrationModal(deviceId) {
                currentCalibratorDeviceId = deviceId;
                const dev = devices.find(d => d.id === deviceId);
                if (!dev) return;

                document.getElementById("cal-modal-title").textContent = dev.name;
                
                if (dev.active_profile.startsWith("profile:") && dev.custom_profiles[dev.active_profile.replace("profile:", "")] != null) {
                    localCalCoords = JSON.parse(JSON.stringify(dev.custom_profiles[dev.active_profile.replace("profile:", "")]));
                } else {
                    localCalCoords = JSON.parse(JSON.stringify(dev.local_coords));
                }

                calGridLockEnabled = false;
                calGridDivisions = 16;
                document.getElementById("cal-setting-divisions").value = 16;
                document.getElementById("cal-val-divisions").textContent = 16;
                updateCalGridLockUI();

                renderCalLedList();
                renderCalWorkspace();

                document.getElementById("calibration-modal").style.display = "flex";
            }

            // --- Window controls toggle ---
            function toggleCalibrationWindowControls() {
                // unused placeholder
            }

            function onCalDivisionsChange(val) {
                calGridDivisions = parseInt(val);
                document.getElementById("cal-val-divisions").textContent = val;
                renderCalWorkspace();
            }

            function onCalLedSearch(val) {
                calLedSearchQuery = val;
                renderCalLedList();
            }

            function renderCalLedList() {
                const container = document.getElementById("cal-led-list-container");
                container.innerHTML = "";

                localCalCoords.forEach((coord, i) => {
                    if (calLedSearchQuery && !`led ${i}`.includes(calLedSearchQuery.toLowerCase())) return;

                    const activeBorder = activeHighlightNodeIdx === i ? 'border-cyan-500 bg-slate-900' : 'border-slate-900 bg-slate-950/40';
                    const item = document.createElement("div");
                    item.className = `p-2 rounded border flex flex-col gap-1.5 font-mono text-[9px] transition-all ${activeBorder}`;
                    
                    item.innerHTML = `
                        <div class="flex justify-between items-center text-slate-400">
                            <span class="font-bold text-slate-300">LED #${i}</span>
                            <span class="text-[7px]">PIN ADDRESS</span>
                        </div>
                        <div class="grid grid-cols-2 gap-2 text-slate-200">
                            <div class="flex items-center gap-1">
                                <span class="text-slate-500">X:</span>
                                <input type="number" step="0.001" min="0" max="1" value="${coord[0].toFixed(3)}" 
                                    onfocus="focusCalLedNode(${i})" 
                                    onchange="updateCalNodeCoordsFromInput(${i}, 'x', this.value)"
                                    class="w-full bg-slate-950 border border-slate-800 rounded px-1.5 py-0.5 text-cyan-400 outline-none focus:border-cyan-500 font-mono">
                            </div>
                            <div class="flex items-center gap-1">
                                <span class="text-slate-500">Y:</span>
                                <input type="number" step="0.001" min="0" max="1" value="${coord[1].toFixed(3)}" 
                                    onfocus="focusCalLedNode(${i})" 
                                    onchange="updateCalNodeCoordsFromInput(${i}, 'y', this.value)"
                                    class="w-full bg-slate-950 border border-slate-800 rounded px-1.5 py-0.5 text-cyan-400 outline-none focus:border-cyan-500 font-mono">
                            </div>
                        </div>
                    `;
                    container.appendChild(item);
                });
            }

            function focusCalLedNode(ledIndex) {
                activeHighlightNodeIdx = ledIndex;
                highlightPhysicalLed(currentCalibratorDeviceId, ledIndex);
                renderCalWorkspace();
            }

            // --- Coordinate and vector calculators ---
            function updateCalNodeCoordsFromInput(ledIndex, axis, val) {
                let parsed = parseFloat(val);
                if (isNaN(parsed)) parsed = 0.0;
                parsed = Math.max(0, Math.min(1, parsed));

                if (axis === 'x') localCalCoords[ledIndex][0] = parsed;
                else localCalCoords[ledIndex][1] = parsed;

                renderCalWorkspace();
            }

            function startDragCalNode(e, ledIndex) {
                e.preventDefault();
                e.stopPropagation();
                activeDragCalNodeIdx = ledIndex;
                activeHighlightNodeIdx = ledIndex;
                highlightPhysicalLed(currentCalibratorDeviceId, ledIndex);
                
                document.onmousemove = moveDragCalNode;
                document.onmouseup = stopDragCalNode;
            }

            function moveDragCalNode(e) {
                if (activeDragCalNodeIdx === null) return;
                const parent = document.getElementById("cal-workspace-bounds").getBoundingClientRect();
                
                let x = (e.clientX - parent.left) / parent.width;
                let y = (e.clientY - parent.top) / parent.height;

                x = Math.max(0, Math.min(1, x));
                y = Math.max(0, Math.min(1, y));

                if (calGridLockEnabled) {
                    const divs = calGridDivisions;
                    x = Math.round(x * divs) / divs;
                    y = Math.round(y * divs) / divs;
                }

                localCalCoords[activeDragCalNodeIdx] = [x, y];
                renderCalLedList();
                renderCalWorkspace();
            }

            function stopDragCalNode() {
                activeDragCalNodeIdx = null;
                document.onmousemove = null;
                document.onmouseup = null;
            }

            function renderCalWorkspace() {
                const root = document.getElementById("cal-nodes-root");
                const svg = document.getElementById("cal-svg");
                root.innerHTML = "";
                svg.innerHTML = "";

                const parent = document.getElementById("cal-workspace-bounds").getBoundingClientRect();
                
                renderCalGridOverlay();

                let pathData = "";
                localCalCoords.forEach((coord, i) => {
                    const pxX = coord[0] * parent.width;
                    const pxY = coord[1] * parent.height;
                    
                    if (i === 0) pathData += `M ${pxX} ${pxY}`;
                    else pathData += ` L ${pxX} ${pxY}`;

                    const node = document.createElement("div");
                    const isSelected = activeHighlightNodeIdx === i;
                    const glowClass = isSelected ? 'border-cyan-400 bg-cyan-400 shadow-[0_0_8px_#06b6d4]' : 'border-slate-950 bg-pink-500 hover:bg-cyan-400';
                    node.className = `absolute h-2.5 w-2.5 rounded-full border cursor-grab active:cursor-grabbing transition-all z-20 ${glowClass}`;
                    node.style.left = `${coord[0]*100}%`;
                    node.style.top = `${coord[1]*100}%`;
                    node.style.transform = "translate(-50%, -50%)";

                    node.onmousedown = (e) => startDragCalNode(e, i);
                    
                    node.onmouseenter = () => {
                        activeHighlightNodeIdx = i;
                        highlightPhysicalLed(currentCalibratorDeviceId, i);
                        renderCalWorkspace();
                    };
                    node.onmouseleave = () => {
                        activeHighlightNodeIdx = null;
                        clearDeviceHighlight();
                        renderCalWorkspace();
                    };

                    root.appendChild(node);
                });

                if (localCalCoords.length > 1) {
                    const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
                    path.setAttribute("d", pathData);
                    path.setAttribute("fill", "none");
                    path.setAttribute("stroke", "rgba(6,182,212,0.2)");
                    path.setAttribute("stroke-width", "1");
                    svg.appendChild(path);
                }
            }

            function renderCalGridOverlay() {
                const overlay = document.getElementById("cal-grid-overlay");
                overlay.innerHTML = "";
                if (!calGridLockEnabled) return;

                const parent = document.getElementById("cal-workspace-bounds").getBoundingClientRect();
                let gridHTML = "";

                for (let i = 1; i < calGridDivisions; i++) {
                    const y = (i / calGridDivisions) * 100;
                    gridHTML += `<div class="absolute inset-x-0 border-t border-slate-800" style="top: ${y}%"></div>`;
                }
                for (let i = 1; i < calGridDivisions; i++) {
                    const x = (i / calGridDivisions) * 100;
                    gridHTML += `<div class="absolute inset-y-0 border-l border-slate-800" style="left: ${x}%"></div>`;
                }

                overlay.innerHTML = gridHTML;
            }

            async function resetCalibrationToDefault() {
                if (confirm("Reset current pins map to standard auto shape?")) {
                    const dev = devices.find(d => d.id === currentCalibratorDeviceId);
                    if (!dev) return;
                    
                    await fetch(`/api/devices/${dev.id}/profile/procedural/select`, { method: "POST" });
                    await closeCalibrationModal();
                    await fetchDevices();
                }
            }

            async function saveCalibrationAndClose() {
                const profileName = prompt("Enter a name for this custom layout profile:", "Custom Curve");
                if (!profileName || profileName.trim() === "") {
                    return;
                }
                
                const sanitizedName = profileName.trim();
                const dev = devices.find(d => d.id === currentCalibratorDeviceId);
                if (!dev) return;

                await fetch(`/api/devices/${dev.id}/profile/${sanitizedName}`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(localCalCoords)
                });
                
                await closeCalibrationModal();
                await fetchDevices();
            }

            async function closeCalibrationModal() {
                document.getElementById("calibration-modal").style.display = "none";
                currentCalibratorDeviceId = "";
                localCalCoords = [];
                activeDragCalNodeIdx = null;
                activeHighlightNodeIdx = null;
                await clearDeviceHighlight();
            }

            // --- DYNAMIC SHAPE EXPLORER LIBRARY MODULES ---
            function onShapeLibrarySearch(val) {
                calShapeLibrarySearchQuery = val;
                renderShapeLibraryList();
            }

            // --- GIF Library search & filters ---
            function onGifSearch(val) {
                gifSearchQuery = val;
                renderGifLibraryList();
            }

            function filterShapeLibrary(category) {
                calShapeLibraryCategory = category;
                
                const pills = ["all", "keyboard", "fan", "ram", "strimer"];
                pills.forEach(p => {
                    const el = document.getElementById(`shape-pill-${p}`);
                    if (p === category) el.classList.add("active");
                    else el.classList.remove("active");
                });

                renderShapeLibraryList();
            }

            function renderShapeLibraryList() {
                const container = document.getElementById("cal-shapes-container");
                container.innerHTML = "";

                Object.keys(standardLibraryPresets).forEach(name => {
                    const p = standardLibraryPresets[name];
                    
                    if (calShapeLibrarySearchQuery && !name.toLowerCase().includes(calShapeLibrarySearchQuery.toLowerCase())) return;
                    if (calShapeLibraryCategory !== "all" && p.category.toLowerCase() !== calShapeLibraryCategory) return;

                    const el = document.createElement("div");
                    el.className = "p-2 bg-slate-950/40 hover:bg-slate-900 border border-slate-900 rounded cursor-pointer transition-colors flex items-center justify-between";
                    el.onclick = () => applyPresetShapeToCalibrator(p.generator, p.size);

                    el.innerHTML = `
                        <div>
                            <span class="text-slate-300 font-bold block">${name}</span>
                            <span class="text-[8px] text-slate-500 block uppercase">${p.category} PRESET (${p.size} LEDs)</span>
                        </div>
                        <span class="text-[9px] text-cyan-400 font-bold uppercase"><i class="fa-solid fa-plus-circle"></i> Load</span>
                    `;
                    container.appendChild(el);
                });
            }

            function applyPresetShapeToCalibrator(generatorName, presetSize) {
                const dev = devices.find(d => d.id === currentCalibratorDeviceId);
                if (!dev) return;

                if (dev.led_count !== presetSize) {
                    if (!confirm(`Warning: Your physical device has ${dev.led_count} LEDs, but this preset is structured for ${presetSize} LEDs. Applying this shape may distort the node layout scaling. Load anyway?`)) {
                        return;
                    }
                }

                let generatedCoords = [];
                if (generatorName.startsWith("keyboard")) {
                    const rows = 6, cols = Math.ceil(dev.led_count / rows);
                    for (let i = 0; i < dev.led_count; i++) {
                        const r = Math.floor(i / cols), c = i % cols;
                        generatedCoords.push([
                            0.05 + (c / Math.max(1, cols - 1)) * 0.9,
                            0.08 + (r / Math.max(1, rows - 1)) * 0.84
                        ]);
                    }
                } else if (generatorName.startsWith("ring")) {
                    for (let i = 0; i < dev.led_count; i++) {
                        const angle = (i / dev.led_count) * 2.0 * Math.PI;
                        generatedCoords.push([
                            0.5 + 0.4 * Math.cos(angle),
                            0.5 + 0.4 * Math.sin(angle)
                        ]);
                    }
                } else if (generatorName === "ram_inline") {
                    for (let i = 0; i < dev.led_count; i++) {
                        generatedCoords.push([0.5, 0.1 + (i / Math.max(1, dev.led_count - 1)) * 0.8]);
                    }
                } else if (generatorName.startsWith("strimer")) {
                    const num_lines = generatorName === "strimer_24" ? 12 : 8;
                    const ledsPerLine = Math.ceil(dev.led_count / num_lines);
                    for (let i = 0; i < dev.led_count; i++) {
                        const lineIdx = Math.floor(i / ledsPerLine);
                        const ledIdx = i % ledsPerLine;
                        generatedCoords.push([
                            0.08 + (lineIdx / Math.max(1, num_lines - 1)) * 0.84,
                            0.05 + (ledIdx / Math.max(1, ledsPerLine - 1)) * 0.9
                        ]);
                    }
                } else {
                    for (let i = 0; i < dev.led_count; i++) {
                        generatedCoords.push([0.05 + (i / Math.max(1, dev.led_count - 1)) * 0.9, 0.5]);
                    }
                }

                localCalCoords = generatedCoords;
                renderCalLedList();
                renderCalWorkspace();
            }

            function triggerProceduralGenerator(type) {
                if (type === "linear") applyPresetShapeToCalibrator("linear", localCalCoords.length);
                if (type === "radial") applyPresetShapeToCalibrator("ring", localCalCoords.length);
                if (type === "matrix") applyPresetShapeToCalibrator("keyboard", localCalCoords.length);
            }

            // --- WebSocket Frame Preview & Telemetry Sync ---
            function setupWebSocket() {
                const loc = window.location;
                const wsUrl = "ws://" + loc.host + "/ws/canvas_frame";
                const ws = new WebSocket(wsUrl);
                const canvas = document.getElementById("stream-preview");
                const ctx = canvas.getContext("2d");
                
                const calCanvas = document.getElementById("cal-stream-preview");
                const calCtx = calCanvas.getContext("2d");

                ws.onmessage = async (event) => {
                    const packet = JSON.parse(event.data);
                    
                    const img = new Image();
                    img.onload = () => {
                        canvas.width = img.width;
                        canvas.height = img.height;
                        ctx.drawImage(img, 0, 0);
                        
                        if (currentCalibratorDeviceId !== "") {
                            calCanvas.width = img.width;
                            calCanvas.height = img.height;
                            calCtx.drawImage(img, 0, 0);
                        }
                    };
                    img.src = "data:image/jpeg;base64," + packet.image;
                    
                    if (packet.audio) {
                        document.getElementById("telemetry-bar-lows").style.width = `${packet.audio.lows * 100}%`;
                        document.getElementById("telemetry-bar-mids").style.width = `${packet.audio.mids * 100}%`;
                        document.getElementById("telemetry-bar-highs").style.width = `${packet.audio.highs * 100}%`;
                        
                        if (currentCalibratorDeviceId !== "") {
                            document.getElementById("cal-meter-lows").style.width = `${packet.audio.lows * 100}%`;
                            document.getElementById("cal-meter-mids").style.width = `${packet.audio.mids * 100}%`;
                            document.getElementById("cal-meter-highs").style.width = `${packet.audio.highs * 100}%`;
                        }
                    }
                    
                    if (activeTab === "layout") {
                        fetchDevicesColors();
                    }
                };

                ws.onclose = () => {
                    setTimeout(setupWebSocket, 2000);
                };
            }

            async function fetchDevicesColors() {
                const res = await fetch('/api/devices');
                const updated = await res.json();
                devices.forEach(d => {
                    const found = updated.find(u => u.id === d.id);
                    if (found && found.demo_colors) {
                        d.demo_colors = found.demo_colors;
                    }
                });
                renderWorkspaceDevices();
            }

            function updateRefOpacity(val) {
                document.getElementById("stream-preview").style.opacity = parseFloat(val);
            }

            window.onload = waitForBackend;
        </script>
    </body>
    </html>
'''