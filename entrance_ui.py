from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage
import tkinter.font as font
import tkinter as tk

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path("./assets")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

class Entrance_UI(Canvas):
    def __init__(self, parent): 
        Canvas.__init__(self, parent)
        self.configure(
            bg = "#FFFFFF",
            height = 600,
            width = 1000,
            bd = 0,
            relief = "ridge",
            highlightthickness = 0,
        )
        
        self.place(x = 0, y = 0)
        self.input = tk.StringVar(self)
        self.entry_1 = Entry(self,
            textvariable = self.input,
            bd=0,
            bg="#C4C4C4",
            highlightthickness=0
        )
        self.myFont = font.Font(family='Helvetica', size=20)
        self.entry_1['font'] = self.myFont
        self.entry_1.place(
            x=552.0,
            y=300.5,
            width=320.0,
            height=58.0
        )
        
        self.button_image_1 = PhotoImage(
            file=relative_to_assets("button.png"))
        self.button_1 = Button(self,
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=lambda: print("button_1 clicked"),
            relief="flat"
        )
        self.button_1.place(
            x=635.0,
            y=408.0,
            width=154.0,
            height=57.0
        )
        
        self.image_image_1 = PhotoImage(
            file=relative_to_assets("image.png"))
        self.image_1 = self.create_image(
            494.0,
            300.0,
            image=self.image_image_1
        )
