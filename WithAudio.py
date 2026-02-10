import pyaudio
import numpy as np
import time
# Einstellungen
CHUNK = 512  # Kleinere Chunk-Größe
FORMAT = pyaudio.paInt16  # Audioformat (16 Bit)
CHANNELS = 2  # Mono
rate=44100  # Sampling-Rate (Hz)
frames_per_buffer=1024
VOLUME_THRESHOLD =71  # Schwellenwert für die Lautstärke

# PyAudio-Instanz erstellen
p = pyaudio.PyAudio()

# Audio-Stream öffnen
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=rate,
                input=True,
                frames_per_buffer=CHUNK)

print("Überwache Audioeingabe...")

try:
    while True:
        # Audio-Daten lesen
        data = stream.read(CHUNK, exception_on_overflow=False)
        
        # Daten in numpy-Array umwandeln
        audio_data = np.frombuffer(data, dtype=np.int16)
        
        # Lautstärke berechnen (z. B. RMS)
        volume = np.sqrt(np.mean(audio_data ** 2))
        
        print(f"Lautstärke: {volume}")
        
        # Prüfen, ob die Lautstärke den Schwellenwert überschreitet
        if volume > VOLUME_THRESHOLD:
            print("Lautstärke zu hoch! If-Statement wird ausgeführt.")
            # Hier kannst du eine Aktion ausführen
            # Beispiel:
            print("JEy")


        time.sleep(0.5)

except KeyboardInterrupt:
    print("Beendet durch Benutzer.")

finally:
    # Stream schließen
    stream.stop_stream()
    stream.close()
    p.terminate()