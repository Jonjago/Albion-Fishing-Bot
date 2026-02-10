import cv2 
import mss
import numpy as np
import time
import pyautogui

from pynput.mouse import Controller as MouseController
from pynput.mouse import Button as MouseButton
from pynput.keyboard import Key, Controller

from Fishing import *
from GetFilePath import * 

class MiniGame:

    def __init__(self, mouseController):
        self.mouseController = mouseController
        self.getFilePath = GetFilePath

    mouseController = MouseController()

    def PlayGame(self):
        with mss.mss() as sct:
            region = (839, 537, 1080, 560)
            region_width = region[2] - region[0]
            region_height = region[3] - region[1]

            template = cv2.imread(self.getFilePath.resource_path("bobber_2.png"))
            #cv2.imshow("TPa", template)

            threshold = 0.8
            while True:
                screenshot = sct.grab(region)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)


                cv2.imshow("MiniGame", frame)

                found = False
                for scale in np.linspace(0.5, 1.5, 20):  # Adjust scale range and steps as needed
                    resized_template = cv2.resize(template, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
                    result = cv2.matchTemplate(frame, resized_template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                

                    if max_val >= threshold:
                        found = True
                        needle_w = resized_template.shape[1]
                        needle_h = resized_template.shape[0]
                        top_left = max_loc
                        bottom_right = (top_left[0] + needle_w, top_left[1] + needle_h)
                        cv2.rectangle(frame, top_left, bottom_right, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_4)

                        

                        if top_left[0] < region_width // 2:
                            #print("Object is in the left half. Pressing left mouse button.")
                            self.mouseController.press(MouseButton.left)
                        elif top_left[0] > region_width // 2:
                            #print("Object is in the right half. Releasing left mouse button.")
                            self.mouseController.release(MouseButton.left)
                        break

                if not found:
                    print("Not Found")
                    self.mouseController.release(MouseButton.left)
                    time.sleep(1)
                    cv2.destroyAllWindows()
                    break
             

            

               

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break


       
            

  