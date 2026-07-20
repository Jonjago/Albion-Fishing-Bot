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

## Installation (Windows)

You do not need to know anything about programming. Follow these steps in order.

### Step 1 — Install Python

1. Open <https://www.python.org/downloads/>.
2. Click the big yellow **Download Python 3.x.x** button.
3. Run the file you just downloaded.
4. **On the first installer screen, tick the box at the bottom that says
   "Add python.exe to PATH".** This is the single most common reason the bot
   fails to start. If you miss it, uninstall Python and redo this step.
5. Click **Install Now** and wait until it says *Setup was successful*.

<details>
<summary>How do I check whether Python is installed correctly?</summary>

Press <kbd>Win</kbd>+<kbd>R</kbd>, type `cmd`, press Enter, then type:

```
python --version
```

You should see something like `Python 3.12.4`. If you instead see
*"python is not recognized"*, PATH was not set — reinstall and tick the box.
</details>

### Step 2 — Download the bot

1. Go to the project page on GitHub.
2. Click the green **Code** button → **Download ZIP**.
3. Right-click the downloaded ZIP → **Extract All…** → **Extract**.

Put the folder somewhere normal like `Desktop` or `Documents`.
**Do not run it from inside the ZIP file** — Windows will not let it install
anything, and it will fail.

### Step 3 — Start it

Open the extracted folder and **double-click `start.bat`**.

A black window opens and shows:

```
 [1/3] Setting up a private Python environment (first run only)...
 [2/3] Checking required packages...
 [3/3] Starting the bot...
```

The first start takes **one to three minutes** because it downloads the
libraries it needs. Every start after that takes a few seconds.
Leave the black window open while you use the bot — closing it closes the bot.

> Windows may show a blue *"Windows protected your PC"* box, because the file is
> not signed. Click **More info → Run anyway**.

That is the whole installation. Nothing is written outside the folder except
your settings, which go to `%APPDATA%\AlbionFishingBot\config.json`.

### Installing on macOS / Linux, or manually

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python dashboard.py
```

Note that the bot reads the screen and drives mouse and keyboard, so it needs
the usual accessibility/screen-recording permissions on macOS, and an X11
session on Linux.

---

## How to run it

Start **Albion Online first**, and get your character standing at the water with
a fishing rod equipped. The bot records real screen positions, so the game has
to be visible while you set it up.

Then run `start.bat`. A small window appears with five tabs.

### 1. Record your fishing spots — tab **Spots**

Move your mouse over the spot in the water where you want to cast, and press
**F2**. A line appears in the list.

Repeat for two to four spots around you — the bot casts at them in turn, which
looks less mechanical and helps when one spot goes quiet. One spot is enough to
work, it just always casts at the same place.

Spots are saved permanently, so you only do this once per fishing location.

### 2. Check the screen — tab **Settings**, then tab **Start**

In **Settings**, pick the monitor Albion runs on.

Then look at the **Start** tab. It shows a line like:

```
Screen    1920x1080 (UI-Scale 1.00x)
```

That must match the resolution Albion is actually running at. If it does not,
the bot will look in the wrong places.

### 3. Start fishing — tab **Start**

Press **Start**, or **F3** from inside the game. Press **F3** again to stop.

The **Status** line tells you what is happening: `Casting`, `Fishing`, `Bite!`.

### 4. If it casts but never catches — calibrate

If you see `Bite!` in the status but no fish are counted, the bot cannot find
the bobber, which means it is looking in the wrong place for the bar.

**Start fishing, and the moment the reel-in bar appears, press F4.** The screen
freezes on that instant. Now drag a box tightly around the bar — take your time,
nothing is running. A red dashed rectangle shows where the bot was looking, so
you can see how far off it was.

Press **Start** again afterwards.

### Hotkeys

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
