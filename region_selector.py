"""Freeze the screen, then draw a rectangle on the still image.

The fishing minigame only lasts a few seconds -- far too short to alt-tab to
the app, press a button and carefully drag a box around a bar that is only ~23
pixels tall.  So calibration works the other way round: a hotkey grabs a
screenshot the moment the bar is visible, and the user draws on that frozen
image afterwards, with no time pressure at all.
"""

import os
import tempfile
import tkinter as tk

import cv2
import mss
import numpy as np

DEFAULT_HINT = (
    "Drag a box tightly around the fishing bar, then let go.    "
    "Right-click or Esc to cancel."
)


def grab_screenshot(screen):
    """Capture the monitor and return the path to a PNG.

    PNG specifically: tkinter's own PhotoImage can display it without Pillow,
    which keeps the dependency list short.
    """
    with mss.mss() as sct:
        frame = np.array(sct.grab(screen.full_region()))
    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    path = os.path.join(tempfile.gettempdir(), "albion_calibration.png")
    cv2.imwrite(path, frame)
    return path


def select_region(parent, screen, background=None, reference=None, hint=DEFAULT_HINT):
    """Show a fullscreen overlay and return ``(left, top, width, height)``.

    ``background``  path to a PNG to draw on instead of the live screen.
    ``reference``   an optional region drawn as a dashed outline, so the user
                    can see where the bot is currently looking versus where the
                    bar actually is.

    Returns None if the user cancels or drags nothing.
    """
    overlay = tk.Toplevel(parent)
    overlay.overrideredirect(True)
    overlay.geometry(f"{screen.width}x{screen.height}+{screen.left}+{screen.top}")
    overlay.attributes("-topmost", True)
    # A frozen screenshot must be fully opaque, otherwise the bar is washed out
    # and hard to trace.  The live variant stays dimmed so the user can tell the
    # two modes apart at a glance.
    overlay.attributes("-alpha", 1.0 if background else 0.35)
    overlay.configure(bg="black")
    overlay.grab_set()

    canvas = tk.Canvas(overlay, bg="black", highlightthickness=0, cursor="crosshair")
    canvas.pack(fill="both", expand=True)

    photo = None
    if background:
        try:
            photo = tk.PhotoImage(file=background, master=overlay)
            canvas.create_image(0, 0, anchor="nw", image=photo)
        except tk.TclError as error:
            print(f"[calibration] Could not show the screenshot: {error}")

    if reference:
        canvas.create_rectangle(
            reference["left"] - screen.left,
            reference["top"] - screen.top,
            reference["left"] - screen.left + reference["width"],
            reference["top"] - screen.top + reference["height"],
            outline="#ff5252",
            width=2,
            dash=(6, 4),
        )
        canvas.create_text(
            reference["left"] - screen.left + reference["width"] // 2,
            reference["top"] - screen.top - 12,
            text="where the bot looks now",
            fill="#ff5252",
            font=("Segoe UI", 10, "bold"),
        )

    # Banner with a readable backdrop -- plain white text vanishes on a bright
    # screenshot.
    canvas.create_rectangle(0, 0, screen.width, 74, fill="#101418", outline="")
    canvas.create_text(
        screen.width // 2, 26, text=hint, fill="white", font=("Segoe UI", 15, "bold")
    )
    size_label = canvas.create_text(
        screen.width // 2, 54, text="", fill="#4fc3f7", font=("Segoe UI", 11)
    )

    expected = screen.expected_minigame_width()
    state = {"x": 0, "y": 0, "rect": None, "result": None}

    def on_press(event):
        state["x"], state["y"] = event.x, event.y
        if state["rect"] is not None:
            canvas.delete(state["rect"])
        state["rect"] = canvas.create_rectangle(
            event.x, event.y, event.x, event.y, outline="#4fc3f7", width=2
        )

    def on_drag(event):
        if state["rect"] is None:
            return
        canvas.coords(state["rect"], state["x"], state["y"], event.x, event.y)
        width = abs(event.x - state["x"])
        height = abs(event.y - state["y"])
        canvas.itemconfigure(
            size_label,
            text=f"{width} x {height} px      (the bar is normally about {expected} px wide)",
        )

    def on_release(event):
        left = min(state["x"], event.x)
        top = min(state["y"], event.y)
        width = abs(event.x - state["x"])
        height = abs(event.y - state["y"])
        if width >= 5 and height >= 5:
            state["result"] = (screen.left + left, screen.top + top, width, height)
        close()

    def close(_event=None):
        overlay.grab_release()
        overlay.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    canvas.bind("<ButtonPress-3>", close)
    overlay.bind("<Escape>", close)
    overlay.focus_force()
    parent.wait_window(overlay)

    # keep a reference until the window is gone, or Tk garbage-collects the image
    del photo
    return state["result"]
