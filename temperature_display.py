# -*- coding: utf-8 -*-
"""
Created on Fri Apr 15 02:31:38 2022

@author: alexd
"""

import tkinter as tk

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

class tkApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.state("zoomed")
        self.init_window_size()
        self.state("normal")
        self.geometry("{}x{}".format(int(self.screen_size["x"]/1.5), int(self.screen_size["y"]/1.5)))
        self.init_window_size()
        
        self.reset_data()
        
        self.graph_1 = tk.Frame(self)
        self.graph_1.place(x="0i",y="0i")
        
        self.fig = Figure(figsize=(self.win_zoom_size["x"]/self.standard_dpi, 0.9*self.win_zoom_size["y"]/self.standard_dpi), dpi=self.standard_dpi)
        self.graph_dict = {
                            "R8 Temperature": self.fig.add_subplot(3,1,1), 
                            "TF Temperature": self.fig.add_subplot(3,1,2), 
                            "MCT Temperature": self.fig.add_subplot(3,1,3)
                          }
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        self.canvas.get_tk_widget().pack(in_=self.graph_1)
        self.toolbar1 = NavigationToolbar2Tk(self.canvas, self.graph_1)
        self.toolbar1.update()
        self.canvas.get_tk_widget().pack(in_=self.graph_1)
        
        self.canvas.mpl_connect("key_press_event", self.on_key_press)
                
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def on_closing(self):
        self.update_idletasks()
        self.update()
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.on = False
            self.quit()
            self.destroy()
            
    def on_key_press(self, event):
         print("you pressed {}".format(event.key))
         key_press_handler(event, self.canvas, self.toolbar)
            
    def init_window_size(self):
        self.update_idletasks()
        self.standard_dpi = 288 # 1080p monitors
        standard_screen_size = {"x":1920, "y":1080}
        self.screen_ratio = {"width": 16, "height": 9}
        self.screen_size = {"x":self.winfo_screenwidth(), "y":self.winfo_screenheight()}
        self.screen_size_inches = {"width": self.winfo_screenwidth()/self.standard_dpi, 
                                    "height": self.winfo_screenheight()/self.standard_dpi}
        
        self.win_zoom_size = {"x":self.winfo_width(), "y":self.winfo_height()}
        
        self.win_zoom_inches = {"width": self.win_zoom_size["x"]/self.standard_dpi, 
                                "height": self.win_zoom_size["y"]/self.standard_dpi}
        self.scaling_factor = {"x": self.winfo_width()/standard_screen_size["x"],
                               "y": self.winfo_height()/standard_screen_size["y"]}
        
    def reset_data(self):
        self.data = {"time": [],
                "R8 Temperature": [],
                "TF Temperature": [],
                "MCT Temperature": []
                }
        
    def read_data(self):
        with open("test_scripts/temperature.txt", "r") as file:
            new_data = file.readlines()[1]
            print(new_data)
            new_data = new_data.split('\t')
            for idx, (key, val) in enumerate(self.data.items()):
                val.append(new_data[idx])

    def graph_data(self):
        for idx, (key, val) in enumerate(self.data.items()):
            if key != "time":
                self.graph_dict[key].clear()
                self.graph_dict[key].plot(self.data["time"], self.data[key])
        self.canvas.draw()
                
    def run(self):
        self.on = True
        while self.on:
            try:
                self.read_data()
                self.graph_data()
                self.update_idletasks()
                self.update()
                self.after(1000)
            except Exception as e:
                print(e)
                self.on = False
            

    
    
if __name__ == "__main__":
    myApp = tkApp()
    myApp.run()