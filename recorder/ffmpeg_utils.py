"""
Helpers to locate FFmpeg and discover audio devices on Windows.
"""

import os
import re
import sys
import glob
import shutil
import subprocess

# Hide the console window FFmpeg/probe spawns (Windows only).
_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


def _bundled_ffmpeg():
    """
    Return the path to a bundled ffmpeg.exe, if present.

    When packaged with PyInstaller, bundled data is extracted to the folder
    pointed to by sys._MEIPASS. In development, we look next to the project
    in the 'vendor' folder.
    """
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        candidate = os.path.join(base, "vendor", "ffmpeg.exe")
        if os.path.exists(candidate):
            return candidate

    # Development: vendor folder at the project root.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidate = os.path.join(project_root, "vendor", "ffmpeg.exe")
    if os.path.exists(candidate):
        return candidate

    return None


def find_ffmpeg():
    """
    Locate the ffmpeg executable.
    Prefers a bundled copy, then PATH, then the winget install location.
    Returns the full path, or None if not found.
    """
    bundled = _bundled_ffmpeg()
    if bundled:
        return bundled

    on_path = shutil.which("ffmpeg")
    if on_path:
        return on_path

    # winget installs FFmpeg here; PATH may need a shell restart to see it.
    local = os.environ.get("LOCALAPPDATA", "")
    pattern = os.path.join(
        local, "Microsoft", "WinGet", "Packages",
        "Gyan.FFmpeg*", "**", "ffmpeg.exe"
    )
    matches = glob.glob(pattern, recursive=True)
    if matches:
        return matches[0]

    return None


def list_audio_devices(ffmpeg_path):
    """
    Return a list of DirectShow audio device names available on the system.
    """
    try:
        result = subprocess.run(
            [ffmpeg_path, "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
            capture_output=True, text=True, creationflags=_NO_WINDOW
        )
    except Exception:
        return []

    output = result.stderr or ""
    devices = []
    # Lines look like:  [dshow @ ...] "Device Name" (audio)
    for line in output.splitlines():
        if "(audio)" in line:
            match = re.search(r'"([^"]+)"', line)
            if match:
                devices.append(match.group(1))
    return devices


def pick_device(devices, keywords):
    """
    Pick the first device whose name contains any of the given keywords
    (case-insensitive). Returns the device name or None.
    """
    for device in devices:
        lower = device.lower()
        for kw in keywords:
            if kw.lower() in lower:
                return device
    return None
