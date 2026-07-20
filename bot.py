"""The fishing loop.

Detects a bite by looking for a burst of motion around the bobber, plays the
minigame, then recasts at the next recorded spot.

Compared to the old FastMotionDetection this version:

* derives every pixel value from the actual screen resolution (screen.py),
* uses monotonic timestamps instead of three never-ending counter threads,
* stops cleanly instead of leaving daemon threads and OpenCV windows behind,
* reports status back to the GUI instead of only printing.
"""

import threading
import time

import cv2
import mss
import numpy as np
import pyautogui
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Button as MouseButton
from pynput.mouse import Controller as MouseController

from actions import Items, Rod
from minigame import MiniGame
from positions import PositionCycler
from screen import Screen, resolve_minigame_region

# Capture box around the bobber, in 1080p reference pixels.
DETECTION_BOX = 125
# Per-pixel brightness change that counts as movement.
PIXEL_DELTA = 25

# The bot's own mouse movement would otherwise trigger pyautogui's corner
# failsafe mid-session; F3 is the stop hotkey instead.
pyautogui.FAILSAFE = False


class FishingBot:
    def __init__(self, settings, on_status=None, on_fish=None):
        self.settings = settings
        self.on_status = on_status or (lambda message: None)
        self.on_fish = on_fish or (lambda count: None)

        self.stop_event = threading.Event()
        self.caught_total = 0

    def stop(self):
        self.stop_event.set()

    def _status(self, message):
        print(f"[bot] {message}")
        self.on_status(message)

    def run(self):
        try:
            self._run()
        except Exception as error:  # keep a crash from killing the GUI silently
            self._status(f"Error: {error}")
            raise
        finally:
            try:
                cv2.destroyAllWindows()
            except cv2.error:
                pass

    def _run(self):
        settings = self.settings
        debug = bool(settings.get("debug_windows"))

        screen = Screen(settings.get("monitor", 1), settings.get("ui_scale"))
        self._status(f"Screen: {screen.description}")

        mouse = MouseController()
        keyboard = KeyboardController()

        minigame_region, region_source = resolve_minigame_region(settings, screen)
        self._status(f"Fishing bar: {region_source}")

        rod = Rod(mouse)
        minigame = MiniGame(mouse, screen, debug=debug, region=minigame_region)
        items = Items(keyboard, mouse, screen, settings, debug=debug)
        spots = PositionCycler(mouse, settings.get("positions", []))

        if len(spots) == 0:
            self._status("No fishing spots recorded - add at least one.")
            return

        sensitivity = float(settings.get("sensitivity", 0.6))
        recast_after = float(settings.get("recast_after_sec", 40))
        food_interval = float(settings.get("food_interval_min", 30)) * 60
        bait_every = int(settings.get("bait_every_n_fish", 10))

        if settings.get("use_food"):
            items.use_food()
        if settings.get("use_bait"):
            items.use_bait()

        spots.next()
        rod.cast()

        last_bite = time.monotonic()
        last_food = time.monotonic()
        caught_since_bait = 0
        previous_frame = None
        previous_time = time.monotonic()

        self._status("Fishing")

        with mss.mss() as sct:
            while not self.stop_event.is_set():
                mouse_x, mouse_y = pyautogui.position()
                region = screen.region_around(mouse_x, mouse_y, DETECTION_BOX)
                frame = cv2.cvtColor(np.array(sct.grab(region)), cv2.COLOR_BGRA2GRAY)

                now = time.monotonic()
                elapsed = max(now - previous_time, 1e-3)
                previous_time = now

                bite = False
                if previous_frame is not None and previous_frame.shape == frame.shape:
                    difference = cv2.absdiff(previous_frame, frame)
                    _, mask = cv2.threshold(
                        difference, PIXEL_DELTA, 255, cv2.THRESH_BINARY
                    )
                    changed = cv2.countNonZero(mask)
                    # Normalised by area, so the value means the same thing on
                    # every resolution.
                    speed = changed / (region["width"] * region["height"]) / elapsed
                    bite = speed > sensitivity

                    if debug:
                        cv2.imshow("Motion", mask)
                        cv2.waitKey(1)

                previous_frame = frame

                if bite:
                    self._status("Bite!")
                    mouse.click(MouseButton.left, 1)
                    time.sleep(0.4)
                    minigame.play(self.stop_event)
                    mouse.release(MouseButton.left)
                    time.sleep(2)

                    self.caught_total += 1
                    caught_since_bait += 1
                    self.on_fish(self.caught_total)
                    last_bite = time.monotonic()

                    if settings.get("use_bait") and caught_since_bait >= bait_every:
                        items.use_bait()
                        caught_since_bait = 0

                    if (
                        settings.get("use_food")
                        and time.monotonic() - last_food >= food_interval
                    ):
                        items.use_food()
                        last_food = time.monotonic()

                    if self.stop_event.is_set():
                        break
                    spots.next()
                    rod.cast()
                    previous_frame = None

                elif time.monotonic() - last_bite >= recast_after:
                    self._status(f"No bite for {recast_after:.0f}s - recasting")
                    mouse.release(MouseButton.left)
                    spots.next()
                    rod.cast()
                    last_bite = time.monotonic()
                    previous_frame = None

                time.sleep(0.01)

        mouse.release(MouseButton.left)
        self._status("Stopped")
