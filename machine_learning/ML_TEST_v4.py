# -*- coding: utf-8 -*-
"""
Created on Sat Jul 31 00:51:38 2021

@author: alexd
"""

# Use this if nvidia cudas is installed
import os
# os.environ['CUDA_VISIBLE_DEVICES'] = '0' # For GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1' # For CPU
os.environ["SM_FRAMEWORK"] = "tf.keras"

# %%
# from tensorflow import keras
# first neural network with keras tutorial
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LayerNormalization
from keras import models
import matplotlib.pyplot as plt

from tuning_fork import Lorentz_Fitting as LF

import matplotlib as mpl
mpl.rcParams['figure.dpi'] = 288


# %%
points = 25

# define the keras model
def build_model(nodes=250, layers=4):
    model = Sequential()
    model.add(Dense(int(2*points), input_dim=int(2*points), activation='linear'))
    for i in range(layers):
        model.add(Dense(nodes, activation='elu'))
    model.add(Dense(1, activation='linear'))
    return model

def func(x, G, naught=32700, eta=0):
    G = G/2
    if eta > 0:
        return (1 + np.random.uniform(-eta, eta)) * np.divide(G, np.power(x-naught, 2) + G**2)
    else:
        return np.divide(G, np.power(x-naught, 2) + G**2)

def create_data(set_size, data_length=points, seed=10, linspace=True):
    np.random.seed(seed)
    f_0 = 32700
    Gamma = np.random.uniform(low=1, high=100, size=(set_size, 1))
    if linspace==True:
        x_start = np.random.uniform(low=f_0-10*Gamma, high=f_0-1*Gamma)
        x_stop = np.random.uniform(low=f_0+10*Gamma, high=f_0+1*Gamma)
        # x_data = np.sort(np.random.uniform(low=32600, high=32800, size=(set_size, 2)))
        x_data = np.transpose(np.linspace(x_start, x_stop, data_length))
    else:
        x_data = np.sort(np.random.uniform(low=32600, high=32800, size=(set_size, data_length)))
    y_data = func(x_data, Gamma)
    return x_data[0], y_data[0], Gamma

def predict_model(model, x, y, x_norm, y_norm):
    return model.predict((x/x_norm, y/y_norm))
# sample_data = create_data()

def getfilename(directory, file_tag, save_num=0):
    if os.path.isfile(directory+file_tag + '_{:d}'.format(save_num)):
        return getfilename(directory, file_tag, save_num+1)
    return directory+file_tag + '_{:d}'.format(save_num)
norm_constant = 4e4

# %%
load = False
seed = 12
# training data
if load == False:
    
    x_train, y_train, train_targets = create_data(set_size=10000, seed=seed)
    
    # x_train = (x_train-x_train.min())/(x_train.max()-x_train.min())
    x_train = x_train/norm_constant
    # x_train = x_train/x_norm
    # y_train = y_train/y_norm
    
    # split into input (X) and output (y) variables
    X = np.concatenate((x_train, y_train), axis=1)
    y = train_targets
    
    # build model
    model = build_model()
    # compile the keras model
    model.compile(loss='mape', optimizer='adam', metrics=['mape'])
    # fit the keras model on the dataset
    model.fit(X, y, validation_split=0.25, epochs=1000, batch_size=100, verbose=1)
    
    # evaluate the keras model
    # training data
    # x_train, y_train, train_targets, x_norm, y_norm = create_data(set_size=100000, seed=int(time.time()))
    
    # split into input (X) and output (y) variables
    # X = np.concatenate((x_train/norm_constant, y_train), axis=1)
    # y = train_targets
    
    _, metric = model.evaluate(X, y)
    print('MAPE: %.2f' % (metric))

# %%

# model.summary()
    directory = r"models"
    file_tag = r"\{}_{}p_{}seed".format("elu_model", points, seed)
    file_name = getfilename(directory, file_tag)
    model.save(file_name)

# %%
if load == True:
    file_name = r"models\{}_{}p_seed{}".format("elu_model", points, seed)
    
    model = models.load_model(file_name)

# %%
import time

x_data, y_data, Gamma = create_data(set_size=1, seed=int(time.time()))

test_data = np.concatenate((x_data/norm_constant, y_data), axis=1)

