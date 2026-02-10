import cv2
import numpy as np
import pyautogui
import time
from mss import mss

# Funktion zur Aufnahme eines 70x70-Bildes um die Mausposition
def capture_mouse_area():
    # Mausposition abrufen
    mouse_x, mouse_y = pyautogui.position()
    
    # Bereich um die Maus definieren (70x70 Pixel)
    monitor = {
        "top": mouse_y - 35,  # 35 Pixel nach oben
        "left": mouse_x - 35,  # 35 Pixel nach links
        "width": 70,  # Breite des Bereichs
        "height": 70  # Höhe des Bereichs
    }
    
    # Screenshot des Bereichs aufnehmen
    with mss() as sct:
        screenshot = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)  # Konvertiere von BGRA zu BGR
        return frame

# Funktion zur Erkennung der Angelboje
def detect_buoy(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Farbbereich für die Angelboje (anpassen an die Farbe der Boje)
    lower_color = np.array([0, 100, 100])  # Beispielwerte
    upper_color = np.array([10, 255, 255])
    
    # Maske erstellen
    mask = cv2.inRange(hsv, lower_color, upper_color)
    
    # Konturen finden
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if contours:
        # Größte Kontur auswählen (vermutlich die Boje)
        largest_contour = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(largest_contour)
        return (x, y, w, h), mask
    return None, mask

# Funktion zur Bewegungserkennung
def detect_movement(prev_frame, current_frame, buoy):
    x, y, w, h = buoy  # Bereich der Angelboje
    gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
    
    # Nur den Bereich der Angelboje analysieren
    roi_prev = gray1[y:y+h, x:x+w]
    roi_current = gray2[y:y+h, x:x+w]
    
    # Frame-Differenz berechnen
    diff = cv2.absdiff(roi_prev, roi_current)
    
    # Schwellenwert anwenden
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
    
    # Bewegung messen
    movement = np.sum(thresh)
    return movement > 500  # Schwellenwert anpassen

# Funktion zur Erkennung von Luftblasen
def detect_bubbles(frame, buoy):
    x, y, w, h = buoy  # Bereich der Angelboje
    roi = frame[y:y+h, x:x+w]  # Nur den Bereich der Angelboje analysieren
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Hough-Kreisdetektion
    circles = cv2.HoughCircles(
        gray, 
        cv2.HOUGH_GRADIENT, 
        dp=1.2, 
        minDist=10, 
        param1=50, 
        param2=30, 
        minRadius=2, 
        maxRadius=10
    )
    
    if circles is not None:
        return True  # Luftblasen erkannt
    return False

# Hauptfunktion
def main():
    print("Starte Fishing Bot...")
    time.sleep(2)  # Zeit, um das Spiel zu öffnen
    
    prev_frame = None  # Vorheriger Frame für Bewegungserkennung
    
    while True:
        # Screenshot des Bereichs um die Maus aufnehmen
        frame = capture_mouse_area()
        
        # Angelboje erkennen
        buoy, mask = detect_buoy(frame)
        
        if buoy:
            x, y, w, h = buoy
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            
            # Bewegung und Luftblasen erkennen
            if prev_frame is not None:
                movement_detected = detect_movement(prev_frame, frame, buoy)
                bubbles_detected = detect_bubbles(frame, buoy)
                
                if movement_detected and bubbles_detected:
                    print("Fisch hat angebissen! Klicke...")
                    pyautogui.click()  # Linksklick ausführen
                    time.sleep(1)  # Wartezeit nach dem Klick
            
            prev_frame = frame.copy()
        
        # Ergebnisse anzeigen (Debugging)
        cv2.imshow("Fishing Bot - Mausbereich", frame)
        cv2.imshow("Mask", mask)
        
        # Beenden mit der Taste 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cv2.destroyAllWindows()

# Programm starten
if __name__ == "__main__":
    main()