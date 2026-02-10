import tkinter as tk
from tkinter import ttk
from pynput import mouse, keyboard

class MousePositionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Position Setter")
        
        self.tab_control = ttk.Notebook(root)
        self.tab_2 = ttk.Frame(self.tab_control)
        self.tab_control.add(self.tab_2, text="Tab 2")
        self.tab_control.pack(expand=1, fill="both")
        
        # Create labels, entries, and buttons
        self.entries = []
        for i in range(4):
            label = ttk.Label(self.tab_2, text=f"{i + 1}.")
            label.grid(row=i + 1, column=0, padx=0, pady=0, sticky="w")
            
            entry = ttk.Entry(self.tab_2, width=6)
            entry.grid(row=i + 1, column=1, padx=0, pady=0, sticky="w")
            self.entries.append(entry)
            
            button = ttk.Button(self.tab_2, text="SET", width=5)
            button.grid(row=i + 1, column=2, padx=0, pady=0, sticky="w")
        
        # Track the current entry to fill
        self.current_entry_index = 0
        
        # Bind F12 key to capture mouse position
        self.root.bind("<F12>", self.capture_mouse_position)
    
    def capture_mouse_position(self, event=None):
        # Get the current mouse position
        mouse_controller = mouse.Controller()
        x, y = mouse_controller.position
        
        # Fill the current entry with the mouse position
        if self.current_entry_index < len(self.entries):
            self.entries[self.current_entry_index].delete(0, tk.END)
            self.entries[self.current_entry_index].insert(0, f"{x}, {y}")
            self.current_entry_index += 1  # Move to the next entry
        else:
            print("All entries are filled!")

# Create the main application window
root = tk.Tk()
app = MousePositionApp(root)
root.mainloop()