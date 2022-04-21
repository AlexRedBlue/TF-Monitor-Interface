# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 14:30:36 2022

@author: alexd
"""

import tkinter as tk

from instruments import LOCKIN
from instruments import AGILENT_SIGNAL_GEN
from instruments import SignalGenerators
from instruments import AGILENT_MULTIMETER
from instruments import CAPACITANCE_BRIDGE

from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

import configparser
import os
import time
from datetime import datetime

import numpy as np

from handlers.trackers import diode_tracker, mct_tracker

class mainwindow_tkApp(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        self.state("zoomed")
        self.init_window_size()
        self.state("normal")
        self.geometry("{}x{}".format(int(self.screen_size["x"]/1.5), int(self.screen_size["y"]/1.5)))
        self.init_window_size()
        
        self.config = configparser.RawConfigParser()
        
        # if not os.path.exists('TFMI_Config.cfg'):
        #     self.initConfig()
        
        self.diode_start_button = tk.Button(master=self, text="Start Diode", bg='green', fg='white', height=2, width=9, command=self.start_diode)
        self.diode_start_button.place(x="{}i".format((self.win_zoom_inches["width"]/2-0.4)), y="{}i".format(self.win_zoom_inches["height"]*1/6))
        
        self.mct_start_button = tk.Button(master=self, text="Start MCT", bg='green', fg='white', height=2, width=9, command=self.start_mct)
        self.mct_start_button.place(x="{}i".format((self.win_zoom_inches["width"]/2-0.4)), y="{}i".format(self.win_zoom_inches["height"]*3/6))

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.update_idletasks()
        self.update()
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.on = False
            self.quit()
            self.destroy()
        
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
        
    def start_diode(self):
        self.diode_start_button.config(text="Stop Diode", bg="red", fg="white", command=self.stop_diode)
        # Main Loop
        try:
            gpib = input("GPIB num: ")
            gpib = "3"
            tracker = diode_tracker(AGILENT_MULTIMETER("GPIB0::"+gpib+"::INSTR"))
            self.run_diode = True
        except:
            self.run_diode = False
            print("tracker failed to initialize")
            self.diode_start_button.config(text="Start Diode", bg="green", fg="white", command=self.start_diode)
        while self.run_diode:
            try:
                tracker.take_data()
                update_time_left = 1000
                update_frequency = 100
                while update_time_left > 0:
                    if update_time_left > update_frequency:
                        self.after(update_frequency, self.update())
                    else:
                        self.after(update_time_left, self.update())
                if time.time() - tracker.timestamp_today > 24*60*60:
                    tracker.saved_data = np.array([])
                    tracker.get_today()
                elif time.time() - tracker.last_save > 60*60:
                    tracker.save_data()
                
            except Exception as e:
                print(e)
                if self.run_diode:
                    tracker.save_data()
                    self.run_diode = False
                    try:
                        self.quit()
                        self.destroy()
                    except Exception as e:
                        print(e)
    
        
    def stop_diode(self):
        self.diode_start_button.config(text="Start Diode", bg="green", fg="white", command=self.start_diode)
        self.run_diode = False
        
    def start_mct(self):
        self.diode_start_button.config(text="Stop MCT", bg="red", fg="white", command=self.stop_mct)
        # Main Loop
        try:
            # gpib = input("GPIB num: ")
            tracker = mct_tracker(DVM=AGILENT_MULTIMETER("GPIB0::7::INSTR"),
                                  Bridge=CAPACITANCE_BRIDGE("GPIB0::1::INSTR"),
                                  track_ratio=True,
                                  P=5E-5, I=300, D=60)
            self.run_mct = True
        except:
            self.run_mct = False
            print("tracker failed to initialize")
            self.diode_start_button.config(text="Start MCT", bg="green", fg="white", command=self.start_mct)
        while self.run_mct:
            try:
                tracker.take_data()
                update_time_left = 1000
                update_frequency = 100
                while update_time_left > 0:
                    if update_time_left > update_frequency:
                        self.after(update_frequency, self.update())
                    else:
                        self.after(update_time_left, self.update())
                if time.time() - tracker.timestamp_today > 24*60*60:
                    tracker.saved_data = np.array([])
                    tracker.get_today()
                elif time.time() - tracker.last_save > 60*60:
                    tracker.save_data()
                        
            except Exception as e:
                print(e)
                if self.run_mct:
                    tracker.save_data()
                    self.run_mct = False
                    try:
                        self.quit()
                        self.destroy()
                    except Exception as e:
                        print(e)
    
    def stop_mct(self):
        self.mct_start_button.config(text="Start MCT", bg="green", fg="white", command=self.start_mct)
        self.run_mct = False
        
if __name__ == "__main__":
    App = mainwindow_tkApp()
    App.mainloop()