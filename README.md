# Albion Fishing Bot

A screen-reading fishing helper for Albion Online, written in Python as a
learning project around computer vision and automation.

It watches the water around your bobber, reacts when a fish bites, plays the
reel-in minigame by tracking the bobber inside the bar, and recasts at the next
spot you recorded.

> **Works on any screen resolution.** Earlier versions only worked at exactly
> 1920x1080. All pixel measurements are now derived from your actual screen, and
> anything that cannot be derived can be recorded or calibrated in the app.

---

## Setup

### Windows (the easy way)

1. Install **Python 3.10 or newer** from <https://www.python.org/downloads/>.
   During the installation, tick **"Add python.exe to PATH"**.
2. Download this project (green **Code** button -> **Download ZIP**) and unpack it.
3. Double-click **`start.bat`**.

That is it. `start.bat` creates its own Python environment, installs everything
it needs, and starts the bot. The first run takes a minute or two; after that it
starts immediately.

### Any platform (manual)

```bash
python -m venv .venv
.venv/Scripts/activate      # Windows
# source .venv/bin/activate # macOS / Linux
pip install -r requirements.txt
python dashboard.py
```

---

## Using it

Three steps:

**1. Record your fishing spots** — Tab **Spots**

Stand at the water in Albion, point the mouse where you want to cast, and press
**F2**. Repeat for as many spots as you like; the bot cycles through them. They
are saved, so you only do this once per fishing location.

**2. Check the screen** — Tab **Settings**

Pick the monitor the game runs on. The **Start** tab shows the detected
resolution and UI scale — make sure it matches your game.

**3. Start** — Tab **Start**

Press **Start** or **F3**. Press **F3** again to stop.

| Hotkey | Does |
|--------|------|
| **F2** | Record the current mouse position as a fishing spot |
| **F3** | Start / stop the bot |
| **F4** | Freeze the screen to calibrate the fishing bar |

### Optional extras — Tab **Extras**

- **Use food** — presses your food hotbar key on an interval.
- **Use bait** — finds the bait in your inventory by image and applies it every
  N fish. Pick which bait tier you carry.

---

## How the resolution independence works

| What | How it adapts |
|------|---------------|
| Fishing bar (minigame) | Centred horizontally, positioned at a fixed fraction of screen height, sized by UI scale. Overridable with **Calibrate fishing bar**. |
| Bobber template | The reference image is 1080p; it is rescaled to `screen height / 1080` and matched in a narrow band around that scale. |
| Bite detection box | A 125px box at 1080p, scaled by UI scale, clamped to the monitor. |
| Motion threshold | Normalised by area, so the same sensitivity value behaves the same on every resolution. |
| Bait / Use button | Located by image matching, not by fixed coordinates. |
| Fishing spots, food slots | Recorded by you — never guessed. |
| Windows display scaling | The app declares itself DPI-aware, so a display set to 125% or 150% no longer shifts every coordinate. |

### Calibrating the fishing bar

If your Albion UI scale differs from the default, or you play windowed, tell the
bot where the bar really is:

1. Start fishing.
2. **The moment the reel-in bar appears, press F4.**
3. The screen freezes on that instant. Drag a box tightly around the bar — take
   as long as you like, nothing is running.

The minigame only lasts a couple of seconds, which is why the screen is frozen
rather than live: there is no way to alt-tab and trace a 23-pixel bar in time.
A red dashed rectangle shows where the bot is currently looking, so you can see
the mismatch directly.

Calibration is stored as a *position on the screen* plus a *size in 1080p
reference pixels*, not as raw pixels — so it keeps working if you later change
resolution.

---

## Troubleshooting

**"Python was not found"**
Python is not installed, or the *Add to PATH* box was not ticked during
installation. Reinstall Python and tick it.

**The bot casts and says "Bite!", but never reels anything in**
The fishing bar is not where the bot looks, so it never finds the bobber. Start
fishing and press **F4** while the bar is on screen — see *Calibrating the
fishing bar* above.

For a detailed report, run `.venv\Scripts\python.exe diagnose.py`, go fishing,
and read what it prints: it saves what the bot sees and scores how well the
bobber template matches.

**It reacts constantly, or never**
Adjust **Bite sensitivity** in **Settings**. Lower = more sensitive. Turn on
**Show debug windows** to see exactly what the bot sees.

**F2 / F3 do nothing**
Global hotkeys need the app to receive key events. On Windows, run `start.bat`
as administrator if Albion itself runs elevated. The buttons in the app always
work regardless.

**Everything is offset / it clicks in the wrong place**
Check that the correct monitor is selected in **Settings**, and that the
resolution shown on the **Start** tab matches the game.

**Where are my settings stored?**
`%APPDATA%\AlbionFishingBot\config.json`. Delete that file to start fresh.

---

## Project layout

| File | Purpose |
|------|---------|
| `dashboard.py` | GUI and entry point |
| `bot.py` | The fishing loop |
| `screen.py` | Resolution, DPI and coordinate scaling |
| `minigame.py` | Bobber tracking during the reel-in minigame |
| `actions.py` | Casting, food, bait |
| `positions.py` | Cycling through recorded spots |
| `region_selector.py` | Drag-to-select overlay for calibration |
| `config.py` | Saving and loading settings |

---

## Demo

[![Demo video](https://img.youtube.com/vi/4lZhj65XAwc/0.jpg)](https://youtu.be/4lZhj65XAwc)

*(Recorded with an earlier version.)*

---

## Disclaimer

This is a personal learning project, provided as-is, with no warranty and no
support. Automating gameplay violates the Albion Online terms of service and can
get your account banned. Use it at your own risk, and preferably only to study
how the code works.