prediction = model.predict(test_data)

print('Width = {:.2f}, and prediction = {:.2f}'.format(Gamma[0][0], prediction[0][0]))


# %%

plt.figure()
plt.plot(x_data[0,:], func(x_data[0,:], Gamma[0][0]))
plt.plot(x_data[0,:], func(x_data[0,:], prediction[0][0]))
plt.show()

# %%

class fitting_metrics:
    
    def __init__(self, x_features, G):
        
        self.G = G
        self.mape_points = np.zeros(x_features)
        self.x_count = np.zeros(x_features)
        self.mape_select = []
        
    def update_mape(self, fit_width, x_indices):
        fit_mape = 100*np.abs(self.G-fit_width)/self.G
        for idx in x_indices:
            self.mape_points[idx] += fit_mape
            self.x_count[idx] += 1
            self.mape_select.append(fit_mape)
        
    def output_mape(self):
        self.x_count[self.x_count==0] = 1
        return np.divide(self.mape_points, self.x_count)


# # %%

# """ This section will randomly select 25 x-points from 200 linspace 
#     to input into the network"""
# ratio_set = []

# for G in np.arange(5, 100, 15):
#     num = 10000
    
#     length = 200
    
#     x_values = np.linspace(32600, 32800, length)
    
#     ML_metrics = fitting_metrics(length, G)
    
#     LF_metrics = fitting_metrics(length, G)
    
    
#     for i in range(num):
#         x_select = np.sort(np.random.choice(x_values, points, replace=False))
#         y_select = func(x_select, G=G)
        
#         x_indices = np.where(np.in1d(x_values, x_select))[0]
        
#         guess = [(x_select[-1]+x_select[0])/2, 0, (x_select[-1]-x_select[0])/8, 0, 0, 0]
#         LF_fit = LF.Lorentz_Fit_X(x_select, y_select, guess)
#         LF_metrics.update_mape(LF_fit[0][2]/2, x_indices)
        
#         test_selected_data = np.concatenate((x_select/norm_constant, y_select), axis=0)
#         test_selected_data = test_selected_data.reshape(-1,50)
        
#         ML_prediction = model.predict(test_selected_data)
#         ML_metrics.update_mape(ML_prediction, x_indices)
    
#     ratio_set.append([200/G, ML_metrics.output_mape().mean(), LF_metrics.output_mape().mean()])
#     print("frequency_range/G: ", 200/G)
#     print("ML mape random selection ", ML_metrics.output_mape().mean())
    
#     print("FIT mape random selection ", LF_metrics.output_mape().mean())

# # %%

# fig, ax1 = plt.subplots()
# color = 'tab:blue'
# ml_line, = ax1.plot(np.asarray(ratio_set)[:,0], np.asarray(ratio_set)[:,1], color=color, label="ML MAPE")
# ax1.tick_params(axis='y', labelcolor=color)
# ax1.set_ylabel("Mean Average Percentage Error", color=color)
# color = 'tab:red'
# ax2 = ax1.twinx()
# fit_line, = ax2.plot(np.asarray(ratio_set)[:,0], np.asarray(ratio_set)[:,2], color=color, label="FIT MAPE")
# ax2.tick_params(axis='y', labelcolor=color)
# ax2.set_ylabel("Mean Average Percentage Error", color=color)
# plt.legend(handles = [ml_line, fit_line])
# ax1.set_xlabel('(Max Freq - Min Freq)/Width')
# plt.tight_layout()

# %%

# fig, ax1 = plt.subplots()


# color = 'tab:blue'
# ax1.plot(x_values, ML_metrics.output_mape(), color=color, label="ML MAPE")
# ax1.tick_params(axis='y', labelcolor=color)
# ax1.set_ylabel("Mean Average Percentage Error", color=color)

# color = 'tab:red'
# ax1b = ax1.twinx()
# ax1b.plot(x_values, LF_metrics.output_mape(), color=color, label="FIT MAPE")
# ax1b.tick_params(axis='y', labelcolor=color)
# ax1b.set_ylabel("Mean Average Percentage Error", color=color)

# # color = 'tab:red'
# # ax1.plot(x_values, np.full(x_values.shape, ML_metrics.output_mape().mean()), color=color, linewidth=3.0, label="Average MAPE")
# ax1.set_title("Random Point Subsets of Resonance")

