import Neural_Network as NN
import Data_Reader as DR
import numpy as np


dataTypesFile = "dataTypesFile.txt"
dataFile = "tmpMsg2.txt"

dr = DR.Data_Reader()
print("Reading Data Files...")
dr.readDataFiles(dataTypesFile, dataFile)

print("Getting Data...")
data, answers, ansKey = dr.get_data_array()

print("Starting Neural Network...")
nn = NN.Neural_Network(int(data[0].size),14,9,1)

print("Beginning training...")
nn.train(data,answers)

print("Computing...")
output = nn.compute(data)

f = open("results.txt", 'w')
right = 0
wrong = 0
for num, item in enumerate(output, 0):
    ans = str(answers[num][0])
    f.write("Output: " + str(np.around(item[0], 0)) + " - real: " + str(ans) + " type: " + ansKey[num] + "\n")
    print("Output: " + str(np.around(item[0], 0)) + " - real: " + str(ans) + " type: " + ansKey[num] + "\n")
    if str(np.around(item[0], 0)) == str(ans):
        right = right + 1
    else:
        wrong = wrong + 1

f.write("Correct/Total: " + str(right) + "/" + str(right+wrong) + " = " + str(np.around(right/(right+wrong) * 100, 2)) + "%")
print("Correct/Total: " + str(right) + "/" + str(right+wrong) + " = " + str(np.around(right/(right+wrong) * 100, 2)) + "%")

f.close()