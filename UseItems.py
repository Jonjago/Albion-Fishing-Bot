import time
from pynput.keyboard import Key, Controller
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button as MouseButton
import cv2
import numpy as np
import pyautogui
import mss

from GetFilePath import * 




class UseItem:

    def __init__(self, keyboardController, mouseController, debug):
        self.mouseController = mouseController
        self.keyboardController = keyboardController
        self.debug = debug

        self.getFilePath = GetFilePath



    def get_screenshot_region(self, width, height):
        screenshot_width = width
        screenshot_height = height

        mouse_x, mouse_y = pyautogui.position()
        left = max(0, mouse_x - screenshot_width // 2)
        top = max(0, mouse_y - screenshot_height // 2)
        return {"top": top, "left": left, "width": screenshot_width, "height": screenshot_height}


    def UseFood(self):
        print("Using food")
        time.sleep(1.5)
        InventroyPosi = (1583,543)
        Pos2 = (1800,368)

        self.keyboardController.press('2')
        self.keyboardController.release('2')
        time.sleep(1.5)             
        self.mouseController.position = InventroyPosi
        self.mouseController.press(MouseButton.left)
        time.sleep(0.5)
        self.mouseController.position = Pos2
        self.mouseController.release(MouseButton.left)
        time.sleep(2)

        position1 = (481, 1006)
                    # Setze die Maus auf die erste Position
        self.mouseController.position = position1
        time.sleep(0.5)
        print("Item Used")
             

    def TakeScreenShot(self):
        with mss.mss() as sct:
            screenshot = sct.grab(sct.monitors[1])
            WorldImg = np.array(screenshot)

        return cv2.cvtColor(WorldImg, cv2.COLOR_BGR2GRAY)
        
    def UseHook(self):
        HookTir = cv2.imread(self.getFilePath.resource_path(os.path.join("InventoryImgs", "TirIII.png")))
        HookBtn = cv2.imread(self.getFilePath.resource_path(os.path.join("InventoryImgs", "UseHookBTn.png")))


        HookTir = cv2.cvtColor(HookTir, cv2.COLOR_BGR2GRAY)
        HookBtn = cv2.cvtColor(HookBtn, cv2.COLOR_BGR2GRAY)
        WorldImg = self.TakeScreenShot()


        found = False
        for scale in np.linspace(0.5, 1.5, 20):  # Adjust scale range and steps as needed
            resized_template = cv2.resize(HookTir, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
            resultIcon = cv2.matchTemplate(WorldImg, resized_template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(resultIcon)

            #print("Val: ",max_val)
            if max_val >= 0.7:
                found = True
                needle_w = resized_template.shape[1]
                needle_h = resized_template.shape[0]
                top_left = max_loc
                bottom_right = (top_left[0] + needle_w, top_left[1] + needle_h)
                cv2.rectangle(WorldImg, top_left, bottom_right, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_4)
                



                # Berechne die Mitte des gefundenen Bereichs für den Klick
                click_xIcon = top_left[0] + needle_w // 2
                click_yIcon = top_left[1] + needle_h // 2
                
                # Klicke auf die gefundene Position
                self.mouseController.position = click_xIcon,click_yIcon
                self.mouseController.click(MouseButton.left, 1)
                #pyautogui.click(click_xIcon, click_yIcon)
                print(f"Geklickt auf: ({click_xIcon}, {click_yIcon})")

                time.sleep(0.5)
                
                # find use Btn
                WorldImg = self.TakeScreenShot()
                resized_template = cv2.resize(HookBtn, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR)
                resultIcon = cv2.matchTemplate(WorldImg, resized_template, cv2.TM_CCOEFF_NORMED)
                min_valButton, max_valButton, min_locButton, max_locButton = cv2.minMaxLoc(resultIcon)

                

                if max_valButton >= 0.5:
                    print("Found button")

                    needle_w = resized_template.shape[1]
                    needle_h = resized_template.shape[0]
                    top_left = max_locButton
                    bottom_right = (top_left[0] + needle_w, top_left[1] + needle_h)
                    cv2.rectangle(WorldImg, top_left, bottom_right, color=(0, 255, 0), thickness=2, lineType=cv2.LINE_4)


                    click_xBtn = top_left[0] + needle_w // 2
                    click_yIBtn = top_left[1] + needle_h // 2
                    
                    
                    # Klicke auf die gefundene Position BTN
                    self.mouseController.position = click_xBtn,click_yIBtn
                    self.mouseController.click(MouseButton.left, 1)
                    time.sleep(0.5)

                    # Klicke auf die gefundene Position close menu
                    self.mouseController.position = click_xIcon,click_yIcon
                    self.mouseController.click(MouseButton.left, 1)
                    time.sleep(0.5)
                    
                    if self.debug == True:
                        cv2.imshow("Testing", WorldImg)
                        cv2.destroyAllWindows()
                    
                break

            else:
                print("No Bait found")
