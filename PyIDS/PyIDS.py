import Neural_Network as NN
import Data_Reader as DR
import numpy as np


dataTypesFile = "dataTypesFile.txt"
dataFile = "tmpMsg2.txt"

dr = DR.Data_Reader()
print("Reading Data Files...")
dr.readDataFiles(dataTypesFile, dataFile)

print("Getting small dataset...")
data, answers, ansKey = dr.get_data_array(True)

print("Starting Neural Network...")
nn = NN.Neural_Network(int(data[0].size),14,9,1)

#f = open("results_1_new.txt", 'w')

print("Beginning training...")
nn.train(data,answers)

print("Computing small dataset...")
output = nn.compute(data)

right = 0
total = 0
for num, item in enumerate(output, 0):
    ans = str(answers[num][0])
    #f.write("Output: " + str(np.around(item[0], 0)) + " - real: " + str(ans) + " type: " + ansKey[num] + "\n")
    print("Output: " + str(np.around(item[0], 0)) + " - real: " + str(ans) + " type: " + ansKey[num] + "\n")
        
    if str(np.around(item[0], 0)) == str(ans):
        right = right + 1
        
    total = total + 1
percent = np.around((right/(total)) * 100, 2)
#f.write("Correct/Total: " + str(right) + "/" + str(total) + " = " + str(percent) + "%")
print("Training Data Correct/Total: " + str(right) + "/" + str(total) + " = " + str(percent) + "%")


#f.close()

print("Getting large dataset...")
full_data, full_answers, full_ansKey = dr.get_full_data_array(True)

print("Computing large dataset...")
full_output = nn.compute(full_data)

#f2 = open("results_2_new.txt", 'w')
right = 0
total = 0
for num, item in enumerate(full_output, 0):
    ans = str(full_answers[num][0])
    #f2.write("Output: " + str(np.around(item[0], 0)) + " - real: " + str(ans) + " type: " + full_ansKey[num] + "\n")
    print("Output: " + str(np.around(item[0], 0)) + " - real: " + str(ans) + " type: " + full_ansKey[num] + "\n")
    if str(np.around(item[0], 0)) == str(ans):
        right += 1
    
    total += 1

#f2.write("Correct/Total: " + str(right) + "/" + str(total) + " = " + str(np.around(right/(total) * 100, 2)) + "%")
print("Full Data Correct/Total: " + str(right) + "/" + str(total) + " = " + str(np.around((right/(total)) * 100, 2)) + "%")

#f2.close()
