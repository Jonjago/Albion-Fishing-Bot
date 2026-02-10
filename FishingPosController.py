
import time
from Fishing import * 

class FishingPosController():

    def __init__(self, pos1, pos2, pos3, pos4):
        self.positionCount = 0
        self.postion1 = pos1
        self.postion2 = pos2
        self.postion3 = pos3
        self.postion4 = pos4

        self.posArea1 = None
        self.posArea2 = None
        self.posArea3 = None
        self.posArea4 = None

    
        self.counter = 0

        self.getPos  = [self.postion1, self.postion2, self.postion3, self.postion4]

        self.posLocation = []

        self.mouseController = MouseController()
       


        """
        +---------+---------+---------+
        | Bereich 1 [3,1] | Bereich 2 [3,2] | Bereich 3 [3,3] |
        +---------+---------+---------+
        | Bereich 4 [2,1] | Bereich 5 [2,2] | Bereich 6 [2,3] |
        +---------+---------+---------+
        | Bereich 7 [1,1] | Bereich 8 [1,2] | Bereich 9 [1,3] |
        +---------+---------+---------+

        Bereich 1: [0, 0] bis [640, 360]
        Bereich 2: [640, 0] bis [1280, 360]
        Bereich 3: [1280, 0] bis [1920, 360]

        Bereich 4: [0, 360] bis [640, 720]
        Bereich 5: [640, 360] bis [1280, 720]
        Bereich 6: [1280, 360] bis [1920, 720]

        Bereich 7: [0, 720] bis [640, 1080]
        Bereich 8: [640, 720] bis [1280, 1080]
        Bereich 9: [1280, 720] bis [1920, 1080]
        """


        self.Fishing = Fishing


    def get_area(self, x, y):
        # Bereichsgrößen
        area_width = 640
        area_height = 360

        # Spalte und Zeile berechnen
        col = x // area_width + 1  # Spalte (1, 2, 3)
        row = 3 - (y // area_height)  # Zeile (3, 2, 1)

        # Bereich zurückgeben
        #print (f"Cords are: {row, col} ")

        return (row, col)    

    def GetPositonCount(self):
        
        for pos in self.getPos:
            if pos != None:
                print("is set")
                self.positionCount +=1
            else:
                print("Is emty")

        print(f"{self.positionCount} found")
        return self.positionCount


    def ScreenPosIMG(self):
        counter = 0
        for cord in self.getPos:
            counter += 1 
            if cord != None:
                x,y = cord
                temp = self.get_area(x,y)

                if counter == 1:
                    self.posArea1 = temp
                elif counter == 2: 
                    self.posArea2 = temp
                elif counter == 3: 
                    self.posArea3 = temp
                elif counter == 4: 
                    self.posArea4 = temp
                print(temp)



    def SetNextPostion(self,):
        self.counter += 1

        if self.counter == self.positionCount +1:
            print("ResetTimer")
            self.counter = 0

        if self.counter == 1:
            print("Ara 1 is now Activ")
            print(f"Screen pos: {self.posArea1}")
            self.mouseController.position = self.getPos[0]
           
           
        elif self.counter == 2:
            print("Ara 2 is now Activ")
            print(f"Screen pos: {self.posArea2}")
            self.mouseController.position = self.getPos[1]
        
        elif self.counter == 3:
            print("Ara 3 is now Activ")
            print(f"Screen pos: {self.posArea3}")
            self.mouseController.position = self.getPos[2]

        elif self.counter == 4:
            print("Ara 4 is now Activ")
            print(f"Screen pos: {self.posArea4}")
            self.mouseController.position = self.getPos[3]

   



        #self.Fishing.StartFishing()


"""
pos1 = (112,773)
pos2 = (182,424)
pos3 = (1738,85)
pos4 = None
FishingPos = FishingPosController(pos1, pos2, pos3, pos4)
FishingPos.GetPositonCount()


FishingPos.ScreenPosIMG()
while True:
    time.sleep(1)

    area = FishingPos.SetNextPostion()
    #print(area)

    # new Template
    if area == (1,1):
        print("1. is activ")
    if area == (2,1):
        print("2. is activ")
    if area == (3,1):
        print("3. is activ")
    if area == (1,2):
        print("4. is activ")
    if area == (2,2):
        print("5. is activ")
    if area == (3,2):
        print("6. is activ")
    if area == (1,3):
        print("7. is activ")
    if area == (2,3):
        print("8. is activ")
    if area == (3,3):
        print("9. is activ")
        
        
    #FishingPos.SetNextPostion()
    #area =  FishingPos.get_area(1838, 50)
    #print(f"Mouse pos area is: {area}")
"""