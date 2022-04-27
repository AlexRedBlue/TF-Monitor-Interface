# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 14:30:36 2022

@author: alexd
"""

import tkinter as tk

# from instruments import LOCKIN
# from instruments import AGILENT_SIGNAL_GEN
# from instruments import SignalGenerators
from instruments import AGILENT_MULTIMETER
from instruments import CAPACITANCE_BRIDGE

# from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
# from matplotlib.backend_bases import key_press_handler
# from matplotlib.figure import Figure

import configparser
# import os
import time
# from datetime import datetime

import numpy as np

from handlers.trackers import diode_tracker, mct_tracker

from threading import Thread

import traceback

class mainwindow_tkApp(tk.Tk):
    
    def __init__(self):
        super().__init__()
        
        self.state("zoomed")
        self.init_window_size()
        self.state("normal")
        self.geometry("{}x{}".format(int(self.screen_size["x"]/1.5), int(self.screen_size["y"]/1.5)))
        self.init_window_size()
       
        self.config = configparser.RawConfigParser()
        
        self.diode_tracker = diode_tracker(AGILENT_MULTIMETER.AGILENT_MULTIMETER("GPIB0::3::INSTR"))
        self.mct_tracker = mct_tracker(DVM=AGILENT_MULTIMETER.AGILENT_MULTIMETER("GPIB0::7::INSTR"),
                                       Bridge=CAPACITANCE_BRIDGE.PRT_73("GPIB0::1::INSTR"),
                                       track_ratio=True,
                                       P=5E-5, I=300, D=60)
        
        self.diode_thread = Thread(target=self.start_diode)
        self.mct_thread = Thread(target=self.start_mct)
        
        # if not os.path.exists('TFMI_Config.cfg'):
        #     self.initConfig()
        self.run_cycle = ["|", "/", "-", "\\"]
        
        self.diode_start_button = tk.Button(master=self, text="Start Diode", bg='green', fg='white', height=2, width=9, command=self.start_diode_thread)
        self.diode_start_button.place(x="{}i".format((self.win_zoom_inches["width"]/2-0.4)), y="{}i".format(self.win_zoom_inches["height"]*1/6))
        
        self.diode_label = tk.Label(master=self, text="")
        self.diode_label.place(x="{}i".format((self.win_zoom_inches["width"]/2+0.4)), y="{}i".format(self.win_zoom_inches["height"]*1/6))
        
        self.mct_start_button = tk.Button(master=self, text="Start MCT", bg='green', fg='white', height=2, width=9, command=self.start_mct_thread)
        self.mct_start_button.place(x="{}i".format((self.win_zoom_inches["width"]/2-0.4)), y="{}i".format(self.win_zoom_inches["height"]*3/6))
        
        self.mct_label = tk.Label(master=self, text="")
        self.mct_label.place(x="{}i".format((self.win_zoom_inches["width"]/2+0.4)), y="{}i".format(self.win_zoom_inches["height"]*3/6))
        

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.update_idletasks()
        self.update()
        if tk.messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.run_diode = False
            self.run_mct = False
            try:
                self.quit()
                self.destroy()
            except:
                pass
            try:
                self.diode_tracker.save_data()
            except:
                traceback.print_exc()
                print("Diode data not saved")
            try:
                self.mct_tracker.save_data()
            except:
                traceback.print_exc()
                print("MCT data not saved")
            
            
        
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
    def start_diode_thread(self):
        self.diode_thread.start()
        
    def start_diode(self):
        self.diode_start_button.config(text="Stop Diode", bg="red", fg="white", command=self.stop_diode_thread)
        cycle = 0
        # Main Loop

        self.run_diode = True

        while self.run_diode:
            try:
                self.diode_tracker.take_data()
                update_time_left = 1000
                update_frequency = 100
                while update_time_left > 0:
                    if update_time_left > update_frequency:
                        self.after(update_frequency, self.update())
                    else:
                        self.after(update_time_left, self.update())
                    update_time_left -= update_frequency
                    if update_time_left % 3 == 0:
                        if cycle < 3:
                            cycle += 1
                        else:
                            cycle = 0
                        self.diode_label.config(text=self.run_cycle[cycle])
                if time.time() - self.diode_tracker.timestamp_today > 24*60*60:
                    self.diode_tracker.save_data()
                    self.diode_tracker.saved_data = np.array([])
                    self.diode_tracker.get_today()
                elif time.time() - self.diode_tracker.last_save > 60*60:
                    self.diode_tracker.save_data()
                
            except Exception as e:
                print(e)
                if self.run_diode:
                    self.diode_tracker.save_data()
                    self.run_diode = False
                    try:
                        self.quit()
                        self.destroy()
                    except Exception as e:
                        print(e)
    
        
    def stop_diode_thread(self):
        self.diode_start_button.config(text="Start Diode", bg="green", fg="white", command=self.stop_diode_thread)
        self.run_diode = False
        
    def start_mct_thread(self):
        self.mct_thread.start()
    
    def start_mct(self):
        self.mct_start_button.config(text="Stop MCT", bg="red", fg="white", command=self.stop_mct_thread)
        cycle = 0
        # Main Loop
        self.run_mct = True
        
        while self.run_mct:
            try:
                self.mct_tracker.take_data()
                update_time_left = 1000
                update_frequency = 100
                while update_time_left > 0:
                    if update_time_left > update_frequency:
                        self.after(update_frequency, self.update())
                    else:
                        self.after(update_time_left, self.update())
                    update_time_left -= update_frequency
                    if update_time_left % 3 == 0:
                        if cycle < 3:
                            cycle += 1
                        else:
                            cycle = 0
                        self.mct_label.config(text=self.run_cycle[cycle])
                if time.time() - self.mct_tracker.timestamp_today > 24*60*60:
                    self.mct_tracker.save_data()
                    self.mct_tracker.saved_data = np.array([])
                    self.mct_tracker.get_today()
                elif time.time() - self.mct_tracker.last_save > 60*60:
                    self.mct_tracker.save_data()   
            except Exception as e:
                print(e)
                if self.run_mct:
                    self.mct_tracker.save_data()
                    self.run_mct = False
                    try:
                        self.quit()
                        self.destroy()
                    except Exception as e:
                        print(e)
    
    def stop_mct_thread(self):
        self.mct_start_button.config(text="Start MCT", bg="green", fg="white", command=self.start_mct_thread)
        self.run_mct = False
        
if __name__ == "__main__":
    App = mainwindow_tkApp()
    App.mainloop()