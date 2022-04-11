# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 13:54:18 2022

@author: physics-svc-mkdata
"""

from datetime import timedelta
import numpy as np

def ticks_to_hours(graph, time_start, time_end):
    new_ticks = []
    xlabels = []
    time_start, time_end = time_start/3600, time_end/3600
    # time if time length of data is < 30 minutes, use 7 HH:MM:SS; otherwise 9 HH:MM
    if (time_end - time_start)*60 < 30:
        ticks = np.linspace(time_start, time_end, 7)
        for idx, val in enumerate(ticks):
            dt = str(timedelta(seconds=int(val*3600)))
            if dt not in xlabels:
                xlabels.append(dt)
                new_ticks.append(val*3600)
    else:
        ticks = np.linspace(time_start, time_end, 9)
        for idx, val in enumerate(ticks):
            dt = str(timedelta(seconds=int(val*3600))).split(":")
            try:
                time = float(dt[0]) + float(dt[1])/60
            except:
                time = val
            dt = dt[0]+":"+dt[1]
            if dt not in xlabels:
                xlabels.append(dt)
                new_ticks.append(time*3600)

    graph.set_xticks(new_ticks)
    graph.set_xticklabels(xlabels)

def close_win(top):
        top.destroy()
        
def isStrInt(text):
    try:
        int(text)
        return True
    except:
        return False
    
def isStrFloat(text):
    try:
        float(text)
        return True
    except:
        return False