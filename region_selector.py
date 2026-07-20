"""Drag a rectangle over the screen to define a region.

This is the escape hatch for anyone whose HUD does not sit where the automatic
calculation expects it: custom Albion UI scale, windowed mode, unusual aspect
ratios.  Whatever the user drags is stored verbatim in the config.
"""

import tkinter as tk


DEFAULT_HINT = (
    "Drag a box tightly around the fishing bar, then let go.   "
    "Do not include the area around it.   Esc to cancel."
)


def select_region(parent, screen, hint=DEFAULT_HINT):
    """Show a fullscreen overlay and return ``(left, top, width, height)``.

    Returns None if the user cancels or drags nothing.
    """
    overlay = tk.Toplevel(parent)
    overlay.overrideredirect(True)
    overlay.geometry(f"{screen.width}x{screen.height}+{screen.left}+{screen.top}")
    overlay.attributes("-topmost", True)
    overlay.attributes("-alpha", 0.35)
    overlay.configure(bg="black")
    overlay.grab_set()

    canvas = tk.Canvas(overlay, bg="black", highlightthickness=0, cursor="crosshair")
    canvas.pack(fill="both", expand=True)
    canvas.create_text(
        screen.width // 2,
        40,
        text=hint,
        fill="white",
        font=("Segoe UI", 16, "bold"),
    )

    state = {"x": 0, "y": 0, "rect": None, "result": None}

    def on_press(event):
        state["x"], state["y"] = event.x, event.y
        if state["rect"] is not None:
            canvas.delete(state["rect"])
        state["rect"] = canvas.create_rectangle(
            event.x, event.y, event.x, event.y, outline="#4fc3f7", width=2
        )

    def on_drag(event):
        if state["rect"] is not None:
            canvas.coords(state["rect"], state["x"], state["y"], event.x, event.y)

    def on_release(event):
        left = min(state["x"], event.x)
        top = min(state["y"], event.y)
        width = abs(event.x - state["x"])
        height = abs(event.y - state["y"])
        if width >= 5 and height >= 5:
            state["result"] = (
                screen.left + left,
                screen.top + top,
                width,
                height,
            )
        close()

    def close(_event=None):
        overlay.grab_release()
        overlay.destroy()

    canvas.bind("<ButtonPress-1>", on_press)
    canvas.bind("<B1-Motion>", on_drag)
    canvas.bind("<ButtonRelease-1>", on_release)
    overlay.bind("<Escape>", close)
    overlay.focus_force()
    parent.wait_window(overlay)

    return state["result"]
