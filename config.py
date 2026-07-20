"""Persistent settings.

The old version forgot every setting on restart -- positions had to be recorded
again on every launch.  Settings now live in
``%APPDATA%\\AlbionFishingBot\\config.json``.
"""

import json
import os
import sys

APP_DIR_NAME = "AlbionFishingBot"

DEFAULTS = {
    # --- screen -----------------------------------------------------------
    "monitor": 1,
    "ui_scale": None,          # None = derive from resolution
    # None = derive from the resolution.  Otherwise a resolution-independent
    # spec: {"cx", "cy"} as screen fractions, {"w_ref", "h_ref"} in 1080p px.
    "minigame_region": None,
    # --- fishing ----------------------------------------------------------
    "positions": [],           # list of [x, y] spots to cast at
    "sensitivity": 0.6,        # motion threshold that counts as a bite
    "recast_after_sec": 40,    # no bite for this long -> cast again
    # --- consumables ------------------------------------------------------
    "use_food": False,
    "food_hotkey": "2",
    "food_interval_min": 30,
    "food_drag_from": None,    # optional: refill the food slot by dragging
    "food_drag_to": None,
    "use_bait": False,
    "bait_template": "TirIII.png",
    "bait_every_n_fish": 10,
    # --- interface --------------------------------------------------------
    "debug_windows": False,
    "always_on_top": True,
    "hotkey_record": "f2",
    "hotkey_toggle": "f3",
    "hotkey_freeze": "f4",
    "first_run": True,
}


def config_dir():
    base = os.environ.get("APPDATA")
    if not base:
        base = os.path.join(os.path.expanduser("~"), ".config")
    path = os.path.join(base, APP_DIR_NAME)
    os.makedirs(path, exist_ok=True)
    return path


def config_path():
    return os.path.join(config_dir(), "config.json")


def load():
    """Return the stored settings, filled up with defaults."""
    settings = dict(DEFAULTS)
    try:
        with open(config_path(), "r", encoding="utf-8") as handle:
            stored = json.load(handle)
        if isinstance(stored, dict):
            settings.update({k: v for k, v in stored.items() if k in DEFAULTS})
    except FileNotFoundError:
        pass
    except (json.JSONDecodeError, OSError) as error:
        print(f"[config] Could not read settings, using defaults: {error}")
    return settings


def save(settings):
    try:
        with open(config_path(), "w", encoding="utf-8") as handle:
            json.dump(settings, handle, indent=2)
    except OSError as error:
        print(f"[config] Could not save settings: {error}")


def resource_path(relative_path):
    """Locate a bundled file, both when run from source and from a PyInstaller exe."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)
