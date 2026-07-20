"""Resolution and DPI handling.

Everything in this project used to be written against a hardcoded 1920x1080
screen.  This module is the single place that knows about pixels, so the rest
of the bot can work in *reference* coordinates (the old 1920x1080 numbers) and
have them translated to whatever the user actually runs.

Two things matter:

* ``ui_scale`` -- Albion's HUD scales with screen *height*, so a 2560x1440
  screen draws the same widgets 1.333x larger than a 1080p screen.  Sizes
  (template images, capture boxes) get multiplied by this factor.
* ``left`` / ``top`` -- with more than one monitor, mss returns coordinates in
  the virtual desktop, which can start at negative values.  Regions must be
  offset by the monitor origin, otherwise the bot grabs the wrong screen.
"""

import ctypes
import sys

import mss

REF_WIDTH = 1920
REF_HEIGHT = 1080

# Minigame bar, measured on a 1920x1080 screen: x 839..1080, y 537..560.
REF_MINIGAME_WIDTH = 241
REF_MINIGAME_HEIGHT = 23
# Vertical centre of the bar as a fraction of screen height (548.5 / 1080).
MINIGAME_CENTER_Y_FRAC = 0.5079
# The auto-detected box is padded a little so a slightly different HUD offset
# still keeps the bar inside it.
MINIGAME_PAD_X = 1.15
MINIGAME_PAD_Y = 2.5


def enable_dpi_awareness():
    """Tell Windows we speak physical pixels.

    Without this, a display set to 125% or 150% scaling reports 1536x864
    instead of 1920x1080.  Mouse coordinates and screenshots then disagree and
    the bot clicks in the wrong place -- on a 1080p screen, which is why some
    users could not get it running even with the "supported" resolution.

    Must be called before tkinter, mss or pyautogui are used.
    """
    if sys.platform != "win32":
        return
    for attempt in (
        lambda: ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4)),
        lambda: ctypes.windll.shcore.SetProcessDpiAwareness(2),
        lambda: ctypes.windll.user32.SetProcessDPIAware(),
    ):
        try:
            attempt()
            return
        except Exception:
            continue


def list_monitors():
    """Return ``[(index, description), ...]`` for every physical monitor."""
    with mss.mss() as sct:
        monitors = sct.monitors[1:]
    return [
        (i + 1, f"Monitor {i + 1}  ({m['width']}x{m['height']})")
        for i, m in enumerate(monitors)
    ]


class Screen:
    """Geometry of the monitor the game runs on."""

    def __init__(self, monitor=1, ui_scale=None):
        with mss.mss() as sct:
            available = sct.monitors[1:]
            if not available:
                raise RuntimeError("No monitor detected.")
            index = monitor - 1
            if index < 0 or index >= len(available):
                index = 0
            geometry = available[index]

        self.monitor = index + 1
        self.left = geometry["left"]
        self.top = geometry["top"]
        self.width = geometry["width"]
        self.height = geometry["height"]
        self.ui_scale = ui_scale if ui_scale else self.height / REF_HEIGHT

    def __repr__(self):
        return (
            f"<Screen monitor={self.monitor} {self.width}x{self.height} "
            f"at ({self.left},{self.top}) ui_scale={self.ui_scale:.3f}>"
        )

    @property
    def description(self):
        return f"{self.width}x{self.height} (UI-Scale {self.ui_scale:.2f}x)"

    def scale(self, reference_pixels):
        """Convert a length measured on 1080p to this screen."""
        return max(1, round(reference_pixels * self.ui_scale))

    def point_from_reference(self, x, y):
        """Convert a 1920x1080 coordinate to an absolute screen coordinate.

        Used only for legacy defaults; anything the user can record should be
        recorded instead of guessed.
        """
        return (
            self.left + round(x / REF_WIDTH * self.width),
            self.top + round(y / REF_HEIGHT * self.height),
        )

    def full_region(self):
        return {
            "left": self.left,
            "top": self.top,
            "width": self.width,
            "height": self.height,
        }

    def region_around(self, x, y, reference_size):
        """A square capture box of ``reference_size`` (1080p px) centred on x/y.

        The box is clamped to the monitor so mss never gets a negative or
        out-of-bounds rectangle.
        """
        size = self.scale(reference_size)
        left = min(max(x - size // 2, self.left), self.left + self.width - size)
        top = min(max(y - size // 2, self.top), self.top + self.height - size)
        return {"left": int(left), "top": int(top), "width": size, "height": size}

    def minigame_region(self):
        """Where the fishing minigame bar is, derived from the screen size.

        Users whose HUD sits somewhere else (custom Albion UI scale, ultrawide,
        windowed mode) can override this by calibrating in the GUI, which stores
        an explicit rectangle in the config.
        """
        width = round(REF_MINIGAME_WIDTH * self.ui_scale * MINIGAME_PAD_X)
        height = round(REF_MINIGAME_HEIGHT * self.ui_scale * MINIGAME_PAD_Y)
        center_x = self.left + self.width // 2
        center_y = self.top + round(self.height * MINIGAME_CENTER_Y_FRAC)
        return {
            "left": center_x - width // 2,
            "top": center_y - height // 2,
            "width": width,
            "height": height,
        }

    def template_scales(self, steps=7, tolerance=0.15):
        """Scale factors to try when matching a 1080p template image.

        The old code swept 0.5x..1.5x in 20 steps on every frame, which was both
        slow and prone to matching the wrong thing.  We know the expected scale
        from the resolution, so we only search a narrow band around it.
        """
        low = self.ui_scale * (1.0 - tolerance)
        high = self.ui_scale * (1.0 + tolerance)
        if steps < 2:
            return [self.ui_scale]
        step = (high - low) / (steps - 1)
        return [low + step * i for i in range(steps)]
