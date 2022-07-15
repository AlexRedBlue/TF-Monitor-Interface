# -*- coding: utf-8 -*-
"""
Created on Tue Jul 12 22:50:56 2022

@author: alexd
"""

import numpy as np
import pandas as pd
import os

class amplitude_data:
    def __init__():
        self.data = {
            "time, s": [],
            "amplitude, nA": [],
            "frequency, hz": []
            }
        
    def save_data(self, fname):
        if not os.path.exists(fname):
            pd.DataFrame(self.data).save_csv()
        
    