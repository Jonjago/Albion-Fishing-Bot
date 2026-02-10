import cv2
import numpy as np
import mss
import pyautogui
import time
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button as MouseButton
from pynput.keyboard import Key, Controller
from MiniGame import *
from Fishing import *
from UseItems import *
from ThreadTimers import *
from FishingLocation import *


class FastMotionDetection:
    def __init__(self):
        self.is_detecting = True
        self.prev_time = None  # Zeitstempel des vorherigen Frames
        self.mouseController = MouseController()
        self.keyboardController = Controller()
        self.miniGame = MiniGame(self.mouseController)
        self.Fishing = Fishing(self.mouseController)

    def get_screenshot_region(self, mouse_x, mouse_y, width, height):
        """
        Dynamische Region basierend auf der Mausposition.
        """
        left = max(mouse_x - width // 2, 0)
        top = max(mouse_y - height // 2, 0)
        return {"top": top, "left": left, "width": width, "height": height}




    def start_detection(self):
        """
        Startet die Bewegungserkennung für schnelle Bewegungen.
        """

        time.sleep(5)
        with mss.mss() as sct:
            prev_frame = None  # Vorheriger Frame für Bewegungsdifferenz
            self.prev_time = time.time()  # Initialer Zeitstempel

            while self.is_detecting:
                # Hole die aktuelle Mausposition
                mouse_x, mouse_y = pyautogui.position()

                # Dynamische Region basierend auf der Mausposition
                region = self.get_screenshot_region(mouse_x, mouse_y, 90, 90)
                screenshot = sct.grab(region)

                # Konvertiere Screenshot in ein OpenCV-kompatibles Format
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2GRAY)  # In Graustufen umwandeln

                # Bewegungsdifferenz berechnen
                if prev_frame is not None:
                    diff = cv2.absdiff(prev_frame, frame)
                    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
                    motion = cv2.countNonZero(thresh)

                    # Geschwindigkeit der Bewegung berechnen
                    current_time = time.time()
                    time_diff = current_time - self.prev_time  # Zeitdifferenz zwischen Frames
                    self.prev_time = current_time

                    # Normierte Bewegungsgeschwindigkeit
                    speed = motion / (region["width"] * region["height"]) / time_diff

                    # Bewegung anzeigen, wenn sie schnell ist
                    if speed > 0.8:  # Schwellenwert für schnelle Bewegung
                        print("Schnelle Bewegung erkannt!")
                        self.mouseController.click(MouseButton.left, 1)
                        time.sleep(0.4)
                        self.miniGame.PlayGame()
                        self.mouseController.position = (399,357)
                        time.sleep(3)
                        self.mouseController.position = (468,977)
                        self.Fishing.StartFishing()
                        time.sleep(2)

                    # Zeige die Bewegungserkennung im Fenster
                    cv2.imshow("Bewegungserkennung", thresh)

                # Aktuellen Frame speichern
                prev_frame = frame

                # Beenden mit der Taste 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.is_detecting = False
                    break

        cv2.destroyAllWindows()

# Hauptprogramm
if __name__ == "__main__":
    detector = FastMotionDetection()
    detector.start_detection()