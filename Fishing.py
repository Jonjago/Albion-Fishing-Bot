import cv2 
import mss
import numpy as np
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button as MouseButton
import time
from UseItems import *

class Fishing: 
    def __init__(self, mouseController):
        self.mouseController = mouseController
        self.UseItemTime = time.time()

    
    def get_screenshot_regionMiniGame(self, width, height):

        # for edge detection
        # befor = 70
        screenshot_width = width
        screenshot_height = height

        mouse_x, mouse_y = pyautogui.position()
        left = max(0, mouse_x - screenshot_width // 2)
        top = max(0, mouse_y - screenshot_height // 2)
        return {"top": top, "left": left, "width": screenshot_width, "height": screenshot_height}
 
   

    def StartFishing(self):
        print("start fishing")
        time.sleep(0.5)
        self.mouseController.press(MouseButton.left)
        time.sleep(2)
        self.mouseController.release(MouseButton.left)
        time.sleep(1)
        

        return
