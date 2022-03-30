# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 15:05:33 2021

@author: physics-svc-mkdata
"""

import numpy as np
import matplotlib.pyplot as plt      

class Neural_Network:
    def __init__(self, input_nodes):
        self.first_layer = self.input_layer(input_nodes=input_nodes)
        self.layers = [self.first_layer]
        self.weights = []
        self.error_history = []
        
    def add_dense_layer(self, nodes):
        self.layers.append(self.dense_layer(nodes, previous_layer_length=self.layers[len(self.layers)-1].nodes))
        self.weights.append({'layer {} weights'.format(len(self.layers)-1): [np.random.rand(nodes, self.layers[len(self.layers)-2].nodes)]})
        
    def transfer_derivative(self, output):
        return 0 if output == 0 else 1
    
    def output(self, input_data):
        for idx, layer in enumerate(self.layers):
            if idx == 0:
                output = layer.output(input_data=input_data)
            else:
                # print(self.weights[idx-1])
                output = layer.output(input_data=output, layer_weights=self.weights[idx-1]['layer {} weights'.format(idx)])
        return output
    
    def train_network(self, train_data, target_data):
        for idx, example in enumerate(train_data):
            self.output(train_data)
            expected = []
            errors = []
            for i in reversed(range(len(self.layers))):
                if i == len(self.layers) - 1:
                    expected.append([target_data[idx]])
                    errors.append(expected[-1] - self.layers[-1].last_output)
                else:
                    expected.append(np.divide(np.transpose(expected[-1]), self.weights[i]['layer {} weights'.format(i+1)][0]))
                    errors.append(expected[-1] - self.layers[i].last_output)
                    # print(expected[-1])
                    # print(errors[-1])
                    
            for j in reversed(range(len(self.weights))):
                weight_layer_name = 'layer {} weights'.format(j+1)
                self.weights[j][weight_layer_name] = (self.weights[j][weight_layer_name] - errors[j+1])
                
    def backward_propagate_error(self, network, expected):
    	for i in reversed(range(len(network))):
    		layer = network[i]
    		errors = list()
    		if i != len(network)-1:
    			for j in range(len(layer)):
    				error = 0.0
    				for neuron in network[i + 1]:
    					error += (neuron['weights'][j] * neuron['delta'])
    				errors.append(error)
    		else:
    			for j in range(len(layer)):
    				neuron = layer[j]
    				errors.append(expected[j] - neuron['output'])
    		for j in range(len(layer)):
    			neuron = layer[j]
    			neuron['delta'] = errors[j]
                
            
    
    class input_layer:
        def __init__(self, input_nodes):
            self.nodes = input_nodes
            self.last_output = []
        
        def output(self, input_data):
            layer_output = np.zeros(self.nodes)
            start = int((len(input_data) - self.nodes)/2)
            points = np.ceil(len(input_data)/self.nodes)
            for idx, val in enumerate(layer_output):
                if int(start + idx - points/2) < 0:
                    begin = 0
                else:
                    begin = int(start + idx - points/2)
                if int(start + points/2 + idx + 1):
                    end = int(start + points/2 + idx + 1)
                else:
                    end = -1
                layer_output[idx] = np.mean(input_data[begin:end])
                # print(values[idx])
            self.last_output = layer_output
            return layer_output
                
    class dense_layer:
        def __init__(self, nodes, previous_layer_length):
            self.nodes = nodes
            self.last_output = []
            
        def relu(self, x):
            return 0 if x < 0 else x
            
        def output(self, input_data, layer_weights):
            layer_output = np.zeros(self.nodes)
            for idx, node_weights in enumerate(layer_weights):
                layer_output[idx] = self.relu(np.multiply(input_data, node_weights).mean())
            self.last_output = layer_output
            return layer_output
        
    
 
# %%
ML_TEST = Neural_Network(input_nodes=100)
ML_TEST.add_dense_layer(nodes=50)
ML_TEST.add_dense_layer(nodes=25)
ML_TEST.add_dense_layer(nodes=10)
ML_TEST.add_dense_layer(nodes=1)

initial_layers = ML_TEST.layers
initial_weights = ML_TEST.weights

# %%

training_length = 1000
train_data = []
train_targets = np.random.uniform(low=1, high=2, size=(training_length,))

for idx, w in enumerate(train_targets):
    train_x = np.random.uniform(low=0, high=4*np.pi, size=(50,))
    train_y = np.sin(w*train_x)
    train_data.append(np.concatenate((train_x,train_y)))
    
ML_TEST.train_network(train_data, train_targets)
final_layers = ML_TEST.layers
final_weights = ML_TEST.weights

# %%

test_length = 100
test_data = []
test_targets = np.random.uniform(low=1, high=2, size=(100,))

for idx, w in enumerate(test_targets):
    test_x = np.random.uniform(low=0, high=4*np.pi, size=(50,))
    test_y = np.sin(w*train_x)
    test_data.append(np.concatenate((test_x,test_y)))


answers = []

for idx, target in enumerate(test_targets):
    answers.append([ML_TEST.output(test_data[idx])[0], target])

errors = []
for idx, [answer, target] in enumerate(answers):
    errors.append((answer-target)**2)
mse = np.mean(errors)
    
print(mse)

# %%
x = range(len(ML_TEST.error_history))
y = np.power(ML_TEST.error_history, 2)
plt.figure()
plt.plot(x,y)



            
