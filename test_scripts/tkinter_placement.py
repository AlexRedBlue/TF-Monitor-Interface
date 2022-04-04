# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 11:59:45 2022

@author: physics-svc-mkdata
"""

import tkinter as tk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import numpy as np

class tkApp(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        self.screen_ratio = "16:9"
        self.screen_size = {"x":1920, "y":1080}
        self.screen_size_inches = {"width": 20, "height": 11.25}
        
        self.monitor_dpi = 96
        self.win_zoom_size = {"x":1920, "y":1017}
        self.win_zoom_inches = {"width": 1920/self.monitor_dpi, "height": 1017/self.monitor_dpi}
        
    
        
        self.state("zoomed")
        # self.print_size()
        
        self.wm_title("Testing")
        padding = 0.25
        self.graph = tk.Frame(self)
        self.graph.place(x="{}i".format(padding),y="0i")
        
        self.graph_2 = tk.Frame(self)
        self.graph_2.place(x="{}i".format(self.win_zoom_inches["width"]/2+padding),y="0i")

        
        self.fig = Figure(figsize=(self.win_zoom_inches["width"]/2-2*padding, (self.win_zoom_inches["width"]/2-2*padding)*4.8/6.4), dpi=self.monitor_dpi)
        self.ax = self.fig.add_subplot(2,1,1)
        self.ay = self.fig.add_subplot(2,1,2)
        
        x = np.linspace(0,2*np.pi)
        self.ax.plot(x, np.sin(x))
        self.ay.plot(x, np.cos(x))
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas_2 = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        self.canvas.get_tk_widget().pack(in_=self.graph)
        self.canvas_2.get_tk_widget().pack(in_=self.graph_2)
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph)
        self.toolbar.update()
        
        self.toolbar_2 = NavigationToolbar2Tk(self.canvas_2, self.graph_2)
        self.toolbar_2.update()
        
        
        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        
        self.param_entry_placement = tk.Frame(self)
        self.param_entry_placement.place(x="1i", y="8i")
        
        self.param_label_placement = tk.Frame(self)
        self.param_label_placement.place(x="2i", y="8i")
        
        self.entry_list = []
        self.label_list = []
        for i in range(4):
            self.entry_list.append(tk.Entry(self.param_entry_placement, width=8))
            self.label_list.append(tk.Label(self.param_label_placement, text=str(float(i)), width=8))
            self.entry_list[-1].pack(in_=self.param_entry_placement, pady=5)
            self.label_list[-1].pack(in_=self.param_label_placement, pady=5)
            
        
    def on_key_press(self, event):
        print("you pressed {}".format(event.key))
        key_press_handler(event, self.canvas, self.toolbar)
    
    def print_size(self):
        self.update_idletasks()
        print("The width of Tkinter window:", self.winfo_width())
        print("The height of Tkinter window:", self.winfo_height())
        
myApp = tkApp()
myApp.mainloop()