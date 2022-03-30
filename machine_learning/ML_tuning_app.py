# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 14:37:00 2021

@author: alexd
"""

import numpy as np
from tuning_fork import Lorentz_Fitting as LF

class test_tuning_fork:
    f_0 = 32700
    width = 5
    
    def adjust_params(self):
        self.f_0 = self.f_0 + np.random.uniform(low=-5, high=5)
        self.width = self.width + np.random.uniform(low=-4, high=4)
        if self.width < 1:
            self.width = np.random.uniform(low=1, high=5)
    
    def get_y_point(self, x):
        return (1/(2*np.pi))*self.width/((x-self.f_0)**2 + self.width**2)

class test_setup:
    start_freq = 32600
    end_freq = 32800
    points = 120
    drive = 1
    sens = 1    
    tf = test_tuning_fork()
    setting_history = []
    
    def __init__(self):
        self.save_hist()
    
    def save_hist(self):
        self.setting_history.append([self.start_freq, self.end_freq, self.points, self.drive, self.sens, self.tf.width, self.tf.f_0])
        
    def sweep(self):
        x = np.linspace(self.start_freq, self.end_freq, self.points)
        y = np.zeros(np.size(x))
        for idx, point in enumerate(x):
            y[idx] = self.tf.get_y_point(point)
        guess = [(x[-1]+x[0])/2, 1E-3, (x[-1] - x[0])/10, 0, 0, 0]
        fit_coeffs, flag_fc = LF.Lorentz_Fit_X(x, y, guess)
        print(flag_fc)
        
        self.tf.adjust_params()
    
    def score_params(self, x, y):
        return 0

test_setup_01 = test_setup()
test_setup_01.sweep()

    