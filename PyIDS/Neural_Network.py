import numpy as np
import h5py

class Neural_Network(object):
    def __init__(self, inSize, hid1Size, hid2Size, outSize):
        self.inputLayerSize = inSize
        self.hiddenLayer1Size = hid1Size
        self.hiddenLayer2Size = hid2Size
        self.outputLayerSize = outSize

        self.trainingIterations = 500

        # Weights
        self.syn0 = 2*np.random.random((self.inputLayerSize, self.hiddenLayer1Size)) - 1
        self.syn1 = 2*np.random.random((self.hiddenLayer1Size, self.hiddenLayer2Size)) - 1
        self.syn2 = 2*np.random.random((self.hiddenLayer2Size, self.outputLayerSize)) - 1

    def saveWeights(self, filename):
        h5f = h5py.File(filename, 'w')
        h5f.create_dataset('syn0', data=self.syn0)
        h5f.create_dataset('syn1', data=self.syn1)
        h5f.create_dataset('syn2', data=self.syn2)
        h5f.close()

    def loadWeights(self, filename):
        h5f = h5py.File(filename, 'r')
        self.syn0 = h5f['syn0'][:]
        self.syn1 = h5f['syn1'][:]
        self.syn2 = h5f['syn2'][:]
        h5f.close()


    def sigmoid(self, x, prime = False):
        x = np.around(x, decimals = 8)
        if(prime==True):
            return x*(1-x)
        return 1/(1+np.exp(-x))


    def train(self, trainingData, trainingAnswers, accuracy=90):
        
        currentAccuracy = 0
        currentIteration = 0
        maxIterations = 20

        # input dataset
        X = trainingData
 
        # correct answer dataset           
        y = trainingAnswers

        # train the neural net until accuracy or max iterations are met
        while currentAccuracy <= accuracy and currentIteration <= maxIterations:

            np.random.seed(currentIteration)

            # Reset the weights in case we were in a relative min
            self.syn0 = 2*np.random.random((self.inputLayerSize, self.hiddenLayer1Size)) - 1
            self.syn1 = 2*np.random.random((self.hiddenLayer1Size, self.hiddenLayer2Size)) - 1
            self.syn2 = 2*np.random.random((self.hiddenLayer2Size, self.outputLayerSize)) - 1
    
            for iter in range(self.trainingIterations):
                # forward propagation
                input_layer = X
                hidden_layer1 = self.sigmoid(np.dot(input_layer,self.syn0))
                hidden_layer2 = self.sigmoid(np.dot(hidden_layer1,self.syn1))
                output_layer = self.sigmoid(np.dot(hidden_layer2,self.syn2))
 
                # determine output layer error value
                ol_error = y - output_layer
 
                # slope of the sigmoid at the values in output layer
                ol_delta = np.multiply(ol_error, self.sigmoid(output_layer,True))


                # determine hidden layer error value
                hl2_error = ol_delta.dot(self.syn2.T)

                # get the slope of the sigmoid at the values in the hidden layer
                hl2_delta = np.multiply(hl2_error, self.sigmoid(hidden_layer2, True))


                # determine hidden layer error value
                hl1_error = hl2_delta.dot(self.syn1.T)

                # get the slope of the sigmoid at the values in the hidden layer
                hl1_delta = np.multiply(hl1_error, self.sigmoid(hidden_layer1, True))
 

                # update weights
                self.syn0 += input_layer.T.dot(hl1_delta)
                self.syn1 += hidden_layer1.T.dot(hl2_delta)
                self.syn2 += hidden_layer2.T.dot(ol_delta)

            currentIteration += 1

            # Check accuracy of the neural network
            correct = 0
            total = 0
            for num, item in enumerate(output_layer, 0):
                ans = str(y[num][0])
        
                if str(np.around(item[0], 0)) == str(ans):
                    correct += 1
        
                total += 1
            currentAccuracy = np.around((correct/(total)) * 100, 2)
        
        return output_layer


    def compute(self, INPUT):
        input_layer = INPUT
        hidden_layer1 = self.sigmoid(np.dot(input_layer,self.syn0))
        hidden_layer2 = self.sigmoid(np.dot(hidden_layer1,self.syn1))
        output_layer = self.sigmoid(np.dot(hidden_layer2,self.syn2))
        return output_layer