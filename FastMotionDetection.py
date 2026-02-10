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
from FishingPosController import *
import tkinter as tk
import queue
import os
import sys


class FastMotionDetection:
    def __init__(self):
        self.is_detecting = True
        self.prev_time = None  
        self.mouseController = MouseController()
        self.keyboardController = Controller()
        self.miniGame = MiniGame(self.mouseController)
        self.Fishing = Fishing(self.mouseController)
        self.pause_event = threading.Event()
       

        self.pause_event.set()

        self.IsFishing = True
        self.AllCaughtFish = 0
     

        self.pos1B = True
        self.pos2B = True
        self.pos3B = True
        self.position1 = (497,1003)
        self.position2 = None
        self.position3 = None
        self.position4 = None


        self.useBait = False
        self.useFood = False

        self.threshold = 0.5 

    def Set_Postions(self, Pos1, pos2, pos3, pos4):
      
        getPositions = [Pos1,pos2,pos3,pos4]
        print(getPositions)
     
    
    

        if getPositions[0] != "": 
            self.position1 = tuple(map(int, getPositions[0].split(',')))
        if getPositions[1] != "":
            self.position2 = tuple(map(int, getPositions[1].split(',')))
        if getPositions[2] != "": 
            self.position3 = tuple(map(int, getPositions[2].split(',')))
        if getPositions[3] != "":
            self.position4 = tuple(map(int, getPositions[3].split(',')))
    
        self.FishingPosController = FishingPosController(self.position1,self.position2,self.position3,self.position4)
        self.FishingPosController.GetPositonCount()
        print(f"Its: {getPositions[1]}")
  
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




    def start_detection(self):
        """
        Startet die Bewegungserkennung für schnelle Bewegungen.
        """
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



         # Using by start
        if self.useFood:
            print("Using Food First to start")
            UseItems.UseFood()
        if self.useBait:
            print("Using Bait to start")
            UseItems.UseHook()

        self.FishingPosController.SetNextPostion()
        print(f"Bla : {self.position1}")

        fishing.StartFishing()

        TimerFood = threading.Thread(target=Timers.UseFood).start()
        TimerCaughFisch= threading.Thread(target=Timers.CheckIfFish).start()


        time.sleep(2)
        with mss.mss() as sct:
            prev_frame = None  # Vorheriger Frame für Bewegungsdifferenz
            self.prev_time = time.time()  # Initialer Zeitstempel

            while self.IsFishing:
                # Hole die aktuelle Mausposition
                mouse_x, mouse_y = pyautogui.position()

                # Dynamische Region basierend auf der Mausposition
                #region = self.get_screenshot_region(mouse_x, mouse_y, 90, 90)
                #screenshot = sct.grab(region)

                region = fishing.get_screenshot_regionMiniGame(125, 125)
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
                    if speed > 0.6:  # Schwellenwert für schnelle Bewegung
                        print("Schnelle Bewegung erkannt!")
                        self.mouseController.click(MouseButton.left, 1)
                        time.sleep(0.4)
                        self.miniGame.PlayGame()
                        self.mouseController.release(MouseButton.left)
                        time.sleep(2)
                        #self.mouseController.position = (468,977)
                      
                       
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
                            #mouseController.position = self.position1
                        
                        #For UI TIME
                        self.CountRuntimeFish()

                        self.FishingPosController.SetNextPostion()
                        fishing.StartFishing()

                    # Zeige die Bewegungserkennung im Fenster
                    cv2.imshow("Bewegungserkennung", thresh)

                # Aktuellen Frame speichern
                prev_frame = frame

                if Timers.timerCoughtFish >= 40 and CheckIfReady == True:
                        print(f"No Fish caught in the last {Timers.caughtFish} Minutes Change to next Position")
                        #mouseController.position = self.position1
                        self.FishingPosController.SetNextPostion()
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



        cv2.destroyAllWindows()

# Hauptprogramm
#if __name__ == "__main__":
#    detector = FastMotionDetection()
#    detector.start_detection()