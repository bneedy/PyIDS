import numpy as np

class Neural_Network(object):
    def __init__(self):
        self.inputLayerSize = 3
        self.hiddenLayer1Size = 10
        self.hiddenLayer2Size = 5
        self.outputLayerSize = 1

        self.levelOfTrain = 60000

        self.MAX = np.array(self.inputLayerSize)

        np.random.seed(1)

        # Weights
        self.syn0 = np.random.randn(self.inputLayerSize, self.hiddenLayer1Size)
        self.syn1 = np.random.randn(self.hiddenLayer1Size, self.hiddenLayer2Size)
        self.syn2 = np.random.randn(self.hiddenLayer2Size, self.outputLayerSize)

        self.train()

    def sigmoid(self, x, deriv = False):
        if(deriv==True):
            return x*(1-x)
        return 1/(1+np.exp(-x))

    def train(self):
        # input dataset
        X = np.array([  [0,0,5],
                        [0,2,1],
                        [3,0,3],
                        [8,0,1],
                        [3,1,3],
                        [2,2,3],
                        [1,1,7],
                        [3,1,3],
                        [3,1,3],
                        [3,1,3] ])

        self.MAX = np.amax(X, axis = 0)
        X = X/self.MAX
 
        # output dataset           
        y = np.array([[0],[1],[1],[0],[0],[1],[0],[1],[1],[1]])

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

        for item in (output_layer):
            print(round(item[0], 4))


    def compute(self, INPUT):
        input_layer = INPUT/self.MAX
        hidden_layer1 = self.sigmoid(np.dot(input_layer,self.syn0))
        hidden_layer2 = self.sigmoid(np.dot(hidden_layer1,self.syn1))
        output_layer = self.sigmoid(np.dot(hidden_layer2,self.syn2))
        return output_layer
