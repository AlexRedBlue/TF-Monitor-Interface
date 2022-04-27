# -*- coding: utf-8 -*-
"""
Created on Tue Jun  8 12:48:27 2021

@author: physics-svc-mkdata
"""

from instruments.LOCKIN import LI5640
from instruments.LOCKIN import SR830
from instruments.LAKESHORE import LS370

import logging

from display.trackers import lakeshore_tracker
import numpy as np
import matplotlib.pyplot as plt
import time
import os
from datetime import datetime

class test_lakeshore():
    def Read_R(self, channel=0):
        return channel+np.random.rand()
    def Autoscan(self, channels):
        # print("Starting Autoscan...\n")
        return np.random.rand(len(channels),2)

class test_lockin():
    def Read_XY(self):
        Vx = np.random.rand()
        Vy = np.random.rand()
        return Vx, Vy


def main_loop(lakeshore, channel_list,test, save_freq, wait_time, directory):
    
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    
    logging.basicConfig(filename='logging\\temperature_monitor.log', 
                        format='%(asctime)s: %(message)s', 
                        datefmt='%m/%d/%Y %H:%M:%S', 
                        level=logging.INFO)
    logging.info('Temperature measurement started')
    
    if test == True:
        print("Initializing Temperature Monitor Test.")
        tracker = lakeshore_tracker(
            lakeshore=test_lakeshore(), 
            channel_list=[1,2,3]
            )
    else:
        end_of_day_directory = "archive-data\\" + directory
        print("Initializing Temperature Monitor. \nStart Time: {}".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        tracker = lakeshore_tracker(
            lakeshore=lakeshore, 
            channel_list=channel_list
            )
        if "LSCI,MODEL370" not in tracker.lakeshore.ID:
            print("Error: Lake Shore not found.\n")
            return 0
    
    last_cache_clear = time.time()
    last_save = time.time()
    
    tracker.initialize_graphs()
    
    monitor = True
    while monitor==True:
        if time.time() - last_save > save_freq:
            tracker.save_data(directory=directory)
            logging.info("Hourly save success")
            last_save = time.time()
            if time.time() - tracker.timestamp_today > 24*60*60:
                tracker.save_data(directory=end_of_day_directory)
                tracker.save_fig(directory=end_of_day_directory+"\\figures")
                print("{}: End of day save success".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
                logging.info("Daily save success")
                tracker.data = []
                tracker.get_date()
        try:
            tracker.take_data(wait_time=wait_time)
            tracker.update_temperature_file()
            tracker.update_graphs()
            plt.pause(0.5)
    
        except KeyboardInterrupt:
            tracker.update_graphs()
            query = input("Paused: Continue? (y/n): ")
            logging.info("User Pause")
            if query == "y":
                logging.info("User Resume")
                pass
            else:
                tracker.save_data(directory=end_of_day_directory)
                tracker.save_fig(directory=end_of_day_directory+"\\figures")
                print("{}: Data saved Sucessfully. Exiting".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
                logging.info("User Terminated, data saved")
                monitor = False
        except Exception as e:
            print(e)
            tracker.save_data(directory=end_of_day_directory)
            tracker.save_fig(directory=end_of_day_directory+"\\figures")
            print("{}: Data saved Sucessfully. Exiting".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
            logging.info(e)
            logging.info("Program Terminated Unexpectedly, data saved")
            monitor = False

if __name__ == "__main__":
    cooldown_num = 4
    
    main_loop(lakeshore = LS370("GPIB0::6::INSTR"),
              channel_list = [1,2,3,4,5,6,7,8],
              test=False, save_freq=1*60*60, wait_time=8,
              directory=r'data\cooldown_{}\rt_data'.format(cooldown_num)
              # directory=r'data\PID_test\rt_data'
              )
    
    
    
    
    
    
    
    