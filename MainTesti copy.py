import cv2
import numpy as np
import pyautogui
import mss
import time
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button as MouseButton
from pynput.keyboard import Key, Controller
from PIL import Image
import sched
import threading
from MiniGame import *
from Fishing import *
from UseItems import *
from ThreadTimers import *
from FishingLocation import *
from GetFilePath import * 
import tkinter as tk
import queue
import os
import sys

class MainTesti():

    def __init__(self):
        self.getFilePath = GetFilePath
        self.pause_event = threading.Event()
        self.pause_event.set()

        self.IsFishing = True
        self.AllCaughtFish = 0
     

        self.pos1B = True
        self.pos2B = True
        self.pos3B = True
        self.position1 = (497,1003)
        #self.position2 = (327,731)
        self.position3 = (1396,1020)



        self.useBait = False
        self.useFood = False

        self.threshold = 0.5 

    def Set_Postions(self, Pos1, pos2, pos3, pos4):
        getPositions = [Pos1, pos2,pos3,pos4]
        print(getPositions)
        self.position1 = tuple(map(int, getPositions[0].split(',')))
        print(self.position1)
   
        

    def update_attribute(self, UseBait, UseFood):
        """Method to update an attribute."""
        self.useBait = UseBait
        self.useFood = UseFood

        print(f"Attribute updated to: {self.useBait} {self.useFood}")

    def CountRuntimeFish(self):
       # """Simulate catching a fish and return the updated count."""
        self.AllCaughtFish += 1
        print("Current Count: ", self.AllCaughtFish)
        return self.AllCaughtFish


    def SetCurrentFishingLocation(self):
        print("Fishing Location")
        

    def EndFishing(self):
        self.IsFishing = False  

    def LookForMiniEvent(self):
        print("Start Fishing")
        self.IsFishing = True

        debugMode = True
        caughtFishBool = False
        caughtFish = 0
  



        CheckIfReady = True


        mouseController = MouseController()
        keyboardController = Controller()

     
        fishing = Fishing(mouseController)
        miniGame = MiniGame(mouseController)
        UseItems = UseItem(keyboardController,mouseController, debugMode)
        Timers = ThreadTimers(caughtFishBool)

        


        if not os.path.exists(self.getFilePath.resource_path('ImageBobber/EV31.png')):
            print("File 'ImageBobber' not found!")
        else:
            template31 = cv2.imread(self.getFilePath.resource_path('ImageBobber/EV31.png'), cv2.IMREAD_UNCHANGED) 
            template_height, template_width = template31.shape[:2]  






        if not os.path.exists(self.getFilePath.resource_path('ImageBobber/ET32.png')):
            print("File 'ImageBobber' not found!")
        else:
            template21 = cv2.imread(self.getFilePath.resource_path('ImageBobber/ET32.png'), cv2.IMREAD_UNCHANGED) 
            template_height, template_width = template21.shape[:2]  

        
        if not os.path.exists(self.getFilePath.resource_path('ImageBobber/ET11.png')):
            print("File 'ImageBobber' not found!")
        else:
            template11 = cv2.imread(self.getFilePath.resource_path('ImageBobber/ET11.png'), cv2.IMREAD_UNCHANGED) 
            template_height, template_width = template11.shape[:2]  


        # SetStarting pos:
        template = template31




        # Get Center of Monitor
        # 1920 / 2 = 960 x
        # 1080 / 2 = 540
        mouseController.position = (960,540)
        mouseController.click(MouseButton.left, 1)
        time.sleep(2)




        # Using by start
        if self.useFood:
            print("Using Food First to start")
            UseItems.UseFood()
        if self.useBait:
            print("Using Bait to start")
            UseItems.UseHook()

        mouseController.position = self.position1
        print(f"Bla : {self.position1}")

        fishing.StartFishing()

        TimerFood = threading.Thread(target=Timers.UseFood).start()
        TimerCaughFisch= threading.Thread(target=Timers.CheckIfFish).start()

        with mss.mss() as sct:
                while self.IsFishing:

                           
                    screenshot = sct.grab(sct.monitors[1])
                    frame2 = np.array(screenshot)

                    self.pause_event.wait()

                    region = fishing.get_screenshot_regionMiniGame(130, 130)
                    screenshot = sct.grab(region)

                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGRA)

                    result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

                
                    if max_val >= self.threshold:

                        top_left = max_loc
                        bottom_right = (top_left[0] + template_width, top_left[1] + template_height)
                        cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
                        mouseController.press(MouseButton.left)
                        time.sleep(0.2)
                        mouseController.release(MouseButton.left)
                       # mouseController.position = self.position2
                        miniGame.PlayGame()
                        time.sleep(0.5)
                        mouseController.position = self.position1

                        Timers.timerCoughtFish = 0
                
                        caughtFish += 1
                        print(f"CaughFish: {caughtFish} : Bool: {self.useBait}")
                        if self.useBait == True and caughtFish >= 10: 
                            print("Using Bait")
                            UseItems.UseHook()
                            mouseController.position = self.position1

                            caughtFish = 0

                        # 1800 sec
                        if self.useFood == True and Timers.timerFood > 1800 and CheckIfReady == True:
                            print("Using Food")
                            UseItems.UseFood()
                            time.sleep(0.5)

                            Timers.timerFood = 0
                           
                            # WORKING: Changing to multiple positions
                            mouseController.position = self.position1
                
                        #For UI TIME
                        self.CountRuntimeFish()

                        fishing.StartFishing()



                        """
                        # Switch to next template image
                        if area == (1,1):
                            print("1. is activ")
                            template = template31
                        if area == (2,1):
                            print("2. is activ")
                            template = template21
                        if area == (3,1):
                            print("3. is activ")
                            template = template11
                        if area == (1,2):
                            print("4. is activ")
                            template = template32
                        if area == (2,2):
                            print("5. is activ")
                            template = template22
                        if area == (3,2):
                            print("6. is activ")
                            template = template12
                        if area == (1,3):
                            print("7. is activ")
                            template = template33
                        if area == (2,3):
                            print("8. is activ")
                            template = template23
                        if area == (3,3):
                            print("9. is activ")
                            template = template13
                        else:
                             print("ERROR: Invalide position")
                         """










                        cv2.destroyAllWindows()
                       # self.CountRuntimeFish()
                        #time.sleep(1)

                    if Timers.timerCoughtFish >= 40 and CheckIfReady == True:
                        print(f"No Fish caught in the last {Timers.caughtFish} Minutes Change to next Position")
                        mouseController.position = self.position1
                        fishing.StartFishing()
                        time.sleep(2)
                            
                        Timers.timerCoughtFish = 0


                    if debugMode == True:
                        cv2.imshow("Search", frame)
                    
                    
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

       
                                       
                    if self.IsFishing == False:
                        Timers.stop()
                        print("Bot Ist False")


                self.pause_event.wait()
               
 

    def pause(self):
        print("Pausing thread...")
        self.pause_event.clear()  # Pause the thread

    def resume(self):
        print("Resuming thread...")
        self.pause_event.set()  # Resume the thread

