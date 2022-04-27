# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 15:06:24 2021

@author: physics-svc-mkdata
"""

# TODO
# add class to instuments for the diode multimeter

from instruments.AGILENT_MULTIMETER import AGILENT_MULTIMETER

import logging

import os
import numpy as np
import matplotlib.pyplot as plt
from display.trackers import diode_tracker
import time
from datetime import datetime

class test_multimeter:
    def Read_V(self):
        return 0.1

# Default, do not change
def main_loop(test, save_freq, wait_time, multimeter, directory):
    
    logging.basicConfig(filename='logging\\diode_monitor.log', 
                        format='%(asctime)s: %(message)s', 
                        datefmt='%m/%d/%Y %H:%M:%S', 
                        level=logging.INFO)
    logging.info('Diode measurement started')
    
    if test == True:
        print("Initizalizing Diode Monitor Test.")
        tracker = diode_tracker(multimeter = test_multimeter())
    else:
        end_of_day_directory = "archive-data\\" + directory
        print("Initizalizing Diode Monitor. \nStart Time: {}".format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
        tracker = diode_tracker(multimeter = multimeter)
    
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
            tracker.take_data()
            tracker.update_temperature_file()
            tracker.update_graphs()
            plt.pause(wait_time)
    
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

# Change Params Here
if __name__ == "__main__":
    cooldown_num = 4
    main_loop(test=False, 
              save_freq=1*60*60, wait_time=1.0,
              multimeter=AGILENT_MULTIMETER("GPIB0::3::INSTR"),
              directory=r'data\cooldown_{}\diode_data'.format(cooldown_num))
    