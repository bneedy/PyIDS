import numpy as np

class Data_Reader(object):
    def __init__(self):
        self.answerTypes = []       # Answers for each tcp packet (i.e. normal, malicious, etc.)
        self.tcpFieldTypes = []     # Each field type for a tcp packet (i.e. protocol, service, etc.)
        self.symbolicOptions = {}   # All symbolic option types
        self.data = []              # All tcp data
        self.answers = []           # Answer for each data element
        self.maxAnswerValue = 0     # Maximum value that will be normalized

    def readDataFiles(self, dataTypeFileName, dataFileName):
        self.read_dataTypes_file(dataTypeFileName)
        self.read_data_file(dataFileName)
        self.modify_data_list()
        self.modify_answer_list()

    def read_dataTypes_file(self, filename):
        file = open(filename)

        for num, line in enumerate(file, 1):
            # First line is the tcp answer types
            if num == 1:
                for item in line.split('.')[0].split(','):
                    self.answerTypes.append(item)
            # All other lines are tcp field types
            else:
                self.tcpFieldTypes.append(line.split('.')[0].split(':'))

    def read_data_file(self, filename):
        file = open(filename)
        tmpList = []

        for line in file:
            self.data.append(line.split(','))
            
            # Get answers and remove them from the data
            self.answers.append(self.data[-1][-1].split('.')[0])
            del self.data[-1][-1]

    def modify_data_list(self):
        # build up the dictionary for symbolic options
        for num, item in enumerate(self.tcpFieldTypes, 0):
            if 'symbolic' in item[1]:
                self.symbolicOptions[num] = []

        # This will convert each line of data to a list of floats and add any new symbolic values
        # to the symbolic options dictionary

        # loop over the each line of data
        for lineNum, line in enumerate(self.data, 0):

            # for each line of data get each field and the field number
            for fieldNum, field in enumerate(line, 0):

                # check if the field is a symbolic field
                if fieldNum in self.symbolicOptions:

                    # check if that symbol has been added to the symbolic options, if not add it
                    if field not in self.symbolicOptions[fieldNum]:
                        self.symbolicOptions[fieldNum].append(field)
                        self.data[lineNum][fieldNum] = float(self.symbolicOptions[fieldNum].index(field)) * 100
                    else:
                        self.data[lineNum][fieldNum] = float(self.symbolicOptions[fieldNum].index(field)) * 100

                # Not symbolic, then just convert to float
                else:
                    self.data[lineNum][fieldNum] = float(self.data[lineNum][fieldNum]) * 100

    def modify_answer_list(self):
        for ansNum, item in enumerate(self.answers, 0):
            self.answers[ansNum] = [self.answerTypes.index(item)]

    def normalizeData(self, origData):
        newData = origData
        for rowNum, row in enumerate(origData, 0):
            for itemNum, item in enumerate(np.amax(origData, axis = 0), 0):
                if item != 0:
                    newData[rowNum][itemNum] = origData[rowNum][itemNum]/item
                else:
                    newData[rowNum][itemNum] = origData[rowNum][itemNum]
        return newData

    def normalizeAnswers(self, origData):
        newData = origData
        self.maxAnswerValue = np.max(origData)
        for rowNum, row in enumerate(origData, 0):
            for itemNum, item in enumerate(row, 0):
                if max != 0:
                    newData[rowNum][itemNum] = origData[rowNum][itemNum]/self.maxAnswerValue
                else:
                    newData[rowNum][itemNum] = origData[rowNum][itemNum]
        return newData

    def get_data(self):
        return self.normalizeData(np.array(self.data).astype('float'))

    def get_answers(self):
        return self.normalizeAnswers(np.array(self.answers).astype('float'))

    def get_answer_name_list(self):
        return self.answerTypes

    def get_max_answer(self):
        return self.maxAnswerValue