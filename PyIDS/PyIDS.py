import Neural_Network as NN
import Data_Reader as DR
import numpy as np

dataTypesFile = "dataTypesFile.txt"
dataFile = "tmpMsg1.txt"

dr = DR.Data_Reader()
dr.readDataFiles(dataTypesFile, dataFile)

data = dr.get_data()
answers = dr.get_answers()
answerList = dr.get_answer_name_list()
maxAnswer = dr.get_max_answer()

nn = NN.Neural_Network(int(data[0].size),10,5,int(answers[0].size))
output = nn.train(data, answers)

for num, item in enumerate(output, 1):
    if num == 1:
        print(answerList[int(round(item[0] * maxAnswer))])
        print(item[0])
        print("========")
    if num == 5:
        print(answerList[int(round(item[0] * maxAnswer))])
        print(item[0])
        print("========")