"""Cycling through the fishing spots the user recorded."""

import time


class PositionCycler:
    """Moves the mouse to the next recorded spot, round-robin.

    The old FishingPosController assumed exactly four slots, indexed them by a
    counter that could run past the end of the list, and classified spots into a
    3x3 grid whose cell size was hardcoded to 640x360 (i.e. 1080p thirds).  None
    of that was actually used for anything, so it is gone.
    """

    def __init__(self, mouse, positions):
        self.mouse = mouse
        self.positions = [tuple(p) for p in positions if p]
        self.index = -1

    def __len__(self):
        return len(self.positions)

    @property
    def current(self):
        if not self.positions:
            return None
        return self.positions[self.index % len(self.positions)]

    def next(self):
        """Move to the next spot and return it, or None if none are recorded."""
        if not self.positions:
            return None
        self.index = (self.index + 1) % len(self.positions)
        target = self.positions[self.index]
        print(f"[positions] Spot {self.index + 1}/{len(self.positions)} at {target}")
        self.mouse.position = target
        time.sleep(0.3)
        return target
