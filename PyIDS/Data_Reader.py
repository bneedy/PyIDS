import numpy as np
from sklearn.preprocessing import normalize

class Data_Reader(object):
    def __init__(self):
        self.answerTypes = []       # Answers for each tcp packet (i.e. normal, malicious, etc.)
        self.tcpFieldTypes = []     # Each field type for a tcp packet (i.e. protocol, service, etc.)
        self.symbolicOptions = {}   # All symbolic option types
        self.data = {}
        self.dataArray = []
        self.answersArray = []
        self.answerKeyArray = []
        self.dataTypeFileName = ""
        self.dataFileName = ""


    def readDataFiles(self, dataTypeFileName, dataFileName):
        self.read_dataTypes_file(dataTypeFileName)
        self.read_data_file(dataFileName)


    def read_dataTypes_file(self, filename):
        for num, line in enumerate(open(filename), 1):
            # First line is the tcp answer types
            if num == 1:
                for item in line.split('.')[0].split(','):
                    self.answerTypes.append(item)
            # All other lines are tcp field types
            else:
                self.tcpFieldTypes.append(line.split('.')[0].split(':'))
        
        # build up the dictionary for symbolic options
        for num, item in enumerate(self.tcpFieldTypes, 0):
            if 'symbolic' in item[1]:
                self.symbolicOptions[num] = []


    def read_data_file(self, dataFileName):
        for line in open(dataFileName):
            key = line.split(',')[-1].split('.')[0]

            if key not in self.data:
                self.data[key] = [line.split(',')[:-1]]
            else:
                self.data[key].append(line.split(',')[:-1])
  
          
    def get_data(self):
        return self.data


    def normalizeData(self, origData):
        return normalize(origData, axis=1, norm='l1')
        #newData = origData
        #for rowNum, row in enumerate(origData, 0):
        #    for itemNum, item in enumerate(np.amax(origData, axis = 0), 0):
        #        if item != 0:
        #            newData[rowNum][itemNum] = origData[rowNum][itemNum]/item
        #        else:
        #            newData[rowNum][itemNum] = origData[rowNum][itemNum]
        #return newData


    def get_data_array(self):

        # 22 bad types, 1 good
        for key in list(self.data.keys()):
            if key == 'normal':
                for item in self.data[key][:66]:
                    self.dataArray.append(item)
                    self.answersArray.append([0]) # 0 for good data
                    self.answerKeyArray.append(key)
            else:
                for item in self.data[key][:3]:
                    self.dataArray.append(item)
                    self.answersArray.append([1]) # 1 for malicious data
                    self.answerKeyArray.append(key)
        
        # loop over the each line of data
        for lineNum, line in enumerate(self.dataArray, 0):

            # for each line of data get each field and the field number
            for fieldNum, field in enumerate(line, 0):

                # check if the field is a symbolic field
                if fieldNum in self.symbolicOptions:

                    # check if that symbol has been added to the symbolic options, if not add it
                    # and get the value of that symbolic field
                    if field not in self.symbolicOptions[fieldNum]:
                        self.symbolicOptions[fieldNum].append(field)
                        self.dataArray[lineNum][fieldNum] = float(self.symbolicOptions[fieldNum].index(field))
                    else:
                        self.dataArray[lineNum][fieldNum] = float(self.symbolicOptions[fieldNum].index(field))

                # Not symbolic, then just convert to float
                else:
                    self.dataArray[lineNum][fieldNum] = float(self.dataArray[lineNum][fieldNum])
    
        return self.normalizeData(np.array(self.dataArray).astype(float)), np.array(self.answersArray).astype(float), self.answerKeyArray
