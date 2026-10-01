"""
Core recording engine. Builds and manages the FFmpeg capture process
for screen + microphone + system audio.
"""

import os
import time
import signal
import subprocess
from datetime import datetime

from . import config
from .ffmpeg_utils import find_ffmpeg, list_audio_devices, pick_device

_NO_WINDOW = 0x08000000 if os.name == "nt" else 0


class Recorder:
    """Manages a single FFmpeg recording session."""

    def __init__(self):
        self.ffmpeg_path = find_ffmpeg()
        self.process = None
        self.current_file = None
        self.mic_device = None
        self.system_device = None
        self._detect_devices()

    def is_available(self):
        """True if FFmpeg was located and we can record."""
        return self.ffmpeg_path is not None

    def _detect_devices(self):
        """Figure out which mic and system-audio devices to use."""
        if not self.ffmpeg_path:
            return
        devices = list_audio_devices(self.ffmpeg_path)

        self.mic_device = config.FORCE_MIC_DEVICE or pick_device(
            devices, ["microphone", "mic"]
        )
        self.system_device = config.FORCE_SYSTEM_AUDIO_DEVICE or pick_device(
            devices, ["stereo mix", "what u hear", "wave out", "loopback"]
        )

    def device_status(self):
        """Human-readable summary of detected devices."""
        return {
            "mic": self.mic_device or "NOT FOUND",
            "system": self.system_device or "NOT FOUND (enable 'Stereo Mix')",
        }

    @property
    def is_recording(self):
        return self.process is not None and self.process.poll() is None

    def _build_command(self, output_path):
        """Assemble the FFmpeg command based on available devices."""
        cmd = [self.ffmpeg_path, "-y"]

        # Video: capture the whole desktop.
        cmd += ["-f", "gdigrab", "-framerate", str(config.FRAMERATE), "-i", "desktop"]

        # Audio inputs (mic and/or system audio).
        audio_inputs = []
        if self.mic_device:
            cmd += ["-f", "dshow", "-i", f"audio={self.mic_device}"]
            audio_inputs.append(len(audio_inputs) + 1)  # input index (video is 0)
        if self.system_device:
            cmd += ["-f", "dshow", "-i", f"audio={self.system_device}"]
            audio_inputs.append(len(audio_inputs) + 1)

        # Video encoding.
        cmd += ["-c:v", "libx264", "-preset", config.VIDEO_PRESET, "-pix_fmt", "yuv420p"]

        # Mix the audio inputs together into one track if we have any.
        if len(audio_inputs) == 2:
            cmd += [
                "-filter_complex",
                "[1:a][2:a]amix=inputs=2:duration=longest[aout]",
                "-map", "0:v", "-map", "[aout]",
                "-c:a", "aac",
            ]
        elif len(audio_inputs) == 1:
            cmd += ["-map", "0:v", "-map", "1:a", "-c:a", "aac"]
        else:
            # No audio devices available: record video only.
            cmd += ["-map", "0:v"]

        cmd.append(output_path)
        return cmd

    def start(self):
        """Start recording. Returns the output file path."""
        if self.is_recording:
            return self.current_file
        if not self.ffmpeg_path:
            raise RuntimeError("FFmpeg not found.")

        folder = config.ensure_save_folder()
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_path = os.path.join(folder, f"teams_call_{stamp}.mp4")

        cmd = self._build_command(output_path)
        self.process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=_NO_WINDOW,
        )
        self.current_file = output_path
        return output_path

    def stop(self):
        """Stop recording gracefully so the file is finalized correctly."""
        if not self.is_recording:
            return self.current_file

        try:
            # Sending 'q' to FFmpeg's stdin lets it finalize the MP4 cleanly.
            self.process.stdin.write(b"q")
            self.process.stdin.flush()
        except Exception:
            pass

        try:
            self.process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            self.process.terminate()
            try:
                self.process.wait(timeout=4)
            except subprocess.TimeoutExpired:
                self.process.kill()

        finished = self.current_file
        self.process = None
        return finished
