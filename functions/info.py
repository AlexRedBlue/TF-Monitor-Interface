# -*- coding: utf-8 -*-
"""
Created on Mon Apr 11 13:54:18 2022

@author: physics-svc-mkdata
"""

from datetime import datetime
import numpy as np

def ticks_to_hours(graph, time_start, time_end):
    new_ticks = []
    xlabels = []
    # time if time length of data is < 30 minutes, use 7 HH:MM:SS; otherwise 9 HH:MM
    if (time_end - time_start) < 30*60:
        ticks = np.linspace(time_start, time_end, 7)
        for time in ticks:
            digital_time = datetime.fromtimestamp(time).strftime("%H:%M:%S")
            if digital_time not in xlabels:
                xlabels.append(digital_time)
                new_ticks.append(time)
    elif (time_end - time_start) < 24*60*60:
        ticks = np.linspace(time_start, time_end, 9)
        for time in ticks:
            digital_time = datetime.fromtimestamp(time).strftime("%H:%M")
            if digital_time not in xlabels:
                xlabels.append(digital_time)
                new_ticks.append(time)
    else:
        ticks = np.linspace(time_start, time_end, 7)
        for time in ticks:
            digital_time = datetime.fromtimestamp(time).strftime("%b %d %H:%M")
            if digital_time not in xlabels:
                xlabels.append(digital_time)
                new_ticks.append(time)

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
    
def phaseAdjust(theta):
    if theta > 0:
        theta = theta % 360
        if theta > 180:
            theta = theta - 360
    else:
        theta = theta % -360
        if theta < -180:
            theta = 360 + theta
    return theta
    
    