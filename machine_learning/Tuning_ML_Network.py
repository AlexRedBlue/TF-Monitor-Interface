# -*- coding: utf-8 -*-
"""
Created on Mon Aug 30 16:12:59 2021

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
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras import optimizers
from keras import models
import matplotlib.pyplot as plt

from scipy import optimize


# %%

def func(f, G, naught=32700, rand=False):
    if rand == True:
        return (1 + 0.05*np.random.rand()) * np.divide(G, np.power(f-naught, 2) + G**2)
    else:
        return np.divide(G, np.power(f-naught, 2) + G**2)

points = 25

# %%

""" Custom Loss Function """

# y_actual = [x,y] values
# y_prediction = [gamma]

def least_sq_error(y_true, y_pred):
    print(y_true.numpy().shape, y_pred.numpy().shape)
    f = y_true.numpy()[0, :points]
    amp = y_true.numpy()[0, points:]
    gamma = y_pred.numpy()[0,0]
    amp_prediciton = func(f, gamma)
    return np.mean(np.power((amp - amp_prediciton), 2))
    

# %%

""" Load/Create Model """

points = 32

def build_model(nodes=64, layers=3):
    # model type
    model = Sequential()
    
    # input layer
    model.add(Dense(int(nodes), input_dim=int(2*points), activation='linear'))
    
    # hidden layers
    for i in range(layers-1):
        model.add(Dense(int(nodes/(i+1)), activation='elu'))
        model.add(Dropout(0.01))
        
    # output layer
    model.add(Dense(2, activation='linear'))
    
    return model

model = build_model()
# model.compile(optimizer='adam', loss=least_sq_error, run_eagerly=True)
model.compile(optimizer='adam', loss="mape", metrics=['mape', 'accuracy'])


# Save and load models using the following

# file_name = r"machine_learning\models\{}".format("elu_model")

# model.save(file_name)

# model = models.load_model(file_name)

# %%

""" Train Model """

def create_data(set_size=10000, data_length=points, seed=10):
    np.random.seed(seed)
    Gamma = np.random.uniform(low=1, high=100, size=(set_size, 1))
    f_0 = np.random.uniform(low=32600, high=32750, size=(set_size, 1))
    x_data = np.sort(np.random.uniform(low=32500, high=32850, size=(set_size, data_length)))
    y_data = func(x_data, Gamma, f_0)
    return x_data, y_data, Gamma, f_0

norm_constant = 32700.
x_train, y_train, Gamma_target, f_0_target = create_data()
X = np.concatenate((x_train/norm_constant, y_train), axis=1)
# X = np.concatenate((x_train/norm_constant, y_train, np.multiply(x_train/norm_constant, y_train)), axis=1)
y = np.concatenate((Gamma_target, f_0_target/norm_constant), axis=1)

# print(least_sq_error(X[0,:], y[0]))

history = model.fit(X, y, validation_split=0.33, epochs=19000, batch_size=1000, verbose=1)

# %%
""" Metrics """

plt.figure()
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])

# %%

# 0: Gamma, 1: f_0
def lorentzian_func(f, G, naught):
    return np.divide(G, np.power(f-naught, 2) + G**2)

""" Compare Model to fit """
param_0 = [50, 32700]

fit = optimize.curve_fit(lorentzian_func, x_train[0,:], y_train[0,:], p0=param_0)
model_prediction = model(X[0, :].reshape((1,int(2*points))))

print("Real G: {}, f_0: {}".format(Gamma_target[0][0], f_0_target[0][0]))
print("fit  G: {}, f_0: {}".format(fit[0][0], fit[0][1]))
print("NN   G: {}, f_0: {}".format(model_prediction[0][0], model_prediction[0][1]*norm_constant))



# %%

""" Save Model """

file_name = r"machine_learning\models\{}".format("improved_elu_model_2")

model.save(file_name)