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

from functions.info import ticks_to_hours

from datetime import datetime
from time import mktime

import numpy as np
import glob

import warnings
import traceback

class tkApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.state("zoomed")
        self.init_window_size()
        self.state("normal")
        self.geometry("{}x{}".format(int(self.screen_size["x"]/1.5), int(self.screen_size["y"]/1.5)))
        self.init_window_size()

        
        self.graph_1 = tk.Frame(self)
        self.graph_1.place(x="0i",y="0i")
        
        self.fig = Figure(figsize=(self.win_zoom_size["x"]/self.standard_dpi, 0.9*self.win_zoom_size["y"]/self.standard_dpi), dpi=self.standard_dpi)
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)  # A tk.DrawingArea.
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_1)
        self.toolbar.update()
        self.canvas.get_tk_widget().pack(in_=self.graph_1)
        
        self.reset_data()

        self.reset_button = tk.Button(self, text='reset', bg='red', fg='white', command=self.reset_data)
        self.reset_button.place(x=int(self.win_zoom_size["x"]/2), y=self.win_zoom_size["y"]-40)
        
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
        self.standard_dpi = 96 # 1080p monitors
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
    
    def get_today(self):
        now = datetime.now()
        self.today = datetime(year=now.year, month=now.month, day=now.day)
        self.timestamp_today = mktime(self.today.timetuple())
        self.today = self.today.strftime("%Y-%m-%d")
        # print(self.timestamp_today)
        
    def reset_data(self):
        self.temperature_fnames = glob.glob(r"C:\Users\physics-svc-mkdata\Documents\recent_temperature\*.dat")
        self.get_today()
        self.canvas.figure = Figure(figsize=(self.win_zoom_size["x"]/self.standard_dpi, 0.9*self.win_zoom_size["y"]/self.standard_dpi), dpi=self.standard_dpi)
        self.graph_dict = {}
        for idx, file in enumerate(self.temperature_fnames):
            if idx != 0:
                self.graph_dict[file] = self.canvas.figure.add_subplot(len(self.temperature_fnames),1,idx+1, sharex=self.graph_dict.get(self.temperature_fnames[0]))
            else:
                self.graph_dict[file] = self.canvas.figure.add_subplot(len(self.temperature_fnames),1,idx+1)

        
        self.data = {}
        for fname in self.temperature_fnames:
            self.data[fname] = {"time": [], "temperature": []}
        self.graph_data()
        self.update()
        
    def read_data(self):
        new_data = False
        for idx, fname in enumerate(self.temperature_fnames):
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    time, temperature = np.loadtxt(fname)
                if time not in self.data[fname]["time"]:
                    self.data[fname]["time"].append(time)
                    self.data[fname]["temperature"].append(temperature)
                    new_data = True
            except:
                pass
        return new_data
            
    def create_label(self, T):
        if T > 100:
            power = 0
            label = "{:.1f}".format(T*10**power)
            units = " K"
        elif T > 10:
            power = 0
            label = "{:.2f}".format(T*10**power)
            units = " K"
        elif T > 1:
            power = 0
            label = "{:.3f}".format(T*10**power)
            units = " K"
        elif T > 0.1:
            power = 3
            label = "{:.1f}".format(T*10**power)
            units = " mK"
        elif T > 0.01:
            power = 3
            label = "{:.2f}".format(T*10**power)
            units = " mK"
        elif T > 0.001:
            power = 3
            label = "{:.3f}".format(T*10**power)
            units = " mK"
        elif T > 0.0001:
            power = 6
            label = "{:.1f}".format(T*10**power)
            units = " uK"
        return label, units, power
            
    def graph_data(self): 
        for key in self.temperature_fnames:
            self.graph_dict[key].clear()
            try:
                label, units, power = self.create_label(self.data[key]["temperature"][-1])
            except:
                label, units, power = '', '', 0
            # print(label, power, units)
            self.graph_dict[key].plot(np.asarray(self.data[key]["time"]), np.asarray(self.data[key]["temperature"])*(10**power), label=label+units)
            self.graph_dict[key].set_xlabel("time, s")
            ylabel = key.split('\\')[-1][0:-4]
            self.graph_dict[key].set_ylabel(ylabel+units)
            self.graph_dict[key].legend(loc=2)
            try:
                if time0 > self.data[key]["time"][0]:
                    time0 = self.data[key]["time"][0]
            except:
                try:
                    time0 = self.data[key]["time"][0]
                except:
                    pass
            try:
                if time1 < self.data[key]["time"][-1]:
                    time1 = self.data[key]["time"][-1]
            except:
                try:
                    time1 = self.data[key]["time"][-1]
                except:
                    pass
        try:
            ticks_to_hours(self.graph_dict[self.temperature_fnames[0]], time0, time1)
        except:
            pass
        self.graph_dict[self.temperature_fnames[0]].set_title("Temperature Monitor")
        self.canvas.draw()
                
    def run(self):
        self.on = True
        while self.on:
            try:
                new_data = self.read_data()
                if new_data:
                    self.graph_data()
                self.update_idletasks()
                self.update()
                update_time_left = 1000
                update_frequency = 100
                while update_time_left > 0:
                    if update_time_left > update_frequency:
                        self.after(update_frequency, self.update())
                    else:
                        self.after(update_time_left, self.update())
                    update_time_left -= update_frequency
            except Exception as e:
                print(e)
                traceback.print_exc()
                self.on = False
            

    
    
if __name__ == "__main__":
    myApp = tkApp()
    myApp.run()