# ax1.set_xlabel("$\mathit{f}$ (Hz)")


# color = 'tab:orange'
# ax2 = ax1.twinx()
# ax2.plot(x_values, func(x_values, G=G), color=color, label="Resonance")
# ax2.set_ylabel("Amplitude", color=color)
# ax2.spines['right'].set_position(("axes", 1.2))
# ax2.tick_params(axis='y', labelcolor=color)
# ax1.legend(loc=2)
# ax2.legend(loc=4)
# ax1b.legend(loc=1)
# plt.tight_layout()
# plt.show()

# # plt.savefig(fname=r"D:\Maglab\Graphs\.png", dpi=150)
    
# # %% 

# """ This section will take 25 x-points and block one of the inputs in order 
#     to see which are the most inportant inputs"""
    
# points = 25
# G = 35
# fineness = 40
# x_range = (32800 - 32600)/fineness

# mape_blocked_difference = np.zeros((fineness, int(2*points)))
# mape_unblocked = np.zeros(fineness)
# mape_blocked = np.zeros((fineness, int(2*points)))

# all_x_points = np.zeros((fineness, int(points)))

# for j in range(fineness):
    
#     x_zero_unblocked = np.sort(np.random.uniform(low=32600, high=32800, size=(int(points))))
#     # x_zero_unblocked = np.linspace(32600+ (j*x_range), 32600 + (j+1)*x_range, points)
#     # x_zero_unblocked = np.linspace(32600 + j*100/fineness/2, 32800 - j*100/fineness/2, points)
#     # x_zero_unblocked = np.linspace(32600 + np.random.rand()*50, 32800 - np.random.rand()*50, points)
#     y_zero_unblocked = func(x_zero_unblocked, G=G)
#     all_x_points[j] = x_zero_unblocked
#     test_data_unblocked = np.concatenate((x_zero_unblocked/norm_constant, y_zero_unblocked), axis=0)
#     test_data_unblocked = test_data_unblocked.reshape(-1,50)
#     prediction_unblocked = model.predict(test_data_unblocked) 
    
#     mape_unblocked[j] = 100 * np.abs(G - prediction_unblocked[0][0])/G
    
#     for i in range(int(2*points)):
#         x_zero_test = x_zero_unblocked.copy()
#         y_zero_test = y_zero_unblocked.copy()
#         if i<25:
#             x_zero_test[i] = 0.0
#         elif i >= 25:
#             y_zero_test[i-25] = 0.0
        
#         test_data_blocked = np.concatenate((x_zero_test/norm_constant, y_zero_test), axis=0)
#         test_data_blocked = test_data_blocked.reshape(-1,50)
         
#         prediction_blocked = model.predict(test_data_blocked)
        
#         mape_blocked[j][i] = 100 * np.abs(G - prediction_blocked[0][0])/G
#         mape_blocked_difference[j][i] = mape_blocked[j][i] - mape_unblocked[j]

# print("mape unblocked: ", mape_unblocked.mean())
# print("mape blocked: ", mape_blocked.mean())

# # %%

# plt.figure()
# plt.tight_layout()
# for idx, x in enumerate(all_x_points):
#     plt.scatter(x, mape_blocked_difference[idx][0:25], s=20, color='blue')
#     plt.scatter(x, mape_blocked_difference[idx][25:50], s=20, color='orange')
# plt.title("MAE blocked - unblocked")
# plt.show()

# # %% 

# """ This section will take 25 x-points and multiply one of the x-y inputs in order 
#     to see which are the most inportant inputs"""

# import time  

# points = 25
# G = 35
# fineness = 40
# x_range = (32800 - 32600)/fineness

# mae_blocked_difference = np.zeros((fineness, points))
# mae_unblocked = np.zeros(fineness)
# mae_blocked = np.zeros((fineness, points))

# all_x_points = np.zeros((fineness, int(points)))

# for j in range(fineness):
    
