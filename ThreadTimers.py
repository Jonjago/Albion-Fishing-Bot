import threading
import time


class ThreadTimers(threading.Thread):
    def __init__(self, caughtFish):
        super().__init__()
        self.timerCoughtFish = 0
        self.timerFood = 0
        self.caughtFish = caughtFish

        self.timerThreshold = 0
        self._running = True


    def stop(self):
        self._running = False 

    def UseFood(self):
        while  self._running :
            time.sleep(1)
            self.timerFood += 1
            if self.timerFood >= 1400:
                print("Timer for Food got resetet")
            print(f"Food: {self.timerFood}")

    
    def CheckIfFish(self):
        while  self._running :
            time.sleep(1)
            self.timerCoughtFish  += 1
           
       
            if self.caughtFish == True:
                self.timerCoughtFish = 0
                self.caughtFish = False




    def GetThreshold(self, currenThreshold):
        start_time = time.time()  # Startzeitpunkt
        while time.time() - start_time < 30:  # 30 Sekunden lang ausführen
            if self.timerThreshold < 44:
                if currenThreshold > self.threshold1:
                    faktor = 16.5 * currenThreshold / 100
                    self.threshold1 = currenThreshold - faktor
                    print(f"Neuer Thresholder1: {self.threshold1}")
                    time.sleep(0.4)
                return self.threshold2

            elif self.timerThreshold > 44 and self.timerThreshold < 88:
                if currenThreshold > self.threshold2:
                    faktor = 16.5 * currenThreshold / 100
                    self.threshold2 = currenThreshold - faktor
                    print(f"Neuer Thresholder2: {self.threshold2}")
                    time.sleep(0.4)
                return self.threshold3

            elif self.timerThreshold > 88 and self.timerThreshold < 132:
                print("Heil")
                if currenThreshold > self.threshold3:
                    faktor = 16.5 * currenThreshold / 100
                    self.threshold3 = currenThreshold - faktor
                    print(f"Neuer Thresholder3: {self.threshold3}")
                    time.sleep(0.4)
                return self.threshold1
            else:
                print("Kein neuer threshold")
                return
        print("30 Sekunden sind vorbei. Funktion beendet.")



    def ThresholdTimer(self):
        while True:
            self.timerThreshold += 1

           
            time.sleep(1)
            if self.timerThreshold >= 132:
               # print(f"Get ThresholdOvber: {self.timerThreshold}")

                return self.timerThreshold



