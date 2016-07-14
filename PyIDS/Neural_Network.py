import numpy as np

class Neural_Network(object):
    def __init__(self, inSize, hid1Size, hid2Size, outSize):
        self.inputLayerSize = inSize
        self.hiddenLayer1Size = hid1Size
        self.hiddenLayer2Size = hid2Size
        self.outputLayerSize = outSize

        self.levelOfTrain = 10000

        self.set_answer_list = []

        np.random.seed(1)

        # Weights
        self.syn0 = np.random.randn(self.inputLayerSize, self.hiddenLayer1Size)
        self.syn1 = np.random.randn(self.hiddenLayer1Size, self.hiddenLayer2Size)
        self.syn2 = np.random.randn(self.hiddenLayer2Size, self.outputLayerSize)

    def set_answer_list(self, answerList):
        self.set_answer_list = answerList

    def sigmoid(self, x, deriv = False):
        if(deriv==True):
            return x*(1-x)
        return 1/(1+np.exp(-x))

    def train(self, trainingData, trainingAnswers):
        # input dataset
        X = trainingData
 
        # correct answer dataset           
        y = trainingAnswers

        # train the neural net
        for iter in range(self.levelOfTrain):
    
            # forward propagation
            input_layer = X
            hidden_layer1 = self.sigmoid(np.dot(input_layer,self.syn0))
            hidden_layer2 = self.sigmoid(np.dot(hidden_layer1,self.syn1))
            output_layer = self.sigmoid(np.dot(hidden_layer2,self.syn2))
 
            # determine output layer error value
            ol_error = y - output_layer
 
            # slope of the sigmoid at the values in output layer
            ol_delta = ol_error * self.sigmoid(output_layer,True)



            # determine hidden layer error value
            hl2_error = ol_delta.dot(self.syn2.T)

            # get the slope of the sigmoid at the values in the hidden layer
            hl2_delta = hl2_error * self.sigmoid(hidden_layer2, True)



            # determine hidden layer error value
            hl1_error = hl2_delta.dot(self.syn1.T)

            # get the slope of the sigmoid at the values in the hidden layer
            hl1_delta = hl1_error * self.sigmoid(hidden_layer1, True)
 


            # update weights
            self.syn0 += input_layer.T.dot(hl1_delta)
            self.syn1 += hidden_layer1.T.dot(hl2_delta)
            self.syn2 += hidden_layer2.T.dot(ol_delta)

        return output_layer


    def compute(self, INPUT):
        input_layer = INPUT
        hidden_layer1 = self.sigmoid(np.dot(input_layer,self.syn0))
        hidden_layer2 = self.sigmoid(np.dot(hidden_layer1,self.syn1))
        output_layer = self.sigmoid(np.dot(hidden_layer2,self.syn2))
        return output_layer
