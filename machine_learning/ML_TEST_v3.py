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

load = True

# %%
# from tensorflow import keras
# first neural network with keras tutorial
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from keras import models
import matplotlib.pyplot as plt

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

def func(x, G, naught=32700, rand=True):
    if rand == True:
        return (1 + 0.05*np.random.rand()) * np.divide(G, np.power(x-naught, 2) + G**2)
    else:
        return np.divide(G, np.power(x-naught, 2) + G**2)

def create_data(set_size=10000, data_length=points, seed=10):
    np.random.seed(seed)
    Gamma = np.random.uniform(low=1, high=100, size=(set_size, 1))
    x_data = np.sort(np.random.uniform(low=32600, high=32800, size=(set_size, data_length)))
    y_data = func(x_data, Gamma)
    return x_data, y_data, Gamma


norm_constant = 32700.

# %%

# training data

x_train, y_train, train_targets = create_data()

x_train = x_train/norm_constant

# split into input (X) and output (y) variables
X = np.concatenate((x_train, y_train), axis=1)
y = train_targets

# build model
# model = build_model()
# compile the keras model



# model.summary()

# %%
if load == False:
    
    model = build_model()
    _, metric = model.evaluate(X, y)
    print('MAPE: %.2f' % (metric))
    
    model.compile(loss='mape', optimizer='adam', metrics=['mape'])
    # fit the keras model on the dataset
    model.fit(X, y, epochs=150, batch_size=10, verbose=1)
    
    # evaluate the keras model
    # training data
    x_train, y_train, train_targets = create_data()
    
    # split into input (X) and output (y) variables
    X = np.concatenate((x_train/norm_constant, y_train), axis=1)
    y = train_targets
    
    file_name = r"machine_learning\models\{}".format("elu_model")
    
    model.save(file_name)

# %%
if load == True:
    file_name = r"machine_learning\models\{}".format("elu_model")
    file_name = r"C:\Users\alexd\Documents\GitHub\data-monitoring\machine_learning\models\elu_model"
    
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

""" This section will randomly select 25 x-points from 200 linspace 
    to input into the network"""

num = 10000
G = 25

x_values = np.linspace(32600, 32800, 200)
ae_set = np.zeros(len(x_values))
ae_num = np.zeros(len(x_values))

mape_select = np.zeros(num)


for i in range(num):
    x_select = np.sort(np.random.choice(x_values, points, replace=False))
    y_select = func(x_select, G=G)
    test_selected_data = np.concatenate((x_select/norm_constant, y_select), axis=0)
    test_selected_data = test_selected_data.reshape(-1,50)
    prediction = model.predict(test_selected_data)
    mape_select[i] = 100 * np.abs(G - prediction[0][0])/G
    for idx, val in enumerate(x_select):
        index = [x_values==val]
        ae_set[index[0]] = ae_set[index[0]] + mape_select[i]
        ae_num[index[0]] = ae_num[index[0]] + 1

ae_num[ae_num==0] = 1
ae_set = np.divide(ae_set, ae_num)
print("mape random selection ", mape_select.mean())
print("mape for selection ", ae_set.mean())

# %%

plt.figure()
plt.plot(x_values, ae_set)
plt.title("mape of point randomly selected: {} choices".format(num))
plt.show()

    
# %% 

""" This section will take 25 x-points and block one of the inputs in order 
    to see which are the most inportant inputs"""
    
points = 25
G = 35
fineness = 40
x_range = (32800 - 32600)/fineness

mae_blocked_difference = np.zeros((fineness, int(2*points)))
mae_unblocked = np.zeros(fineness)
mae_blocked = np.zeros((fineness, int(2*points)))

all_x_points = np.zeros((fineness, int(points)))

