"""
Detects whether a Microsoft Teams call is likely in progress.

Teams does not expose a public "call started" API. The most reliable
practical signal on Windows is: Teams is running AND the microphone is
currently in active use (Windows records this per-app in the registry
under the microphone CapabilityAccessManager store).

When you join a call, Teams opens the mic and Windows writes a
"LastUsedTimeStop = 0" marker for that app (0 means "in use right now").
When the call ends, Windows writes a real timestamp. We read that.

This is paired with a user prompt in the app, so a false positive never
silently records.
"""

import winreg

import psutil

from . import config

# Registry roots where Windows stores per-app microphone usage.
_MIC_STORES = [
    (winreg.HKEY_CURRENT_USER,
     r"Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone"),
    (winreg.HKEY_CURRENT_USER,
     r"Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone\NonPackaged"),
]


def is_teams_running():
    """True if a Teams process is currently running."""
    names = set(config.TEAMS_PROCESS_NAMES)
    for proc in psutil.process_iter(["name"]):
        try:
            name = (proc.info["name"] or "").lower()
            if name in names:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def _app_is_using_mic(subkey_name):
    """True if the given CapabilityAccessManager subkey marks the mic in use."""
    # A LastUsedTimeStop value of 0 means the app is using the mic right now.
    try:
        value, _ = winreg.QueryValueEx(subkey_name, "LastUsedTimeStop")
        return value == 0
    except FileNotFoundError:
        return False
    except OSError:
        return False


def _mic_in_use_by_teams():
    """
    Scan the microphone consent store for any app actively using the mic
    whose key name looks like Teams. Returns True if found.
    """
    for root, path in _MIC_STORES:
        try:
            store = winreg.OpenKey(root, path)
        except OSError:
            continue
        try:
            index = 0
            while True:
                try:
                    child_name = winreg.EnumKey(store, index)
                except OSError:
                    break
                index += 1

                looks_like_teams = (
                    "teams" in child_name.lower()
                    or "msteams" in child_name.lower()
                )
                if not looks_like_teams:
                    continue

                try:
                    child = winreg.OpenKey(store, child_name)
                except OSError:
                    continue
                try:
                    if _app_is_using_mic(child):
                        return True
                finally:
                    winreg.CloseKey(child)
        finally:
            winreg.CloseKey(store)
    return False


def _any_app_using_mic():
    """
    Fallback: True if ANY app currently has the mic open.
    Used only when we can't find a Teams-specific entry but Teams is running.
    """
    for root, path in _MIC_STORES:
        try:
            store = winreg.OpenKey(root, path)
        except OSError:
            continue
        try:
            index = 0
            while True:
                try:
                    child_name = winreg.EnumKey(store, index)
                except OSError:
                    break
                index += 1
                try:
                    child = winreg.OpenKey(store, child_name)
                except OSError:
                    continue
                try:
                    if _app_is_using_mic(child):
                        return True
                finally:
                    winreg.CloseKey(child)
        finally:
            winreg.CloseKey(store)
    return False


def is_call_active():
    """
    Best-effort guess at whether a Teams call is active.

    Logic:
      - Teams must be running.
      - The microphone must be actively in use (by Teams specifically,
        or by some app while Teams is running).

    Returns True only when both hold.
    """
    if not is_teams_running():
        return False

    if _mic_in_use_by_teams():
        return True

    # Teams running + mic in use by something is a strong call signal too,
    # since the browser/other apps rarely hold the mic open silently.
    return _any_app_using_mic()
