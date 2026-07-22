import shutil
import subprocess
from typing import Dict, List, Any

def discover_system_audio_devices() -> Dict[str, List[Dict[str, Any]]]:
    inputs, outputs = [], []
    if shutil.which("pactl"):
        try:
            res = subprocess.run(["pactl", "list", "short", "sources"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0:
                for line in res.stdout.strip().split("\n"):
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[1].strip()
                        display_name = name
                        if name.startswith("alsa_input."):
                            display_name = name.replace("alsa_input.", "Mic: ").replace(".analog-stereo", "").replace("_", " ")
                        elif name.startswith("alsa_output."):
                            display_name = name.replace("alsa_output.", "Speaker: ").replace(".analog-stereo.monitor", "").replace("_", " ")
                        device_item = {"id": name, "name": display_name}
                        if ".monitor" in name: outputs.append(device_item)
                        else: inputs.append(device_item)
        except Exception as e:
            print(f"[*] Audio discovery error: {e}")
    if not inputs and not outputs and shutil.which("arecord"):
        try:
            res = subprocess.run(["arecord", "-L"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0:
                for line in res.stdout.split("\n"):
                    line = line.strip()
                    if line and not line.startswith(" ") and ":" in line:
                        inputs.append({"id": line, "name": f"ALSA: {line}"})
        except Exception:
            pass
    if not inputs: inputs.append({"id": "default", "name": "System Default Microphone"})
    if not outputs: outputs.append({"id": "@DEFAULT_MONITOR@", "name": "System Default Output (Speakers)"})
    return {"inputs": inputs, "outputs": outputs}