for j in range(fineness):
    
    x_zero_unblocked = np.sort(np.random.uniform(low=32600, high=32800, size=(int(points))))
    # x_zero_unblocked = np.linspace(32600+ (j*x_range), 32600 + (j+1)*x_range, points)
    # x_zero_unblocked = np.linspace(32600 + j*100/fineness/2, 32800 - j*100/fineness/2, points)
    # x_zero_unblocked = np.linspace(32600 + np.random.rand()*50, 32800 - np.random.rand()*50, points)
    y_zero_unblocked = func(x_zero_unblocked, G=G)
    all_x_points[j] = x_zero_unblocked
    test_data_unblocked = np.concatenate((x_zero_unblocked/norm_constant, y_zero_unblocked), axis=0)
    test_data_unblocked = test_data_unblocked.reshape(-1,50)
    prediction_unblocked = model.predict(test_data_unblocked) 
    
    mae_unblocked[j] = 100 * np.abs(G - prediction_unblocked[0][0])/G
    
    for i in range(int(2*points)):
        x_zero_test = x_zero_unblocked.copy()
        y_zero_test = y_zero_unblocked.copy()
        if i<25:
            x_zero_test[i] = 0.0
        elif i >= 25:
            y_zero_test[i-25] = 0.0
        
        test_data_blocked = np.concatenate((x_zero_test/norm_constant, y_zero_test), axis=0)
        test_data_blocked = test_data_blocked.reshape(-1,50)
         
        prediction_blocked = model.predict(test_data_blocked)
        
        mae_blocked[j][i] = 100 * np.abs(G - prediction_blocked[0][0])/G
        mae_blocked_difference[j][i] = mae_blocked[j][i] - mae_unblocked[j]

print("mae unblocked: ", mae_unblocked.mean())
print("mae blocked: ", mae_blocked.mean())

# %%

plt.figure()
for idx, x in enumerate(all_x_points):
    plt.scatter(x, mae_blocked_difference[idx][0:25], s=20, color='blue')
    plt.scatter(x, mae_blocked_difference[idx][25:50], s=20, color='orange')
plt.title("MAE blocked - unblocked")
plt.show()

# %% 

""" This section will take 25 x-points and multiply one of the x-y inputs in order 
    to see which are the most inportant inputs"""

import time  

points = 25
G = 35
fineness = 40
x_range = (32800 - 32600)/fineness

mae_blocked_difference = np.zeros((fineness, points))
mae_unblocked = np.zeros(fineness)
mae_blocked = np.zeros((fineness, points))

all_x_points = np.zeros((fineness, int(points)))

for j in range(fineness):
    
    # x_zero_unblocked = np.sort(np.random.uniform(low=32600, high=32800, size=(int(points))))
    # x_zero_unblocked = np.linspace(32600+ (j*x_range), 32600 + (j+1)*x_range, points)
    # x_zero_unblocked = np.linspace(32600 + j*100/fineness/2, 32800 - j*100/fineness/2, points)
    np.random.seed(int(time.time()))
    time.sleep(1)
    x_zero_unblocked = np.linspace(32600 + np.random.rand()*50, 32800 - np.random.rand()*50, points)
    y_zero_unblocked = func(x_zero_unblocked, G=G, rand=False)
    all_x_points[j] = x_zero_unblocked
    test_data_unblocked = np.concatenate((x_zero_unblocked/norm_constant, y_zero_unblocked), axis=0)
    test_data_unblocked = test_data_unblocked.reshape(-1,50)
    prediction_unblocked = model.predict(test_data_unblocked) 
    
    mae_unblocked[j] = 100*np.abs(G - prediction_unblocked[0][0])/G
    
    np.random.seed(15)
    for i in range(points):
        
        x_zero_test = x_zero_unblocked.copy()
        y_zero_test = y_zero_unblocked.copy()
        
        y_zero_test[i] = (1+0.05*np.random.rand()) * y_zero_test[i]
        
        test_data_blocked = np.concatenate((x_zero_test/norm_constant, y_zero_test), axis=0)
        test_data_blocked = test_data_blocked.reshape(-1,50)
         
        prediction_blocked = model.predict(test_data_blocked)
        
        mae_blocked[j][i] = 100*np.abs(G - prediction_blocked[0][0])/G
        mae_blocked_difference[j][i] = mae_blocked[j][i] - mae_unblocked[j]

print("mape unblocked: ", mae_unblocked.mean())
print("mape blocked: ", mae_blocked.mean())

# %%

plt.figure()
for idx, x in enumerate(all_x_points):
    plt.scatter(x, mae_blocked_difference[idx], s=20, color='blue')
    # plt.scatter(x, mae_blocked_difference[idx][25:50], s=20, color='orange')
plt.title("MAPE blocked - unblocked")
plt.show()





