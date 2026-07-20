"""Things the bot does to the game: casting the rod, eating, re-baiting."""

import os
import time

import cv2
import mss
import numpy as np
from pynput.mouse import Button as MouseButton

from config import resource_path

BAIT_BUTTON_TEMPLATE = os.path.join("InventoryImgs", "UseHookBTn.png")
ICON_MATCH_THRESHOLD = 0.7
BUTTON_MATCH_THRESHOLD = 0.5


class Rod:
    """Casting the fishing rod."""

    def __init__(self, mouse):
        self.mouse = mouse

    def cast(self):
        print("[rod] Casting")
        time.sleep(0.5)
        self.mouse.press(MouseButton.left)
        time.sleep(2)
        self.mouse.release(MouseButton.left)
        time.sleep(1)


class Items:
    """Consumables: food and bait.

    Bait is located by template matching, so it follows the screen resolution
    automatically.  Food used to rely on two hardcoded 1080p inventory
    coordinates; those are now optional and recorded by the user, and the bot
    works without them by just pressing the food hotkey.
    """

    def __init__(self, keyboard, mouse, screen, settings, debug=False):
        self.keyboard = keyboard
        self.mouse = mouse
        self.screen = screen
        self.settings = settings
        self.debug = debug

    # -- helpers ---------------------------------------------------------

    def _grab_screen_gray(self):
        with mss.mss() as sct:
            shot = sct.grab(self.screen.full_region())
        return cv2.cvtColor(np.array(shot), cv2.COLOR_BGRA2GRAY)

    def _find(self, haystack, template, threshold):
        """Return the absolute centre of ``template`` in ``haystack``, or None.

        Coordinates are offset by the monitor origin, so this also works on a
        second monitor whose virtual-desktop coordinates do not start at 0.
        """
        best = None
        for scale in self.screen.template_scales():
            scaled = cv2.resize(
                template, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR
            )
            if scaled.shape[0] > haystack.shape[0] or scaled.shape[1] > haystack.shape[1]:
                continue
            result = cv2.matchTemplate(haystack, scaled, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            if max_val >= threshold and (best is None or max_val > best[0]):
                best = (max_val, max_loc, scaled.shape)
        if best is None:
            return None
        _, (left, top), (height, width) = best
        return (
            self.screen.left + left + width // 2,
            self.screen.top + top + height // 2,
        )

    def _click(self, position):
        self.mouse.position = position
        time.sleep(0.1)
        self.mouse.click(MouseButton.left, 1)

    # -- actions ---------------------------------------------------------

    def use_food(self):
        """Eat.  Optionally refill the food slot first by dragging from the bag."""
        hotkey = str(self.settings.get("food_hotkey", "2"))[:1] or "2"
        drag_from = self.settings.get("food_drag_from")
        drag_to = self.settings.get("food_drag_to")

        print("[items] Using food")
        self.keyboard.press(hotkey)
        self.keyboard.release(hotkey)
        time.sleep(1.5)

        if drag_from and drag_to:
            self.mouse.position = tuple(drag_from)
            self.mouse.press(MouseButton.left)
            time.sleep(0.5)
            self.mouse.position = tuple(drag_to)
            time.sleep(0.2)
            self.mouse.release(MouseButton.left)
            time.sleep(1.5)

    def use_bait(self):
        """Open the bait in the inventory and click its Use button."""
        bait_name = self.settings.get("bait_template", "TirIII.png")
        icon = cv2.imread(
            resource_path(os.path.join("InventoryImgs", bait_name)), cv2.IMREAD_GRAYSCALE
        )
        button = cv2.imread(
            resource_path(BAIT_BUTTON_TEMPLATE), cv2.IMREAD_GRAYSCALE
        )
        if icon is None or button is None:
            print(f"[items] Bait templates missing ({bait_name}) - skipping.")
            return False

        world = self._grab_screen_gray()
        icon_pos = self._find(world, icon, ICON_MATCH_THRESHOLD)
        if icon_pos is None:
            print("[items] No bait found in the inventory.")
            return False

        print(f"[items] Bait at {icon_pos}")
        self._click(icon_pos)
        time.sleep(0.5)

        world = self._grab_screen_gray()
        button_pos = self._find(world, button, BUTTON_MATCH_THRESHOLD)
        if button_pos is None:
            print("[items] Use button not found.")
            return False

        self._click(button_pos)
        time.sleep(0.5)
        # Click the icon again to close the context menu.
        self._click(icon_pos)
        time.sleep(0.5)
        return True
