"""The reel-in minigame: keep the bobber inside the bar."""

import time

import cv2
import mss
import numpy as np
from pynput.mouse import Button as MouseButton

from config import resource_path

BOBBER_TEMPLATE = "bobber_2.png"
MATCH_THRESHOLD = 0.8
# Safety net: if the bobber is somehow tracked forever, give up instead of
# holding the mouse button down for the rest of the session.
MAX_DURATION_SEC = 30


class MiniGame:
    def __init__(self, mouse, screen, debug=False, region=None):
        self.mouse = mouse
        self.screen = screen
        self.debug = debug
        self.region = region
        self.template = cv2.imread(resource_path(BOBBER_TEMPLATE))
        if self.template is None:
            raise FileNotFoundError(f"Template image not found: {BOBBER_TEMPLATE}")

    def _region(self):
        return self.region or self.screen.minigame_region()

    def play(self, stop_event=None):
        """Hold/release the mouse to keep the bobber centred until it vanishes.

        Returns True if the bobber was seen at least once.
        """
        region = self._region()
        # Both the search band and the template size follow the screen
        # resolution, so this works on 1080p, 1440p, 4K and ultrawide alike.
        resized = []
        for scale in self.screen.template_scales():
            template = cv2.resize(
                self.template, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR
            )
            if template.shape[0] >= 4 and template.shape[1] >= 4:
                resized.append(template)

        center_x = region["width"] // 2
        started = time.monotonic()
        seen = False

        try:
            with mss.mss() as sct:
                while True:
                    if stop_event is not None and stop_event.is_set():
                        break
                    if time.monotonic() - started > MAX_DURATION_SEC:
                        print("[minigame] Timeout - aborting.")
                        break

                    frame = np.array(sct.grab(region))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                    found_at = None
                    for template in resized:
                        if (
                            template.shape[0] > frame.shape[0]
                            or template.shape[1] > frame.shape[1]
                        ):
                            continue
                        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
                        _, max_val, _, max_loc = cv2.minMaxLoc(result)
                        if max_val >= MATCH_THRESHOLD:
                            found_at = (max_loc, template.shape)
                            break

                    if found_at is None:
                        # Bobber gone -> the minigame is over.
                        self.mouse.release(MouseButton.left)
                        break

                    seen = True
                    (left, top), (height, width, _) = found_at
                    if left + width // 2 < center_x:
                        self.mouse.press(MouseButton.left)
                    else:
                        self.mouse.release(MouseButton.left)

                    if self.debug:
                        cv2.rectangle(
                            frame,
                            (left, top),
                            (left + width, top + height),
                            (0, 255, 0),
                            2,
                        )
                        cv2.imshow("Minigame", frame)
                        cv2.waitKey(1)
        finally:
            self.mouse.release(MouseButton.left)
            if self.debug:
                try:
                    cv2.destroyWindow("Minigame")
                except cv2.error:
                    pass

        return seen