#     # x_zero_unblocked = np.sort(np.random.uniform(low=32600, high=32800, size=(int(points))))
#     # x_zero_unblocked = np.linspace(32600+ (j*x_range), 32600 + (j+1)*x_range, points)
#     # x_zero_unblocked = np.linspace(32600 + j*100/fineness/2, 32800 - j*100/fineness/2, points)
#     np.random.seed(int(time.time()))
#     time.sleep(1)
#     x_zero_unblocked = np.linspace(32600 + np.random.rand()*50, 32800 - np.random.rand()*50, points)
#     y_zero_unblocked = func(x_zero_unblocked, G=G, rand=False)
#     all_x_points[j] = x_zero_unblocked
#     test_data_unblocked = np.concatenate((x_zero_unblocked/norm_constant, y_zero_unblocked), axis=0)
#     test_data_unblocked = test_data_unblocked.reshape(-1,50)
#     prediction_unblocked = model.predict(test_data_unblocked) 
    
#     mae_unblocked[j] = 100*np.abs(G - prediction_unblocked[0][0])/G
    
#     np.random.seed(15)
#     for i in range(points):
        
#         x_zero_test = x_zero_unblocked.copy()
#         y_zero_test = y_zero_unblocked.copy()
        
#         y_zero_test[i] = (1+0.05*np.random.rand()) * y_zero_test[i]
        
#         test_data_blocked = np.concatenate((x_zero_test/norm_constant, y_zero_test), axis=0)
#         test_data_blocked = test_data_blocked.reshape(-1,50)
         
#         prediction_blocked = model.predict(test_data_blocked)
        
#         mae_blocked[j][i] = 100*np.abs(G - prediction_blocked[0][0])/G
#         mae_blocked_difference[j][i] = mae_blocked[j][i] - mae_unblocked[j]

# print("mape unblocked: ", mae_unblocked.mean())
# print("mape blocked: ", mae_blocked.mean())

# # %%

# plt.figure()
# plt.tight_layout()
# for idx, x in enumerate(all_x_points):
#     plt.scatter(x, mae_blocked_difference[idx], s=20, color='blue')
#     # plt.scatter(x, mae_blocked_difference[idx][25:50], s=20, color='orange')
# plt.title("MAPE blocked - unblocked")
# plt.show()

# %%

""" This section will randomly select 25 x-points from 200 linspace 
    to input into the network"""


ml_avg_hist = []

plot_ML = True
plot_FIT = False

fig, ax1 = plt.subplots()
if plot_ML == True:
    ax1.tick_params(axis='y')
    ax1.set_ylabel("Mean Average Percentage Error")
    if plot_FIT == True:
        color = 'tab:red'
        ax2 = ax1.twinx()
        # fit_line, = ax2.plot(200/np.asarray(ratio_set)[:,0], np.asarray(ratio_set)[:,2], color=color, label="FIT MAPE")
        ax2.tick_params(axis='y', labelcolor=color)
        ax2.set_ylabel("Mean Average Percentage Error")
        # plt.legend(handles = [ml_line, fit_line])
        
# ax1.set_xlabel('(Max Freq - Min Freq)/Width')
ax1.set_xlabel('Width')
ax1.set_title("MAPE vs Width (zero noise)")

for freq_range in range(1, 20):
    ratio_set = []
    fit_hist = []
    for G in np.arange(1, 100, 0.1):
    
        # G = 25
        num = 1
        length = points
        # length = 200
        eta = 0.0
        
        x_values = np.linspace(32700-freq_range*G, 32700+freq_range*G, length)
        
        ML_metrics = fitting_metrics(length, G)
        
        LF_metrics = fitting_metrics(length, G)
        
        
        for i in range(num):
            if i % 10 == 0:
                print("\rnum: %i   " % i, end="")
                # sys.stdout.write("\rnum: %i" % i)
                # sys.stdout.flush()
            if length == points:
                x_select = x_values
            elif length > points:
                x_select = np.sort(np.random.choice(x_values, points, replace=False))
            y_select = func(x_select, G=G, eta=eta)
            
            x_indices = np.where(np.in1d(x_values, x_select))[0]
            
            guess = [(x_select[-1]+x_select[0])/2, 0, (x_select[-1]-x_select[0])/8, 0, 0, 0]
            LF_fit = LF.Lorentz_Fit_X(x_select, y_select, guess)
            LF_metrics.update_mape(np.abs(LF_fit[0][2]), x_indices)
            fit_hist.append(LF_fit[0])
            
            test_selected_data = np.concatenate((x_select/norm_constant, y_select), axis=0)
            test_selected_data = test_selected_data.reshape(-1,50)
            
            ML_prediction = model.predict(test_selected_data)
            ML_metrics.update_mape(ML_prediction, x_indices)
        
        ratio_set.append([200/G, ML_metrics.output_mape().mean(), LF_metrics.output_mape().mean()])
    
    ml_avg_hist.append(np.mean(np.asarray(ratio_set)[:,1]))
        # print("frequency_range/G: ", 200/G)
        # print("ML mape random selection ", ML_metrics.output_mape().mean())
        
        # print("FIT mape random selection ", LF_metrics.output_mape().mean())
    ax1.plot(200/np.asarray(ratio_set)[:,0], np.asarray(ratio_set)[:,1])

