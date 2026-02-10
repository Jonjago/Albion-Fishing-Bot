import tkinter as tk
from tkinter import ttk

class App(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        # Beispiel-Widgets
        label = ttk.Label(self, text="Ich bin sichtbar!", font=("Arial", 16))
        label.pack(pady=20)
        button = ttk.Button(self, text="Klick mich!")
        button.pack(pady=20)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Fishing Bot by Techahoi")

    # Hintergrundfarbe setzen (diese wird transparent gemacht)
    root.config(bg="blue")  # Setze eine Farbe, die transparent gemacht wird
    

    # Transparenz aktivieren
    root.attributes("-transparentcolor", "blue")  # Macht die Farbe "blue" transparent

    # App-Frame hinzufügen
    app = App(root)
    app.pack(fill="both", expand=True)

    # Fenstergröße und Position festlegen
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry("+{}+{}".format(x_cordinate, y_cordinate - 20))

    root.mainloop()