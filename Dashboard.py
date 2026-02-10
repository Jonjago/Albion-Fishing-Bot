import tkinter as tk
from tkinter import ttk
from MainTesti import *
import keyboard
from FastMotionDetection import *

class App(ttk.Frame):

    
    def __init__(self, parent):
        ttk.Frame.__init__(self)


    
    
        # Make the app responsive
        for index in [0, 1, 2]:
            self.columnconfigure(index=index, weight=1)
            self.rowconfigure(index=index, weight=1)

        # Create value lists
        self.option_menu_list = ["", "OptionMenu", "Option 1", "Option 2"]
        self.combo_list = ["Combobox", "Editable item 1", "Editable item 2"]
        self.readonly_combo_list = ["Readonly combobox", "Item 1", "Item 2"]

        # Create control variables
        self.var_0 = tk.BooleanVar()
        self.var_1 = tk.BooleanVar(value=True)
        self.var_2 = tk.BooleanVar()
        self.var_3 = tk.IntVar(value=2)
        self.var_4 = tk.StringVar(value=self.option_menu_list[1])
        self.var_5 = tk.DoubleVar(value=75.0)


        self.entry_value1 = None
        self.entry_value2 = None
        self.entry_value4 = None
        self.entry_value3 = None

        # Create widgets :)
        self.setup_widgets()

    def setup_widgets(self):
        Main = MainTesti()
        Motion = FastMotionDetection()
          # Panedwindow
        self.paned = ttk.PanedWindow(self)
        self.paned.grid(row=0, column=2, pady=(25, 5), sticky="nsew", rowspan=3)

        # Pane #1
        self.pane_1 = ttk.Frame(self.paned, padding=5)
        self.paned.add(self.pane_1, weight=1)


         # Notebook, pane #2
        self.pane_2 = ttk.Frame(self.paned, padding=5)
        self.paned.add(self.pane_2, weight=3)

        # Notebook, pane #2
        self.notebook = ttk.Notebook(self.pane_2)
        self.notebook.pack(fill="both", expand=True)

        # Tab #1
        self.tab_1 = ttk.Frame(self.notebook)
        for index in [0, 1]:
            self.tab_1.columnconfigure(index=index, weight=1)
            self.tab_1.rowconfigure(index=index, weight=1)
        self.notebook.add(self.tab_1, text="Main")

        # Tab #2
        self.tab_2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_2, text="Areas")
        

        # Tab #3
        self.tab_3 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_3, text="Extras")

        


        self.tab_4 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_4, text="Debug")

   
        self.canvas = tk.Canvas(self.tab_2)
        self.scrollbar = ttk.Scrollbar(self.tab_2, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        # Configure the canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.t_label = ttk.Label(
            self.tab_1,
            text="Time:",
            justify="left",
            font=("-size", 8, "-weight", "bold"),
        )
        self.t_label.grid(row=0, column=0, pady=2, padx=0, columnspan=1, sticky="w")



        # Start
        self.entryTimer = ttk.Entry(self.tab_1,)
        self.entryTimer.insert(0, "00:00:00")
        self.entryTimer.grid(row=1, column=0, padx=5, pady=2, sticky="ew")

        self.running = False
        self.elapsed_time = 0  # Time in seconds

        def start_timer():
            self.running = True
            update_timer()

        def stop_timer():
             self.running = False

        def reset_timer():
            self.elapsed_time = 0
            self.entryTimer.delete(0, tk.END)
            self.entryTimer.insert(0, "00:00:00")

        def update_timer():
            if self.running:
                self.elapsed_time += 1
                hours, remainder = divmod(self.elapsed_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                self.entryTimer.delete(0, tk.END)
                self.entryTimer.insert(0, f"{hours:02}:{minutes:02}:{seconds:02}")
                root.after(1000, update_timer)  # Timer erneut aufrufen


        self.radio_1 = ttk.Radiobutton(
            self.tab_1, text="Use Edge (Beta)", variable=self.var_3, value=2
        )
        self.radio_1.grid(row=1, column=1, padx=5, pady=2, sticky="nsew")

        self.radio_2 = ttk.Radiobutton(
            self.tab_1, text="Use Sound (Comming)", variable=self.var_3, value=1,state = tk.DISABLED 
        )
        self.radio_2.grid(row=2, column=1, padx=5, pady=2, sticky="nsew")

  
        """
        self.cf_label = ttk.Label(
            self.tab_1,
            text="Caught Fisch:",
            justify="left",
            font=("-size", 8, "-weight", "bold"),
        )
        self.cf_label.grid(row=2, column=0, pady=2, padx=0, columnspan=1, sticky="w")

       # self.entryCF = ttk.Entry(self.tab_1,)
       # self.entryCF.insert(0, "0")
        #self.entryCF.grid(row=3, column=0, padx=5, pady=2, sticky="ew")
        #self.entryCF.bind( lambda event: AllFish())
        """
     


        self.toggle_button = ttk.Checkbutton(
            self.tab_1, 
            text="Start", 
            style="Toggle.TButton",
            command=lambda: Start(),
            variable=self.var_5
        )
        self.toggle_button.grid(row=4, column=0, padx=5, pady=2, sticky="w")

    
        self.inc = 0
        self.isOn = False
        def Start():
            if self.isOn:
                print("Stop Bot")
                stop_timer()  
                reset_timer() 

                self.toggle_button.config(text="Play") 
                self.isOn = False

                Motion.EndFishing()
           
            else:
                print("Start Bot") 
                print(f"Value 3: {self.entry_value3}")  
                print(f"Value 4: {self.entry_value4}")
                Motion.Set_Postions( self.entry1.get(), self.entry2.get(),  self.entry3.get(),  self.entry4.get())
           
                start_timer()  
           

                self.toggle_button.config(text="Stop") 
                self.isOn = True

              
                bot_thread = threading.Thread(target=Motion.start_detection)
                bot_thread.daemon = True
                bot_thread.start()
                print("hell")
                 
                    
           

       


            

        self.rest_button = ttk.Button(
            self.tab_1, 
            text="Reset", 
            style="Toggle.TButton",
        )
        self.rest_button.grid(row=4, column=1, padx=5, pady=5, sticky="ew")


        self.info_label = ttk.Label(
            self.tab_2,
            text="Select Fishing Area [F2]",
            justify="left",
            font=("-size", 10, "-weight", "bold"),
        )
        self.info_label.grid(row=0, column=0, pady=0, padx=0, columnspan=2, sticky="w")

# Labels für die Eingabefelder
         # Labels für die Eingabefelder
        self.label1 = ttk.Label(self.tab_2, text="1.",)
        self.label1.grid(row=1, column=0, padx=0, pady=0, sticky="w")  # Minimaler Abstand
                  
        self.entry1 = ttk.Entry(self.tab_2, width=8,  font=("-size", 10, "-weight", "bold"))
        self.entry1.grid(row=1, column=1, padx=0, pady=0, sticky="w")  # Minimaler Abstand
       
        self.label2 = ttk.Label(self.tab_2, text="2.")
        self.label2.grid(row=2, column=0, padx=0, pady=0, sticky="w")  # Minimaler Abstand
        
        self.entry2 = ttk.Entry(self.tab_2, width=8,font=("-size", 10, "-weight", "bold"))
        self.entry2.grid(row=2, column=1, padx=0, pady=0, sticky="w")  # Minimaler Abstand
      
        self.label3 = ttk.Label(self.tab_2, text="3.")
        self.label3.grid(row=3, column=0, padx=0, pady=0, sticky="w")  # Minimaler Abstand
        
        self.entry3 = ttk.Entry(self.tab_2, width=8,font=("-size", 10, "-weight", "bold"))
        self.entry3.grid(row=3, column=1, padx=0, pady=0, sticky="w")  # Minimaler Abstand 
       
        self.label4 = ttk.Label(self.tab_2, text="4.")
        self.label4.grid(row=4, column=0, padx=0, pady=0, sticky="w")  # Minimaler Abstand
        
        self.entry4 = ttk.Entry(self.tab_2, width=8,font=("-size", 10, "-weight", "bold"))
        self.entry4.grid(row=4, column=1, padx=0, pady=0, sticky="w")  # Minimaler Abstand
       

        def record_mouse_position():
            # Mausposition abrufen
            x = root.winfo_pointerx()
            y = root.winfo_pointery()
            print(f"Mausposition: x={x}, y={y}")

            self.entry_value1 = self.entry1.get()
            self.entry_value2 = self.entry2.get()
            self.entry_value3 = self.entry3.get()
            self.entry_value4 = self.entry4.get()

            if self.entry_value1.strip() == "":
                #print("1. is Free")
                #self.entry1.delete()
                self.entry1.insert(0, f"{x},{y}")
                print(f"Val1: { self.entry1.get()}")

            elif self.entry_value2.strip() == "":
                #print("2. is Free")
                self.entry2.insert(0, f"{x},{y}")
                print(f"Val2: { self.entry2.get()}")

            elif self.entry_value3.strip() == "":
                #print("3. is Free")
                self.entry3.insert(0, f"{x},{y}")
                print(f"Val3: {self.entry3.get()}")

            elif self.entry_value4.strip() == "":
                #  print("4. is Free")
                self.entry4.insert(0, f"{x},{y}")
                print(f"Val4: { self.entry4.get()}")
            else:
                print("all positions are alreadyd set")

            print(f"Entry Values: {self.entry1.get()}, {self.entry2.get()}, {self.entry3.get()}, {self.entry4.get()}")


        keyboard.add_hotkey("space", record_mouse_position)



        # Extras

        self.selected_option = tk.StringVar(value="Use Food")  # Default selection

        # Create the radio buttons
        self.use_food_var = tk.BooleanVar(value=False)  # Default unchecked
        self.use_bait_var = tk.BooleanVar(value=False)  # Default unchecked

        # Create the checkbuttons
        self.check_food = ttk.Checkbutton(
            self.tab_3,
            text="Use Food",
            variable=self.use_food_var,
            #command=lambda :  UpdateMainParameters()
        )
        self.check_food.grid(row=1, column=0, padx=5, pady=2, sticky="w")

        self.check_bait = ttk.Checkbutton(
            self.tab_3,
            text="Use Bait",
            variable=self.use_bait_var,
         
        )
        self.check_bait.grid(row=2, column=0, padx=5, pady=2, sticky="w")

        # Create the Save button
        self.save_button = ttk.Button(
            self.tab_3,
            text="Save",
            style="Toggle.TButton",
            command=lambda : UpdateMainParameters()  # Method to call when the button is clicked
        )
        self.save_button.grid(row=3, column=0, padx=5, pady=5, sticky="w")
                
        def UpdateMainParameters():
                print("Parmaeter übergabe")
                food_selected = self.use_food_var.get()  # Korrektur: Klammern hinzufügen
                bait_selected = self.use_bait_var.get()  # Korrektur: Klammern hinzufügen
    
                # Call the update_attribute method with the boolean values
                Motion.update_attribute(bait_selected,food_selected)
        

        


     





   





    
def StartBot():
    print("Der Bot wird Gestartet!")
  

lastClickX = 0
lastClickY = 0


def SaveLastClickPos(event):
    global lastClickX, lastClickY
    lastClickX = event.x
    lastClickY = event.y


def Dragging(event):
    x, y = event.x - lastClickX + root.winfo_x(), event.y - lastClickY + root.winfo_y()
    root.geometry("+%s+%s" % (x , y))




if __name__ == "__main__":
    root = tk.Tk()
    root.title("Fishing Bot by Techahoi")

    # Simply set the theme
    root.tk.call("source", "azure.tcl")
    root.tk.call("set_theme", "dark")

    app = App(root)
    app.pack(fill="both", expand=True)


    # Set a minsize for the window, and place it in the middle
    root.update()
    root.minsize(root.winfo_width(), root.winfo_height())
    x_cordinate = int((root.winfo_screenwidth() / 2) - (root.winfo_width() / 2))
    y_cordinate = int((root.winfo_screenheight() / 2) - (root.winfo_height() / 2))
    root.geometry("+{}+{}".format(x_cordinate, y_cordinate-20))


    window_width = 100  # Set your desired width
    window_height = 100  # Set your desired height
    root.geometry(f"{window_width}x{window_height}")


    root.wm_attributes("-topmost", True)
    root.overrideredirect(True)

    root.wm_attributes("-alpha", 0.9)
    # Set the root window background color to a transparent color

    root.bind('<Button-1>', SaveLastClickPos)
    root.bind('<B1-Motion>', Dragging)

    root.mainloop()


