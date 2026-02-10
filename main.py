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

def LookForMiniEvent():
    debugMode = True
    caughtFishBool = False
    caughtFish = 0

    useFood = True
    useBait = True


    pos1B = True
    pos2B = True
    pos3B = True
    position1 = (497,1003)
    position2 = (327,731)
    position3 = (1396,1020)


    mouseController = MouseController()
    keyboardController = Controller()

    fishing = Fishing(mouseController)
    miniGame = MiniGame(mouseController)
    UseItems = UseItem(keyboardController,mouseController, debugMode)
    Timers = ThreadTimers(caughtFishBool)
    FishingLoc = FishingLocation(position1,position2,position3)

    TimerFood = threading.Thread(target=Timers.UseFood).start()
    TimerCaughFisch= threading.Thread(target=Timers.CheckIfFish).start()
    

    with mss.mss() as sct:

        if useFood == True:
            UseItems.UseFood()
        if useBait == True:
            UseItems.UseHook()


        screenshot = sct.grab(sct.monitors[1])
        frame2 = np.array(screenshot)

        currentThresh = 0

        # Schauen ob das Richitge Angeln schon angefangen hat
        CheckIfReady = False

        TimerThre = threading.Thread(target=Timers.ThresholdTimer).start()
        #cv2.imshow("hahaha", frame2)
        while True:
            print(Timers.timerCoughtFish)

            # Screenshot-Bereich basierend auf der Mausposition berechnen2
            region = fishing.get_screenshot_regionMiniGame(70,70)
            # Screenshot des Bereichs erstellen
            screenshot = sct.grab(region)

            frame = np.array(screenshot)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.GaussianBlur(frame,(3,3),0)
            frame = cv2.Canny(image=frame, threshold1=35, threshold2=100)

            averageImg = np.average(frame)

            if Timers.timerThreshold < 135:
                
               Threshold = threading.Thread(target=Timers.GetThreshold, args=(averageImg,)).start()
               #print("Val: ", Timers.threshold , " Timer: ", Timers.timerThreshold)

                # Get Trehsold from Positions
               if Timers.timerThreshold < 44 and pos1B == True:
                    #mouseController.click(MouseButton.left, 1)
                    pyautogui.press('d')
                    print("Start new Locaation")
                    time.sleep(1)
                    mouseController.position = position1
                    fishing.StartFishing()
                    time.sleep(0.7)

                    pos1B = False

               elif Timers.timerThreshold > 44 and Timers.timerThreshold < 88 and pos2B == True:
                    #mouseController.click(MouseButton.left, 1)
                    pyautogui.press('d')
                    time.sleep(0.5)
                    print("Start new Location 2")
                    mouseController.position = position2
                    fishing.StartFishing()
                    time.sleep(0.7)
                    pos2B = False

               elif Timers.timerThreshold > 88 and Timers.timerThreshold < 132 and pos3B == True:
                    #Timers.threshold3 = 0
                    #mouseController.click(MouseButton.left, 1)
                    pyautogui.press('d')
                    time.sleep(0.5)
                    print("Start new Location 3")
                    mouseController.position = position3
                    fishing.StartFishing()
                    pos3B = False

                    currentThresh = Timers.threshold1
                    #print("Thres3: ", Timers.threshold3)
               else:
                   next
                    #mouseController.position = position2
                


            if debugMode == True:
                cv2.imshow("Live Screenshot at Mouse Position", frame)
                #print(averageImg, " Max: ", Timers.threshold1)


            if cv2.waitKey(1) & 0xFF == ord("q"):
                continue
            
            
         

            #  if averageImg >= Timers.threshold3 and Timers.timerThreshold > 130:
            if averageImg >= currentThresh and Timers.timerThreshold > 130:
                #print("fish triggert")
                cv2.destroyAllWindows()

                mouseController.click(MouseButton.left, 1)
                time.sleep(0.5)
                mouseController.release(MouseButton.left)
                    
                miniGame.PlayGame()
                last_five_minute_action = time.time()   


                time.sleep(0.5)
                currentThresh  = FishingLoc.FishingLocation(Timers.threshold1, Timers.threshold2, Timers.threshold3)           
                
               

                #mouseController.position = position3d
                time.sleep(0.5)

                
                CheckIfReady = True

                Timers.caughtFish = True
                caughtFish += 1
                print("Caught fish: ", str(caughtFish))
                
                
            else:
                # Du nutzt den dreck zum erckenen von th weren
                #print("Th: ", averageImg ,  " 3Th: ", Timers.threshold3, "Time: ", Timers.timerThreshold)
                #print("Time fihsing", current_time - last_five_minute_action)

                # Was 90 sec bevor
                if Timers.timerCoughtFish >= 45 and CheckIfReady == True:
                    #print("5 Minuten sind vergangen, führe die Aktion aus.")
                    
                    mouseController.press(MouseButton.left)
                        


                    time.sleep(0.4)
                    currentThresh  = FishingLoc.FishingLocation(Timers.threshold1, Timers.threshold2, Timers.threshold3)   
                    Timers.timerCoughtFish = 0

                    #fishing.StartFishing()
                   # mouseController.position = position1
                    time.sleep(0.5)


         
            if useFood == True and Timers.timerFood > 1500 and CheckIfReady == True:
                UseItems.UseFood()
                time.sleep(0.7)
                currentThresh  = FishingLoc.FishingLocation(Timers.threshold1, Timers.threshold2, Timers.threshold3)     
                Timers.timerFood = 0
                print("User hat grade was gegessen!")
             
                #mouseController.position = position2
                time.sleep(0.7)
                #fishing.StartFishing()
                
                print("UseBait: ", caughtFish)
            if useBait == True and caughtFish >= 10: 

                UseItems.UseHook()
                currentThresh  = FishingLoc.FishingLocation(Timers.threshold1, Timers.threshold2, Timers.threshold3)     
                caughtFish = 0
                
                #mouseController.position = position2
                time.sleep(0.7)
                #fishing.StartFishing()
         


        
            time.sleep(0.1)


time.sleep(2)

LookForMiniEvent()
"""""
def UseFishForLV():
    time.sleep(1.5)
    InventroyPosi = (1583,543)
    Pos2 = (1800,368)
    counter = 0
    while True:

        keyboardController.press('2')
        keyboardController.release('2')
        counter += 1
        print(counter)
        time.sleep(1.5)
        if counter == 9:
                
            mouseController.position = InventroyPosi
            print("Pos 1")
            mouseController.press(MouseButton.left)
            time.sleep(1.5)
            mouseController.position = Pos2
            print("Pos 2")
            mouseController.release(MouseButton.left)
            #2222222222time.sleep(10)
            counter = 0

UseFishForLV()"
"""""