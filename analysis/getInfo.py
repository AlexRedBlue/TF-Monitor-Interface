# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 12:18:23 2022

@author: alexd
"""

# import numpy as np
import pandas as pd
import glob
import os

import time
from datetime import datetime

def get_start_date(timestamp):
    start = datetime.fromtimestamp(timestamp)
    day_0 = datetime(year=start.year, month=start.month, day=start.day)
    time_0 = time.mktime(day_0.timetuple())
    return day_0, time_0

def get_timestamp_from_day(month_day_year, end_of_day=0):
    month, day, year = month_day_year.split("-")
    month, day, year = int(month), int(day), int(year)
    if end_of_day == 1:
        dt = datetime(year=year, month=month, day=day, hour=23, minute=59)
    elif end_of_day == 0:
        dt = datetime(year=year, month=month, day=day) 
    return time.mktime(dt.timetuple())

def get_files(directory, data_name):
    file_list = glob.glob(directory+'*.dat')
    df_files = pd.DataFrame(columns=['date', 'num'])
    for file in file_list:
        name, date, num = file[len(directory):-4].split('_')
        df_files = df_files.append({'date' : date, 'num' : int(num)}, ignore_index=True)
    file_dates = df_files['date'].unique()
    file_nums = df_files.groupby(['date']).max().to_numpy()[:,0]
    
    file_list = []
    for idx, value in enumerate(file_dates):
        
        file_list.append(directory+'{}_{}_{}.dat'.format(data_name, file_dates[idx],file_nums[idx]))
    return file_list
    
def get_directory(data_type, time_period, archive=True):
    if archive == True:
        return r'C:\Users\alexd\Documents\GitHub\data-monitoring\archive-data\data\{}\{}'.format(time_period, data_type)
    else:
        return r'C:\Users\alexd\Documents\GitHub\data-monitoring\data\{}\{}'.format(time_period, data_type)


def import_MCT_data_from_directory(directory, verbose=False):
    # key = lambda x: x.split('.')[0]
    # data_name = 'MCT'
    file_list = sorted(glob.glob(directory+r'\mct_*.dat'), key=os.path.getmtime)
    data_list = []
    unique_indexes = []
    
    for file in file_list:
        data_list.append(pd.read_csv(file, sep="\t", index_col=None, names=["Time, s", "Ratio", "Voltage, V", "Temperature, K"], skiprows=2))
    if verbose == True:
        print(file_list[-1][len(directory):], ' Accepted')
    unique_indexes.append(-1)
    
    for i in range(len(data_list)-2, -1, -1):
        try:
            if data_list[i].to_numpy()[-1,0] not in data_list[i+1].to_numpy()[:,0]:
                if verbose == True:
                    print(file_list[i][len(directory):], ' Accepted')
                unique_indexes.append(i)
            else:
                if verbose == True:
                    print(file_list[i][len(directory):], ' Not accepted')
                pass
        except:
            if verbose == True:
                print(file_list[i][len(directory):], ' Empty')
            pass
    mct_data = pd.concat([data_list[x] for x in unique_indexes])
    return mct_data

def import_tf_data_from_directory(directory, verbose=False):
    
    # data_name = 'MC_TFT'
    file_list = sorted(glob.glob(directory+'\\*.dat'), key=os.path.getmtime)
    # print(file_list)
    data_list = []
    unique_indexes = []
    
    for file in file_list:
        data_list.append(pd.read_csv(file, sep="\t", index_col=None, header=0))
    if verbose == True:
        print(file_list[-1][len(directory):], ' Accepted')
    unique_indexes.append(-1)
    for i in range(len(data_list)-2, -1, -1):
        try:
            if data_list[i].to_numpy()[-1,0] not in data_list[i+1].to_numpy()[:,0]:
                if verbose == True:
                    print(file_list[i][len(directory):], ' Accepted')
                unique_indexes.append(i)
            else:
                if verbose == True:
                    print(file_list[i][len(directory):], ' Not accepted')
                pass
        except:
            if verbose == True:
                print(file_list[i][len(directory):], ' Empty')
            pass
    tf_data = pd.concat([data_list[x] for x in unique_indexes])
    return tf_data


def import_diode_data_from_directory(self, directory,
                                         verbose=False):
        # key = lambda x: x.split('.')[0]
        data_name = 'diode'
        file_list = sorted(glob.glob(directory+r'\diode_*.dat'), key=os.path.getmtime)
        data_list = []
        unique_indexes = []
        
        for file in file_list:
            data_list.append(pd.read_csv(file, sep="\t", index_col=None, header=0))
        if verbose == True:
            print(file_list[-1][len(directory):], ' Accepted')
        unique_indexes.append(-1)
        for i in range(len(data_list)-2, -1, -1):
            try:
                if data_list[i].to_numpy()[-1,0] not in data_list[i+1].to_numpy()[:,0]:
                    if verbose == True:
                        print(file_list[i][len(directory):], ' Accepted')
                    unique_indexes.append(i)
                else:
                    if verbose == True:
                        print(file_list[i][len(directory):], ' Not accepted')
                    pass
            except:
                if verbose == True:
                    print(file_list[i][len(directory):], ' Empty')
                pass
        self.diode_data = pd.concat([data_list[x] for x in unique_indexes])
        

def import_rt_data_from_directory(directory,
                                  verbose=False):
    
    # data_name = 'rt'
    file_list = sorted(glob.glob(directory+r'\rt_*.dat'), key=os.path.getmtime)
    data_list = []
    unique_indexes = []
    
    for file in file_list:
        data_list.append(pd.read_csv(file, sep="\t", index_col=None, header=0))
    if verbose == True:
        print(file_list[-1][len(directory):], ' Accepted')
    unique_indexes.append(-1)
    for i in range(len(data_list)-2, -1, -1):
        try:
            if data_list[i].to_numpy()[-1,0] not in data_list[i+1].to_numpy()[:,0]:
                if verbose == True:
                    print(file_list[i][len(directory):], ' Accepted')
                unique_indexes.append(i)
            else:
                if verbose == True:
                    print(file_list[i][len(directory):], ' Not accepted')
                pass
        except:
            if verbose == True:
                print(file_list[i][len(directory):], ' Empty')
            pass
    rt_data = pd.concat([data_list[x] for x in unique_indexes])
    return rt_data
    