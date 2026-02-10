from pynput.mouse import Controller as MouseController
from pynput.mouse import Button as MouseButton
from Fishing import *

class FishingLocation():

    def __init__(self, CordsLoc1, CordsLoc2, CordsLoc3):
        #self.threshold = threshold
        self.CordsLoc1 = CordsLoc1
        self.CordsLoc2 = CordsLoc2
        self.CordsLoc3 = CordsLoc3



        self.global_fishingLocation = 0
       
      
        


    def FishingLocation(self, Threshold1, Threshold2, Threshold3):


        self.Threshold1 = Threshold1
        self.Threshold2 = Threshold2
        self.Threshold3 = Threshold3


        mouseController = MouseController()
        print("First: ", self.CordsLoc1)

        MouseControll = MouseController()
        Fish = Fishing(MouseControll)
     

        fishingLocation = self.global_fishingLocation

        if fishingLocation % 4 == 0:
            print("Location 1")
            mouseController.position = self.CordsLoc1
            time.sleep(0.5)
            Fish.StartFishing()
            self.global_fishingLocation += 1

            return self.Threshold2

         

        elif fishingLocation % 4 == 1:
            print("Location 2")
            time.sleep(0.5)
            mouseController.position = self.CordsLoc2
            Fish.StartFishing()

            self.global_fishingLocation += 1

            return self.Threshold3
        else:  # zaehler % 4 == 3
            print("Location 4")
            time.sleep(0.5) 
            mouseController.position = self.CordsLoc3
            Fish.StartFishing()
            self.global_fishingLocation += 1
            return self.Threshold1

    
    
    def FishingLocationForAudio(self):

        mouseController = MouseController()
        print("First: ", self.CordsLoc1)

        MouseControll = MouseController()
        Fish = Fishing(MouseControll)
     

        fishingLocation = self.global_fishingLocation

        if fishingLocation % 4 == 0:
            print("Location 1")
            mouseController.position = self.CordsLoc1
            time.sleep(0.5)
            Fish.StartFishing()
            self.global_fishingLocation += 1

        elif fishingLocation % 4 == 1:
            print("Location 2")
            time.sleep(0.5)
            mouseController.position = self.CordsLoc2
            Fish.StartFishing()
            self.global_fishingLocation += 1

        elif fishingLocation % 4 == 2:
            print("Location 3")
            time.sleep(0.5) 
            mouseController.position = self.CordsLoc3
            Fish.StartFishing()
            self.global_fishingLocation += 1
  


       
