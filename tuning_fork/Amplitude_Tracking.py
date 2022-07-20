# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 13:38:03 2022

@author: alexd
"""

import numpy as np
import pandas as pd

tracking_cal = "calibration/tracking_calibration_polynomial.dat"
tracking_poly_coeffs = pd.read_csv(tracking_cal, sep='\t')

# print(tracking_poly_coeffs.columns)

polynomials = {}
for column in tracking_poly_coeffs.columns:
    polynomials[column] = np.poly1d(tracking_poly_coeffs[column])
    
def amplitude_tracker(frequency, current, drive):
    
    # current normalized to 25 mV drive
    current = current/drive*0.025
    
    # check if current is between 1 nA and 4 nA
    if current > 1 and current < 7:
        # TODO
        # Call this function in main program
        # Implement toggle for Amplitude Tracking
        # Add visual to show when running and when outside range
        # Create data handler for single freq measurements
        new_frequency = polynomials["f0 vs I"](current)
        if np.abs(new_frequency - frequency) < 10:
            return True, new_frequency
        else:
            return False, frequency
    else:
        
        return False, frequency
    
def temperature(current, drive):
    
    # current normalized to 25 mV drive
    current = current/drive*0.025
    # current in nA
    if current > 1 and current < 7:
        return polynomials["T vs I"](current)
    else:
        return np.nan
    
if __name__ == "__main__":
    import matplotlib.pyplot as plt
    c = np.linspace(1, 7, 100)
    plt.figure()
    plt.plot(c, 1e3*np.vectorize(temperature)(c))