import Neural_Network as NN
import Data_Reader as DR
import numpy as np

dr = DR.Data_Reader()

#dr.read_dataTypes_file()

rsp1 = -1
nn = NN.Neural_Network()
while (int(rsp1) != -1):
    rsp1 = input("Please enter first value: ")
    rsp2 = input("Please enter second value: ")
    rsp3 = input("Please enter third value: ")

    #try:
    X = np.array([[int(rsp1), int(rsp2), int(rsp3)]])

    print("Here is your answer...")
    for item in (nn.compute(X)):
        print(round(item[0], 4))
    #except:
    #    quit()