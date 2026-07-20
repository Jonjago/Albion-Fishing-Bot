"""Albion Fishing Bot - user interface.

Run this file to start the bot.

Design notes (the old Dashboard.py had all of these problems):
* the window is a normal window, so it has a title bar and can be closed;
* settings and fishing spots are saved and restored between sessions;
* status messages come back from the worker thread through a queue, so nothing
  touches tkinter from a background thread;
* the resolution is shown right on the first tab, so a wrong monitor or a wrong
  UI scale is visible instead of silently producing a bot that never bites.
"""

import queue
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

import config
from screen import (
    Screen,
    enable_dpi_awareness,
    list_monitors,
    resolve_minigame_region,
)

# Must happen before tkinter or any screen capture is set up.
enable_dpi_awareness()

from bot import FishingBot  # noqa: E402  (import after DPI setup on purpose)
from region_selector import grab_screenshot, select_region  # noqa: E402

try:
    import keyboard as global_hotkeys
except Exception:  # pragma: no cover - optional dependency
    global_hotkeys = None

WELCOME = """Welcome!

Three steps to get fishing:

1.  Tab "Spots": stand at the water, point your mouse where you want to
    cast, and press F2. Repeat for up to a handful of spots.

2.  Tab "Settings": check that the monitor and resolution shown are the
    ones the game runs on.

3.  Tab "Start": press Start (or F3). Press F3 again to stop.

If the bot casts but never reels a fish in, the fishing bar is not
where it looks. Fix it like this:

    Start fishing, and the moment the reel-in bar appears, press F4.
    The screen freezes on that instant, and you can draw a box around
    the bar in your own time. The red dashed rectangle shows where the
    bot is looking right now."""


