"""Diagnose why the minigame is not detected.

Run this, then start fishing in Albion. While the reel-in bar is on screen the
tool records what the bot would see and how well the bobber template matches.

    .venv\\Scripts\\python.exe diagnose.py

It writes into a "diagnose" folder next to this file:
    fullscreen.png       - the whole screen, for locating the bar by hand
    region_best.png      - the search region at its best match
    region_last.png      - the search region at the end
and prints the best match score per scale factor.
"""

import os
import time

import cv2
import mss
import numpy as np

import config
from minigame import BOBBER_TEMPLATE, MATCH_THRESHOLD
from screen import Screen, enable_dpi_awareness, resolve_minigame_region

enable_dpi_awareness()

DURATION_SEC = 25
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "diagnose")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    settings = config.load()
    screen = Screen(settings.get("monitor", 1), settings.get("ui_scale"))

    region, source = resolve_minigame_region(settings, screen)

    template = cv2.imread(config.resource_path(BOBBER_TEMPLATE))
    if template is None:
        print(f"!! {BOBBER_TEMPLATE} not found")
        return

    print(f"Screen        : {screen}")
    print(f"Search region : {region}   ({source})")
    print(f"Template      : {template.shape[1]}x{template.shape[0]} px")
    print(f"Threshold     : {MATCH_THRESHOLD}")
    print()

    with mss.mss() as sct:
        cv2.imwrite(
            os.path.join(OUT_DIR, "fullscreen.png"),
            cv2.cvtColor(np.array(sct.grab(screen.full_region())), cv2.COLOR_BGRA2BGR),
        )
    print(f"Saved fullscreen.png")
    print(f"\nStart fishing now - recording for {DURATION_SEC} seconds...\n")

    # Two strategies, so we can see which one actually finds the bobber:
    #   A) scale the template up to the screen (what the bot does today)
    #   B) scale the captured frame down to 1080p and match the crisp template
    scales = screen.template_scales()
    best = {"a": 0.0, "b": 0.0}
    best_frame = None
    frames = 0
    started = time.monotonic()

    with mss.mss() as sct:
        while time.monotonic() - started < DURATION_SEC:
            frame = cv2.cvtColor(np.array(sct.grab(region)), cv2.COLOR_BGRA2BGR)
            frames += 1

            # A: upscaled template
            for scale in scales:
                scaled = cv2.resize(
                    template, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR
                )
                if scaled.shape[0] > frame.shape[0] or scaled.shape[1] > frame.shape[1]:
                    continue
                _, value, _, _ = cv2.minMaxLoc(
                    cv2.matchTemplate(frame, scaled, cv2.TM_CCOEFF_NORMED)
                )
                if value > best["a"]:
                    best["a"] = value

            # B: normalise the frame to 1080p scale instead
            inverse = 1.0 / screen.ui_scale
            interpolation = cv2.INTER_AREA if inverse < 1 else cv2.INTER_LINEAR
            normalised = cv2.resize(
                frame, None, fx=inverse, fy=inverse, interpolation=interpolation
            )
            if (
                normalised.shape[0] >= template.shape[0]
                and normalised.shape[1] >= template.shape[1]
            ):
                _, value, _, location = cv2.minMaxLoc(
                    cv2.matchTemplate(normalised, template, cv2.TM_CCOEFF_NORMED)
                )
                if value > best["b"]:
                    best["b"] = value
                    marked = frame.copy()
                    x = int(location[0] * screen.ui_scale)
                    y = int(location[1] * screen.ui_scale)
                    w = int(template.shape[1] * screen.ui_scale)
                    h = int(template.shape[0] * screen.ui_scale)
                    cv2.rectangle(marked, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    best_frame = marked

            time.sleep(0.05)

        cv2.imwrite(os.path.join(OUT_DIR, "region_last.png"), frame)
        if best_frame is not None:
            cv2.imwrite(os.path.join(OUT_DIR, "region_best.png"), best_frame)

    print(f"Frames analysed          : {frames}")
    print(f"Best match, template up  : {best['a']:.3f}  (A - current behaviour)")
    print(f"Best match, frame down   : {best['b']:.3f}  (B - proposed fix)")
    print()
    if max(best.values()) < 0.5:
        print(">> Neither works. The bar is probably NOT inside the search region.")
        print("   Open diagnose/fullscreen.png and check where the bar actually is.")
    elif best["b"] > best["a"]:
        print(">> Strategy B is better - the template upscaling was the problem.")
    else:
        print(">> Strategy A is fine - the region is the more likely problem.")
    print(f"\nImages are in: {OUT_DIR}")


if __name__ == "__main__":
    main()
