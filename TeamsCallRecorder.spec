# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the Teams Call Recorder.

Produces a single windowed exe with FFmpeg bundled inside, so the app
is fully self-contained and needs no Python or separate FFmpeg install.
"""

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    # Bundle ffmpeg.exe and the app icon so they're available at runtime.
    datas=[('vendor/ffmpeg.exe', 'vendor'), ('assets/app.ico', 'assets')],
    hiddenimports=[
        'win32gui',
        'win32api',
        'psutil',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TeamsCallRecorder',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,           # no console window; this is a GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app.ico',   # custom app icon for the exe
)
