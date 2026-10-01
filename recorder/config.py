"""
Configuration for the Teams Call Recorder.
Edit these values to change behavior without touching the main code.
"""

import os

# Folder where recordings are saved. Change this to any folder you like.
SAVE_FOLDER = r"C:\Recordings"

# Recording quality / framerate for screen capture.
FRAMERATE = 25

# x264 encoding speed. Faster = less CPU, slightly bigger files.
# Options: ultrafast, superfast, veryfast, faster, fast, medium
VIDEO_PRESET = "veryfast"

# How often (seconds) to poll for whether a Teams call is active.
POLL_INTERVAL = 3

# Process names that indicate Teams is running (lowercase).
TEAMS_PROCESS_NAMES = ["ms-teams.exe", "teams.exe"]

# If True, the app proposes auto-start when a call is detected.
# You still confirm, and you can always stop manually.
AUTO_START_ENABLED = True

# Device names are auto-detected at runtime, but you can force them here
# if auto-detection picks the wrong device. Leave as None to auto-detect.
FORCE_MIC_DEVICE = None          # e.g. "Microphone Array (Realtek(R) Audio)"
FORCE_SYSTEM_AUDIO_DEVICE = None  # e.g. "Stereo Mix (Realtek(R) Audio)"


def ensure_save_folder():
    """Create the save folder if it does not exist."""
    os.makedirs(SAVE_FOLDER, exist_ok=True)
    return SAVE_FOLDER
