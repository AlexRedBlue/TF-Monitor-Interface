# -*- coding: utf-8 -*-
"""
Created on Wed Aug 11 11:44:43 2021

@author: physics-svc-mkdata
"""

from instruments.AGILENT_MULTIMETER import AGILENT_MULTIMETER
from instruments.CAPACITANCE_BRIDGE import PRT_73

import logging
import traceback

from display.trackers import mct_tracker
import numpy as np
import matplotlib.pyplot as plt
import time
import os
from datetime import datetime

def main_loop(DVM, Bridge, track_ratio, P, I, D, test, save_freq, wait_time, directory):

    end_of_day_directory = "archive-data\\" + directory
    print("Initializing MCT Monitor.")
    
    logging.basicConfig(filename='logging\\mct_monitor.log', 
                        format='%(asctime)s: %(message)s', 
                        datefmt='%m/%d/%Y %H:%M:%S', 
                        level=logging.INFO)
    logging.info('MCT measurement started')
    
    tracker = mct_tracker(
        DVM=DVM, 
        Bridge=Bridge,
        track_ratio=track_ratio,
        P=P,
        I=I,
        D=D
        )

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
            logging.info("User Pause")
            query = input("Paused: Continue? (y/n): ")
            if query == "y":
                logging.info("User Resume")
                pass
            else:
                tracker.save_data(directory=end_of_day_directory)
                tracker.save_fig(directory=end_of_day_directory+"\\figures")
                logging.info("User Terminated, data saved")
                print("Saved Data Successfully.")
                monitor = False
        except Exception as e:
            traceback.print_exc()
            tracker.save_data(directory=end_of_day_directory)
            tracker.save_fig(directory=end_of_day_directory+"\\figures")
            print("Data saved Sucessfully. Exiting")
            logging.info(e)
            logging.info("Program Terminated Unexpectedly, data saved")
            monitor = False

if __name__ == "__main__":
    # TODO
    # Auto adjust PID to proper values for smoother temperature curve
    cooldown = 4
    
    main_loop(DVM = AGILENT_MULTIMETER("GPIB0::7::INSTR"),
              Bridge = PRT_73("GPIB0::1::INSTR"),
              track_ratio = False,
              P=5E-5, I=300, D=60,
              test=False, save_freq=1*60*60, wait_time=1,
              directory=r'data\cooldown_{}\MCT_data'.format(cooldown)
              # directory=r'data\PID_test\rt_data'
              )