class Dashboard(ttk.Frame):
    def __init__(self, root):
        super().__init__(root, padding=10)
        self.root = root
        self.settings = config.load()
        self.messages = queue.Queue()

        self.bot = None
        self.bot_thread = None
        self.running = False
        self.started_at = None

        self._build()
        self._register_hotkeys()
        self._poll_messages()
        self._tick_runtime()

        if self.settings.get("first_run"):
            self.settings["first_run"] = False
            config.save(self.settings)
            self.after(300, lambda: messagebox.showinfo("Getting started", WELCOME))

    # ------------------------------------------------------------------ UI

    def _build(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        self._build_start_tab()
        self._build_spots_tab()
        self._build_extras_tab()
        self._build_settings_tab()
        self._build_help_tab()

    def _build_start_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Start")

        self.status_var = tk.StringVar(value="Idle")
        self.screen_var = tk.StringVar(value="")
        self.fish_var = tk.StringVar(value="0")
        self.runtime_var = tk.StringVar(value="00:00:00")

        ttk.Label(tab, text="Status", font=("-weight", "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(tab, textvariable=self.status_var).grid(row=0, column=1, sticky="w")

        ttk.Label(tab, text="Screen", font=("-weight", "bold")).grid(
            row=1, column=0, sticky="w", pady=(6, 0)
        )
        ttk.Label(tab, textvariable=self.screen_var).grid(
            row=1, column=1, sticky="w", pady=(6, 0)
        )

        ttk.Label(tab, text="Fish caught", font=("-weight", "bold")).grid(
            row=2, column=0, sticky="w", pady=(6, 0)
        )
        ttk.Label(tab, textvariable=self.fish_var).grid(
            row=2, column=1, sticky="w", pady=(6, 0)
        )

        ttk.Label(tab, text="Runtime", font=("-weight", "bold")).grid(
            row=3, column=0, sticky="w", pady=(6, 0)
        )
        ttk.Label(tab, textvariable=self.runtime_var).grid(
            row=3, column=1, sticky="w", pady=(6, 0)
        )

        toggle_key = self.settings.get("hotkey_toggle", "f3").upper()
        self.start_button = ttk.Button(
            tab, text=f"Start  [{toggle_key}]", command=self.toggle
        )
        self.start_button.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(14, 0))

        tab.columnconfigure(1, weight=1)
        self._refresh_screen_label()

    def _build_spots_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Spots")

        record_key = self.settings.get("hotkey_record", "f2").upper()
        ttk.Label(
            tab,
            text=f"Point the mouse at the water, then press {record_key}.",
            wraplength=300,
        ).grid(row=0, column=0, columnspan=2, sticky="w")

        self.spot_list = tk.Listbox(tab, height=6)
        self.spot_list.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=8)

        ttk.Button(tab, text=f"Record ({record_key})", command=self.record_spot).grid(
            row=2, column=0, sticky="ew", padx=(0, 4)
        )
        ttk.Button(tab, text="Delete selected", command=self.delete_spot).grid(
            row=2, column=1, sticky="ew", padx=(4, 0)
        )
        ttk.Button(tab, text="Clear all", command=self.clear_spots).grid(
            row=3, column=0, columnspan=2, sticky="ew", pady=(6, 0)
        )

        tab.columnconfigure(0, weight=1)
        tab.columnconfigure(1, weight=1)
        tab.rowconfigure(1, weight=1)
        self._refresh_spots()

    def _build_extras_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Extras")

        self.use_food_var = tk.BooleanVar(value=self.settings.get("use_food", False))
        self.food_hotkey_var = tk.StringVar(value=self.settings.get("food_hotkey", "2"))
        self.food_interval_var = tk.IntVar(
            value=int(self.settings.get("food_interval_min", 30))
        )
        self.use_bait_var = tk.BooleanVar(value=self.settings.get("use_bait", False))
        self.bait_template_var = tk.StringVar(
            value=self.settings.get("bait_template", "TirIII.png")
        )
        self.bait_every_var = tk.IntVar(
            value=int(self.settings.get("bait_every_n_fish", 10))
        )

        ttk.Checkbutton(tab, text="Use food", variable=self.use_food_var).grid(
            row=0, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(tab, text="Food hotbar key").grid(row=1, column=0, sticky="w")
        ttk.Entry(tab, textvariable=self.food_hotkey_var, width=6).grid(
            row=1, column=1, sticky="w"
        )
        ttk.Label(tab, text="Eat every (minutes)").grid(row=2, column=0, sticky="w")
        ttk.Spinbox(
            tab, from_=1, to=180, textvariable=self.food_interval_var, width=6
        ).grid(row=2, column=1, sticky="w")

        ttk.Separator(tab).grid(row=3, column=0, columnspan=2, sticky="ew", pady=8)

        ttk.Checkbutton(tab, text="Use bait", variable=self.use_bait_var).grid(
            row=4, column=0, columnspan=2, sticky="w"
        )
        ttk.Label(tab, text="Bait item").grid(row=5, column=0, sticky="w")
        ttk.Combobox(
            tab,
            textvariable=self.bait_template_var,
            values=["TirIII.png", "TirV.png", "SeeGrass.png"],
            state="readonly",
            width=14,
        ).grid(row=5, column=1, sticky="w")
        ttk.Label(tab, text="Re-bait every N fish").grid(row=6, column=0, sticky="w")
        ttk.Spinbox(
            tab, from_=1, to=99, textvariable=self.bait_every_var, width=6
        ).grid(row=6, column=1, sticky="w")

        ttk.Button(tab, text="Save", command=self.save_settings).grid(
            row=7, column=0, columnspan=2, sticky="ew", pady=(12, 0)
        )
        tab.columnconfigure(0, weight=1)

    def _build_settings_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Settings")

        monitors = list_monitors()
        self.monitor_var = tk.StringVar()
        current = self.settings.get("monitor", 1)
        labels = [label for _, label in monitors]
        self.monitor_var.set(
            labels[current - 1] if 0 < current <= len(labels) else (labels[0] if labels else "")
        )

        ttk.Label(tab, text="Game monitor").grid(row=0, column=0, sticky="w")
        monitor_box = ttk.Combobox(
            tab, textvariable=self.monitor_var, values=labels, state="readonly", width=24
        )
        monitor_box.grid(row=0, column=1, sticky="w")
        monitor_box.bind("<<ComboboxSelected>>", lambda _e: self._on_monitor_change())

        self.sensitivity_var = tk.DoubleVar(
            value=float(self.settings.get("sensitivity", 0.6))
        )
        ttk.Label(tab, text="Bite sensitivity").grid(
            row=1, column=0, sticky="w", pady=(8, 0)
        )
        sensitivity_row = ttk.Frame(tab)
        sensitivity_row.grid(row=1, column=1, sticky="ew", pady=(8, 0))
        self.sensitivity_label = ttk.Label(sensitivity_row, width=5)
        ttk.Scale(
            sensitivity_row,
            from_=0.1,
            to=2.0,
            variable=self.sensitivity_var,
            command=lambda _v: self.sensitivity_label.configure(
                text=f"{self.sensitivity_var.get():.2f}"
            ),
        ).pack(side="left", fill="x", expand=True)
        self.sensitivity_label.pack(side="left")
        self.sensitivity_label.configure(text=f"{self.sensitivity_var.get():.2f}")

        self.recast_var = tk.IntVar(value=int(self.settings.get("recast_after_sec", 40)))
        ttk.Label(tab, text="Recast after (seconds)").grid(
            row=2, column=0, sticky="w", pady=(8, 0)
        )
        ttk.Spinbox(tab, from_=10, to=180, textvariable=self.recast_var, width=6).grid(
            row=2, column=1, sticky="w", pady=(8, 0)
        )

        ttk.Separator(tab).grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        self.region_var = tk.StringVar()
        ttk.Label(tab, text="Fishing bar").grid(row=4, column=0, sticky="w")
        ttk.Label(tab, textvariable=self.region_var, wraplength=180).grid(
            row=4, column=1, sticky="w"
        )
        freeze_key = self.settings.get("hotkey_freeze", "f4").upper()
        ttk.Button(
            tab, text=f"Calibrate bar ({freeze_key})", command=self.calibrate
        ).grid(
            row=5, column=0, sticky="ew", pady=(6, 0), padx=(0, 4)
        )
        ttk.Button(tab, text="Reset to automatic", command=self.reset_region).grid(
            row=5, column=1, sticky="ew", pady=(6, 0), padx=(4, 0)
        )

        ttk.Separator(tab).grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)

        self.debug_var = tk.BooleanVar(value=self.settings.get("debug_windows", False))
        ttk.Checkbutton(
            tab, text="Show debug windows", variable=self.debug_var
        ).grid(row=7, column=0, columnspan=2, sticky="w")

        self.on_top_var = tk.BooleanVar(value=self.settings.get("always_on_top", True))
        ttk.Checkbutton(
            tab,
            text="Keep window on top",
            variable=self.on_top_var,
            command=self._apply_on_top,
        ).grid(row=8, column=0, columnspan=2, sticky="w")

        ttk.Button(tab, text="Save", command=self.save_settings).grid(
            row=9, column=0, columnspan=2, sticky="ew", pady=(12, 0)
        )
        tab.columnconfigure(1, weight=1)
        self._refresh_region_label()

    def _build_help_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text="Help")
        text = tk.Text(tab, wrap="word", height=12, width=44, relief="flat")
        text.insert("1.0", WELCOME + f"\n\nSettings file:\n{config.config_path()}")
        text.configure(state="disabled")
        text.pack(fill="both", expand=True)

    # ------------------------------------------------------------- helpers

    def _current_screen(self):
        return Screen(self.settings.get("monitor", 1), self.settings.get("ui_scale"))

    def _refresh_screen_label(self):
        try:
            self.screen_var.set(self._current_screen().description)
        except Exception as error:
            self.screen_var.set(f"unknown ({error})")

    def _refresh_region_label(self):
        try:
            screen = self._current_screen()
        except Exception:
            self.region_var.set("unknown")
            return
        region, source = resolve_minigame_region(self.settings, screen)
        self.region_var.set(f"{source}: {region['width']}x{region['height']}")

    def _refresh_spots(self):
        self.spot_list.delete(0, tk.END)
        for index, (x, y) in enumerate(self.settings.get("positions", []), start=1):
            self.spot_list.insert(tk.END, f"{index}.   x={x}   y={y}")

    def _on_monitor_change(self):
        label = self.monitor_var.get()
        for index, text in list_monitors():
            if text == label:
                self.settings["monitor"] = index
                break
        self._refresh_screen_label()
        self._refresh_region_label()
        config.save(self.settings)

    def _apply_on_top(self):
        self.root.wm_attributes("-topmost", bool(self.on_top_var.get()))

    def _register_hotkeys(self):
        if global_hotkeys is None:
            print("[hotkeys] 'keyboard' package unavailable - use the buttons instead.")
            return
        try:
            global_hotkeys.add_hotkey(
                self.settings.get("hotkey_record", "f2"),
                lambda: self.messages.put(("record", None)),
            )
            global_hotkeys.add_hotkey(
                self.settings.get("hotkey_toggle", "f3"),
                lambda: self.messages.put(("toggle", None)),
            )
            global_hotkeys.add_hotkey(
                self.settings.get("hotkey_freeze", "f4"), self._on_freeze_hotkey
            )
        except Exception as error:
            print(f"[hotkeys] Could not register global hotkeys: {error}")

    def _on_freeze_hotkey(self):
        """Grab the screen immediately, on the hotkey thread.

        Capturing here rather than after the message round-trip means the image
        is from the instant the key went down, while the bar is still up.
        """
        try:
            screenshot = grab_screenshot(self._current_screen())
        except Exception as error:
            self.messages.put(("status", f"Screenshot failed: {error}"))
            return
        self.messages.put(("freeze", screenshot))

    # ------------------------------------------------------------- actions

    def record_spot(self):
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        self.settings.setdefault("positions", []).append([x, y])
        config.save(self.settings)
        self._refresh_spots()
        self.status_var.set(f"Spot recorded at ({x}, {y})")

    def delete_spot(self):
        selection = self.spot_list.curselection()
        if not selection:
            return
        del self.settings["positions"][selection[0]]
        config.save(self.settings)
        self._refresh_spots()

    def clear_spots(self):
        self.settings["positions"] = []
        config.save(self.settings)
        self._refresh_spots()

    def calibrate(self):
        """Explain the freeze workflow; F4 does the actual capture."""
        freeze_key = self.settings.get("hotkey_freeze", "f4").upper()
        if global_hotkeys is None:
            # No global hotkeys available - fall back to a countdown so the user
            # still has a way to catch the bar.
            if messagebox.askokcancel(
                "Calibrate",
                "Global hotkeys are unavailable on this system.\n\n"
                "Press OK, switch to Albion and start fishing. The screen will "
                "freeze automatically in 8 seconds, and you can draw the box "
                "on the frozen image.",
            ):
                self.after(8000, self.freeze_and_calibrate)
            return

        messagebox.showinfo(
            "Calibrate the fishing bar",
            "The minigame is too short to draw a box while it runs, so we "
            "freeze the screen instead.\n\n"
            "1.  Switch to Albion and start fishing.\n"
            f"2.  The moment the bar appears, press {freeze_key}.\n"
            "3.  The screen freezes. Now drag a box tightly around the bar, "
            "with no time pressure.\n\n"
            "The red dashed rectangle shows where the bot is looking right now.",
        )

    def freeze_and_calibrate(self, screenshot=None):
        """Open the selector on a frozen screenshot."""
        try:
            screen = self._current_screen()
        except Exception as error:
            messagebox.showerror("Calibration", str(error))
            return

        if screenshot is None:
            screenshot = grab_screenshot(screen)

        # The bot moves the cursor and casts on its own; leaving it running
        # would yank the mouse away mid-drag.  The screenshot is already taken,
        # so stopping now costs nothing.
        was_running = self.running
        if was_running:
            self.stop_bot()

        reference, _ = resolve_minigame_region(self.settings, screen)

        selection = select_region(
            self.root, screen, background=screenshot, reference=reference
        )
        if not selection:
            return

        left, top, width, height = selection
        region = screen.clamp_region(
            {"left": left, "top": top, "width": width, "height": height}
        )

        # A box far wider than the bar breaks the left/right decision, because
        # the bot steers towards the centre of whatever it was given.
        expected = screen.expected_minigame_width()
        if region["width"] > expected * 2.5:
            if not messagebox.askyesno(
                "Box looks too wide",
                f"You drew a box {region['width']} px wide, but the fishing bar "
                f"is normally about {expected} px on this screen.\n\n"
                "The bot steers the bobber towards the middle of this box, so a "
                "box much wider than the bar will make it pull the wrong way.\n\n"
                "Keep it anyway?",
            ):
                return

        self.settings["minigame_region"] = screen.region_to_spec(region)
        config.save(self.settings)
        self._refresh_region_label()
        self.status_var.set(
            f"Fishing bar calibrated ({region['width']}x{region['height']} px)"
        )
        if was_running:
            messagebox.showinfo(
                "Calibrated",
                "Saved. The bot was stopped for the calibration - press Start "
                "again to continue fishing.",
            )

    def reset_region(self):
        self.settings["minigame_region"] = None
        config.save(self.settings)
        self._refresh_region_label()

    def save_settings(self):
        self.settings.update(
            {
                "use_food": bool(self.use_food_var.get()),
                "food_hotkey": self.food_hotkey_var.get() or "2",
                "food_interval_min": int(self.food_interval_var.get()),
                "use_bait": bool(self.use_bait_var.get()),
                "bait_template": self.bait_template_var.get(),
                "bait_every_n_fish": int(self.bait_every_var.get()),
                "sensitivity": round(float(self.sensitivity_var.get()), 3),
                "recast_after_sec": int(self.recast_var.get()),
                "debug_windows": bool(self.debug_var.get()),
                "always_on_top": bool(self.on_top_var.get()),
            }
        )
        config.save(self.settings)
        self.status_var.set("Settings saved")

    def toggle(self):
        if self.running:
            self.stop_bot()
        else:
            self.start_bot()

    def start_bot(self):
        self.save_settings()
        if not self.settings.get("positions"):
            messagebox.showwarning(
                "No spots",
                "Record at least one fishing spot first "
                f"(tab \"Spots\", hotkey {self.settings.get('hotkey_record', 'f2').upper()}).",
            )
            return

        self.bot = FishingBot(
            self.settings,
            on_status=lambda message: self.messages.put(("status", message)),
            on_fish=lambda count: self.messages.put(("fish", count)),
        )
        self.bot_thread = threading.Thread(target=self.bot.run, daemon=True)
        self.bot_thread.start()

        self.running = True
        self.started_at = time.monotonic()
        self.start_button.configure(
            text=f"Stop  [{self.settings.get('hotkey_toggle', 'f3').upper()}]"
        )

    def stop_bot(self):
        if self.bot is not None:
            self.bot.stop()
        self.running = False
        self.started_at = None
        self.start_button.configure(
            text=f"Start  [{self.settings.get('hotkey_toggle', 'f3').upper()}]"
        )
        self.status_var.set("Stopped")

    # -------------------------------------------------------------- pumps

    def _poll_messages(self):
        """Drain messages from the worker thread on the tkinter main thread."""
        try:
            while True:
                kind, payload = self.messages.get_nowait()
                if kind == "status":
                    self.status_var.set(payload)
                elif kind == "fish":
                    self.fish_var.set(str(payload))
                elif kind == "record":
                    self.record_spot()
                elif kind == "toggle":
                    self.toggle()
                elif kind == "freeze":
                    self.freeze_and_calibrate(payload)
        except queue.Empty:
            pass
        self.after(100, self._poll_messages)

    def _tick_runtime(self):
        if self.running and self.started_at is not None:
            elapsed = int(time.monotonic() - self.started_at)
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            self.runtime_var.set(f"{hours:02}:{minutes:02}:{seconds:02}")
        self.after(1000, self._tick_runtime)

    def on_close(self):
        self.stop_bot()
        config.save(self.settings)
        if global_hotkeys is not None:
            try:
                global_hotkeys.unhook_all_hotkeys()
            except Exception:
                pass
        self.root.destroy()


def main():
    root = tk.Tk()
    root.title("Albion Fishing Bot")

    try:
        root.tk.call("source", config.resource_path("azure.tcl"))
        root.tk.call("set_theme", "dark")
    except tk.TclError as error:
        print(f"[ui] Theme unavailable, using the default look: {error}")

    app = Dashboard(root)
    app.pack(fill="both", expand=True)

    root.update_idletasks()
    root.minsize(root.winfo_width(), root.winfo_height())
    x = int(root.winfo_screenwidth() / 2 - root.winfo_width() / 2)
    y = int(root.winfo_screenheight() / 2 - root.winfo_height() / 2)
    root.geometry(f"+{x}+{y}")
    root.wm_attributes("-topmost", bool(app.settings.get("always_on_top", True)))
    root.protocol("WM_DELETE_WINDOW", app.on_close)

    root.mainloop()


if __name__ == "__main__":
    main()
