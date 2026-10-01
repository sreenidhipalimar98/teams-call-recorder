"""
Teams Call Recorder - desktop UI.

A small always-on-top window that:
  - auto-detects when a Teams call starts and asks before recording
  - lets you start/stop manually at any time
  - shows a big STOP button so you can halt immediately if someone declines
  - auto-stops and saves when the call ends

You are expected to verbally inform the other participants that recording
has started. If they decline, hit STOP.
"""

import os
import sys
import threading
import tkinter as tk
from tkinter import messagebox, filedialog

from . import config
from .recorder_core import Recorder
from .call_detector import is_call_active

COLOR_IDLE = "#2d3436"
COLOR_RECORDING = "#c0392b"
COLOR_ACCENT = "#0984e3"


class RecorderApp:
    def __init__(self, root):
        self.root = root
        self.recorder = Recorder()
        self.was_call_active = False
        self.prompt_open = False

        self._build_ui()
        self._check_ffmpeg()
        self._poll_loop()

    # ---------- UI construction ----------

    def _icon_path(self):
        """Locate app.ico whether running from source or packaged."""
        if getattr(sys, "frozen", False):
            base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
        else:
            base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidate = os.path.join(base, "assets", "app.ico")
        return candidate if os.path.exists(candidate) else None

    def _build_ui(self):
        self.root.title("Teams Call Recorder")
        self.root.geometry("360x300")
        self.root.attributes("-topmost", True)
        self.root.configure(bg=COLOR_IDLE)

        icon = self._icon_path()
        if icon:
            try:
                self.root.iconbitmap(icon)
            except Exception:
                pass

        self.status_label = tk.Label(
            self.root, text="Idle", font=("Segoe UI", 16, "bold"),
            fg="white", bg=COLOR_IDLE,
        )
        self.status_label.pack(pady=(18, 4))

        self.detail_label = tk.Label(
            self.root, text="Waiting for a Teams call...",
            font=("Segoe UI", 9), fg="#dfe6e9", bg=COLOR_IDLE, wraplength=320,
        )
        self.detail_label.pack(pady=(0, 10))

        self.toggle_btn = tk.Button(
            self.root, text="Start Recording", font=("Segoe UI", 13, "bold"),
            bg=COLOR_ACCENT, fg="white", activebackground="#74b9ff",
            relief="flat", width=20, height=2, command=self.toggle_recording,
        )
        self.toggle_btn.pack(pady=6)

        self.auto_var = tk.BooleanVar(value=config.AUTO_START_ENABLED)
        self.auto_check = tk.Checkbutton(
            self.root, text="Auto-detect call and prompt me",
            variable=self.auto_var, fg="white", bg=COLOR_IDLE,
            selectcolor=COLOR_IDLE, activebackground=COLOR_IDLE,
            activeforeground="white", font=("Segoe UI", 9),
        )
        self.auto_check.pack(pady=2)

        folder_btn = tk.Button(
            self.root, text="Change save folder", font=("Segoe UI", 8),
            bg=COLOR_IDLE, fg="#b2bec3", relief="flat",
            command=self.change_folder,
        )
        folder_btn.pack(pady=(6, 0))

        self.folder_label = tk.Label(
            self.root, text=config.SAVE_FOLDER, font=("Segoe UI", 8),
            fg="#636e72", bg=COLOR_IDLE, wraplength=320,
        )
        self.folder_label.pack()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def _check_ffmpeg(self):
        if not self.recorder.is_available():
            self.detail_label.config(
                text="FFmpeg not found. Please restart the app after install."
            )
            self.toggle_btn.config(state="disabled")
            return

        devices = self.recorder.device_status()
        self.detail_label.config(
            text=f"Mic: {devices['mic']}\nSystem: {devices['system']}"
        )

    # ---------- Recording control ----------

    def toggle_recording(self):
        if self.recorder.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        try:
            path = self.recorder.start()
        except Exception as exc:
            messagebox.showerror("Recording error", str(exc))
            return
        self._set_recording_ui(path)

    def stop_recording(self):
        path = self.recorder.stop()
        self._set_idle_ui()
        if path and os.path.exists(path):
            self.detail_label.config(text=f"Saved:\n{os.path.basename(path)}")

    def _set_recording_ui(self, path):
        self.root.configure(bg=COLOR_RECORDING)
        self.status_label.config(text="● RECORDING", bg=COLOR_RECORDING)
        self.detail_label.config(
            text=f"Saving to:\n{os.path.basename(path)}", bg=COLOR_RECORDING
        )
        self.toggle_btn.config(text="STOP", bg="#ffffff", fg=COLOR_RECORDING)

    def _set_idle_ui(self):
        self.root.configure(bg=COLOR_IDLE)
        self.status_label.config(text="Idle", bg=COLOR_IDLE)
        self.detail_label.config(bg=COLOR_IDLE)
        self.toggle_btn.config(text="Start Recording", bg=COLOR_ACCENT, fg="white")

    # ---------- Folder selection ----------

    def change_folder(self):
        chosen = filedialog.askdirectory(initialdir=config.SAVE_FOLDER)
        if chosen:
            config.SAVE_FOLDER = chosen
            self.folder_label.config(text=chosen)

    # ---------- Auto-detect loop ----------

    def _poll_loop(self):
        """Runs on the Tk main loop; checks for call start/stop periodically."""
        threading.Thread(target=self._check_call_state, daemon=True).start()
        self.root.after(config.POLL_INTERVAL * 1000, self._poll_loop)

    def _check_call_state(self):
        try:
            active = is_call_active()
        except Exception:
            active = False

        # Call just started.
        if active and not self.was_call_active:
            if (self.auto_var.get() and not self.recorder.is_recording
                    and not self.prompt_open):
                self.root.after(0, self._prompt_auto_start)

        # Call just ended: auto-stop if we were recording.
        if not active and self.was_call_active:
            if self.recorder.is_recording:
                self.root.after(0, self._auto_stop)

        self.was_call_active = active

    def _prompt_auto_start(self):
        self.prompt_open = True
        answer = messagebox.askyesno(
            "Teams call detected",
            "A Teams call looks active.\n\n"
            "Remember to tell the other person that recording is starting.\n\n"
            "Start recording now?",
        )
        self.prompt_open = False
        if answer:
            self.start_recording()

    def _auto_stop(self):
        self.stop_recording()
        self.detail_label.config(text="Call ended. Recording saved.")

    # ---------- Shutdown ----------

    def on_close(self):
        if self.recorder.is_recording:
            if not messagebox.askyesno(
                "Still recording",
                "A recording is in progress. Stop and exit?",
            ):
                return
            self.recorder.stop()
        self.root.destroy()


def main():
    config.ensure_save_folder()
    root = tk.Tk()
    RecorderApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
