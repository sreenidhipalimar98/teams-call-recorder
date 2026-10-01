# Teams Call Recorder

A local Windows app that records your Teams calls (screen + your mic +
the other participants' audio) and saves them to a folder you choose.

It auto-detects when a Teams call starts and asks before recording, and
auto-stops when the call ends. A big STOP button lets you halt instantly.

## Important: consent

You are expected to **verbally inform the other participants that recording
is starting**. If anyone declines, press STOP. This tool is for recording
your own meetings with the participants' awareness.

## Download

Grab the latest `TeamsCallRecorder_Setup.exe` from the
[Releases page](https://github.com/sreenidhipalimar98/teams-call-recorder/releases)
and run it. No Python or FFmpeg install needed, everything is bundled.

On first launch Windows may show a SmartScreen prompt (the app isn't
code-signed). Click **More info > Run anyway**.

## How to run from source

Requires Python 3.10+, FFmpeg, and the packages `psutil` and `pywin32`.

```bash
pip install -r requirements.txt
python run.py
```

A small always-on-top window opens.

- **Start Recording / STOP** — manual control, works any time.
- **Auto-detect call and prompt me** — when on, the app watches for a
  Teams call and asks if you want to record. You confirm each time.
- **Change save folder** — pick where recordings go (default `C:\Recordings`).

Recordings are saved as `teams_call_YYYY-MM-DD_HH-MM-SS.mp4`.

## Audio notes

The app mixes two audio sources into one track:

- **Mic:** your microphone (your voice)
- **System audio:** "Stereo Mix" (what you hear, i.e. the other people)

If the other participants' audio is missing from a recording, enable
**Stereo Mix**:

1. Right-click the speaker icon in the taskbar > Sound settings
2. More sound settings > Recording tab
3. Right-click an empty area > Show Disabled Devices
4. Enable **Stereo Mix**

## Configuration

Edit `recorder/config.py` to change the save folder, framerate, encoding
preset, or to force specific audio devices.

## Project structure

```
run.py                     Launcher
requirements.txt           Python dependencies
recorder/
  app.py                   UI + auto-detect loop
  recorder_core.py         FFmpeg recording engine
  call_detector.py         Teams call detection
  ffmpeg_utils.py          FFmpeg + device discovery
  config.py                Settings
```

## Building from source

The repository does not include the FFmpeg binary (it's large and is
fetched locally). To build the standalone exe and installer yourself:

1. Install Python 3.10+ and the dependencies:

   ```bash
   pip install -r requirements.txt
   pip install pyinstaller pillow
   ```

2. Get FFmpeg and place it at `vendor/ffmpeg.exe`. Easiest on Windows:

   ```bash
   winget install Gyan.FFmpeg
   ```

   Then copy the installed `ffmpeg.exe` into a `vendor` folder at the
   project root.

3. (Optional) Regenerate the icon:

   ```bash
   python make_icon.py
   ```

4. Build the standalone exe:

   ```bash
   python -m PyInstaller TeamsCallRecorder.spec --noconfirm --clean
   ```

   The exe appears in `dist/`.

5. (Optional) Build the Windows installer with [Inno Setup](https://jrsoftware.org/isdl.php):

   ```bash
   "%LOCALAPPDATA%\Programs\Inno Setup 6\ISCC.exe" installer.iss
   ```

   The installer appears in `installer_output/`.
