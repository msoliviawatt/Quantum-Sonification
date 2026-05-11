import threading
import numpy as np
import sounddevice as sd
import tkinter as tk
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class GUI:
    def __init__(self):
        self._build_gui()

    def run(self):
        self.root.mainloop()

    def on_close(self):
        self.running = False

        try:
            if (self.stream is not None):
                self.stream.stop()
                self.stream.close()
        finally:
            self.root.destroy()

    def _build_gui(self):
        self.root = tk.Tk()
        self.root.title("Electro-Optic Interferomter")
        self.root.geometry("1000x75")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)