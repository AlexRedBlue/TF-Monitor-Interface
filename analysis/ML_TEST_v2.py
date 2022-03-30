# -*- coding: utf-8 -*-
"""
Created on Fri Jul 30 23:24:01 2021

@author: alexd
"""

import numpy as np
import matplotlib.pyplot as plt

class network:
    def __init__(self, input_size):
        self.input_size = input_size
        self.layers = list()
        self.weights = list()
        
    def add_dense_layer(self, nodes):
        if len(self.layers) == 0:
            self.weights.append(np.random.rand(nodes, self.input_size))
        else:
            self.weights.append(np.random.rand(nodes, self.layers[-1].nodes))
        self.layers.append(self.layer(nodes))
        
        
    def output(self, inputs):
        outputs = inputs
        for idx, weights in enumerate(self.weights):
            outputs = self.layers[idx].propagate_forward(outputs, weights)
        return outputs
        

    def train_network(self, training_set, target_set):
        for idx, data in enumerate(training_set):
            network_output = self.output(data)
            expected = target_set[idx]
            error = expected - network_output
            if error > 0.1:
                for i in range(len(self.weights)):
                    self.weights[i] = np.random.rand(*np.shape(self.weights[i]))
                
                
        
    class layer:
        def __init__(self, nodes):
            self.nodes = nodes
            self.last_output = None
            
        def reLU_activation(self, x):
            return x if x > 0 else 0
        
        def propagate_forward(self, inputs, weights):
            output = np.mean(np.multiply(inputs, weights), axis=1)
            self.last_output = output
            return output
        
        def back_propagate(self):
            pass
        
test = network(50)
test.add_dense_layer(10)
test.add_dense_layer(1)

set_size = 100

train_targets = np.random.uniform(low=1.0, high=4, size=(set_size, 1))
x_test = np.random.uniform(low=0.0, high=4*np.pi, size=(set_size, 25))
y_test = np.sin(train_targets * x_test)

train_data = np.concatenate((x_test, y_test), axis=1)

test.train_network(train_data, train_targets)

test_data = np.random.uniform(low=0.0, high=4*np.pi, size=(1, 25))
test_data = np.concatenate((test_data, np.sin(2.5*test_data)), axis=1)

print(test.output(test_data))


