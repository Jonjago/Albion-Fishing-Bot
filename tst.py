import pyaudio
import numpy as np
import time
from MiniGame import *
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button as MouseButton

mouseController = MouseController()
miniGame = MiniGame(mouseController)

# Audio-Konfiguration
CHUNK = 1024  # Anzahl der Samples pro Frame
FORMAT = pyaudio.paInt16  # Audioformat
CHANNELS = 1  # Mono
RATE = 44100  # Abtastrate

# Initialisiere PyAudio
p = pyaudio.PyAudio()

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=1)  # Stelle sicher, dass VB-CABLE hier ausgewählt ist

print("Höre auf Audio...")

# Variable to track the last detection time
last_detection_time = 0
cooldown_time = 3  # Cooldown in seconds (adjust as needed)

def erkenne_fisch(audio_data):
    global last_detection_time

    # Analysiere das Audiosignal (z. B. Frequenz oder Lautstärke)
    audio_array = np.frombuffer(audio_data, dtype=np.int16)
    lautstärke = np.abs(audio_array).mean()

    # Check if the volume exceeds the threshold and if the cooldown has passed
    current_time = time.time()
    if lautstärke > 20 and (current_time - last_detection_time > cooldown_time):
        print("Fisch erkannt!")
        last_detection_time = current_time  # Update the last detection time
        mouseController.click(MouseButton.left, 1)
        time.sleep(0.5)
        miniGame.PlayGame()
  

def Main():
    try:
        while True:
            data = stream.read(CHUNK)
            erkenne_fisch(data)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

Main()