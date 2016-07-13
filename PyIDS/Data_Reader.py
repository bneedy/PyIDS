

class Data_Reader(object):
    def __init__(self):
        self.dataTypes = []
        self.data = []

    def read_dataTypes_file(self, filename):
        file = open(filename)

        for line in file:
            self.dataTypes.append(line)
            print(line.split(','))

    def read_data_file(self, filename):
        file = open(filename)
        counter = 0
        
        for line in file:
            self.data.append(line)
            counter = counter + 1
            if counter >= 200:
                break