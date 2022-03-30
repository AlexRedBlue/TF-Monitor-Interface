# -*- coding: utf-8 -*-
"""
Created on Thu Jan 20 13:40:29 2022

@author: physics-svc-mkdata
"""
import numpy as np
from scipy import interpolate

def load_calibration(self):
    calibration_directory = r"C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\calibration"
    file_name = "\\08-20-08-26_rvt_calibration_main.dat"
    R8_file_name = "\\R8_RT_Curve.dat"
    self.calibration = np.loadtxt(calibration_directory+file_name, delimiter="\t", skiprows=1)
    self.R8_calibration = np.loadtxt(calibration_directory+R8_file_name, delimiter="\t", skiprows=1)
    self.R8_sorted = self.R8_calibration[:,0].argsort()
    self.r_sorted_list = list()
    for i in range(self.calibration.shape[1]-2):
        self.r_sorted_list.append(self.calibration[:,i+2].argsort())




def create_interpolated_curve(R, T):
    tck = interpolate.splrep(R,T)
    return tck
    
if __name__ == "__main__":
    calibration_directory = r"C:\Users\physics-svc-mkdata\Documents\GitHub\data-monitoring\calibration"
    file_name = "\\08-20-08-26_rvt_calibration_main.dat"
    R8_file_name = "\\R8_RT_Curve.dat"
    calibration = np.loadtxt(calibration_directory+file_name, delimiter="\t", skiprows=1)
    R8_calibration = np.loadtxt(calibration_directory+R8_file_name, delimiter="\t", skiprows=1)
    R8_sorted = R8_calibration[:,0].argsort()
    R, T = R8_calibration[R8_sorted,0], R8_calibration[R8_sorted,1]
    tck = create_interpolated_curve(R, T)
    test_R = 2000
    new_T=interpolate.splev(test_R,tck)
    print(new_T)
    
    import matplotlib.pyplot as plt
    plt.figure()
    plt.plot(R, T)
    plt.scatter(test_R, new_T, color="red")