# %%

plt.figure()
plt.plot(range(1, 20), ml_avg_hist)


# %%


for j in range(1):
    
    G = 25
    num = 1000
    length = points
    length = 200
    eta = 0.0
    
    x_values = np.linspace(32600, 32800, length)
    
    ML_metrics = fitting_metrics(length, G)
    
    LF_metrics = fitting_metrics(length, G)
    
    
    for i in range(num):
        if i % 10 == 0:
            print("\rnum: ", i, end="\r")
            # sys.stdout.write("\rnum: %i" % i)
            # sys.stdout.flush()
        if length == points:
            x_select = x_values
        elif length > points:
            x_select = np.sort(np.random.choice(x_values, points, replace=False))
        y_select = func(x_select, G=G, eta=eta)
        
        x_indices = np.where(np.in1d(x_values, x_select))[0]
        
        guess = [(x_select[-1]+x_select[0])/2, 0, (x_select[-1]-x_select[0])/8, 0, 0, 0]
        LF_fit = LF.Lorentz_Fit_X(x_select, y_select, guess)
        LF_metrics.update_mape(np.abs(LF_fit[0][2]), x_indices)
        fit_hist.append(LF_fit[0])
        
        test_selected_data = np.concatenate((x_select/norm_constant, y_select), axis=0)
        test_selected_data = test_selected_data.reshape(-1,50)
        
        ML_prediction = model.predict(test_selected_data)
        ML_metrics.update_mape(ML_prediction, x_indices)
    
    # ratio_set.append([200/G, ML_metrics.output_mape().mean(), LF_metrics.output_mape().mean()])
    # print("frequency_range/G: ", 200/G)
    # print("ML mape random selection ", ML_metrics.output_mape().mean())

# %%

plot_ML = True
plot_FIT = True

fig, ax1 = plt.subplots()

if plot_ML == True:
    color = 'tab:blue'
    ML_line, = ax1.plot(x_values, ML_metrics.output_mape(), color=color, label="ML MAPE")
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_ylabel("Mean Average Percentage Error", color=color)

if plot_FIT == True:
    color = 'tab:red'
    ax1b = ax1.twinx()
    FIT_line, = ax1b.plot(x_values, LF_metrics.output_mape(), color=color, label="FIT MAPE")
    ax1b.tick_params(axis='y', labelcolor=color)
    ax1b.set_ylabel("Mean Average Percentage Error", color=color)

# color = 'tab:red'
# ax1.plot(x_values, np.full(x_values.shape, ML_metrics.output_mape().mean()), color=color, linewidth=3.0, label="Average MAPE")
ax1.set_title("Random Point Subsets of Resonance")

ax1.set_xlabel("$\mathit{f}$ (Hz)")


color = 'tab:orange'
ax2 = ax1.twinx()
resonance_line, = ax2.plot(x_values, func(x_values, G=G), color=color, label="Resonance")
ax2.set_ylabel("Amplitude", color=color)
ax2.spines['right'].set_position(("axes", 1.2))
ax2.tick_params(axis='y', labelcolor=color)
plt.legend(handles=[ML_line, FIT_line, resonance_line])
plt.tight_layout()

# # plt.savefig(fname=r"D:\Maglab\Graphs\.png", dpi=150)

# %% 

# fit_hist = np.array(fit_hist)

# fig, ax = plt.subplots(3,1)
# for i, subplot in enumerate(ax):
#     subplot.plot(np.arange(20, 100, 0.1), fit_hist[:, i])
