import sys
import numpy as np
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal
import Neural_Network as NN
import Data_Reader as DR

class DataReaderWorker(QThread):
    displaySignal = pyqtSignal(str)
    returnSignalSmall = pyqtSignal(np.ndarray, np.ndarray, list)
    returnSignalLarge = pyqtSignal(np.ndarray, np.ndarray, list)

    def __init__(self, dr):
        super().__init__()
        self.dataReader = dr

    def setDataFiles(self, dataTypesFile, dataFile):
        self.dataTypesFile = dataTypesFile
        self.dataFile = dataFile

    def run(self):
        if hasattr(self,'dataTypesFile') and hasattr(self,'dataFile'):
            self.displaySignal.emit("Reading Data Files...")
            self.dataReader.readDataFiles(self.dataTypesFile, self.dataFile)

            self.displaySignal.emit("Getting small dataset...")
            self.data, self.answers, self.ansKey = self.dataReader.get_data_array(True)
            self.returnSignalSmall.emit(self.data, self.answers, self.ansKey)

            self.displaySignal.emit("Getting large dataset...")
            self.full_data, self.full_answers, self.full_ansKey = self.dataReader.get_full_data_array(True)
            self.returnSignalLarge.emit(self.full_data, self.full_answers, self.full_ansKey)

            self.displaySignal.emit("Finished Initializing")

        else:
            self.displaySignal.emit("Data files are not set.")

class NeuralNetworkWorker(QThread):
    displaySignal = pyqtSignal(str)
    returnSignal = pyqtSignal(np.ndarray, np.ndarray, list)

    def __init__(self, nn, data, answers, ansKey, outputFile, trainFlag):
        super().__init__()
        self.nn = nn
        self.data = data
        self.answers = answers
        self.ansKey = ansKey
        self.outputFile = outputFile
        self.trainFlag = trainFlag
        self.writeToFile = False

    def calculateCorrectness(self, output, answers, ansKey):
        # Calculate correctness...
        right = 0
        total = 0
        for num, item in enumerate(output, 0):
            ans = str(answers[num][0])
            if self.writeToFile:
                self.fileOut.write("Output: " + str(np.around(item[0], 0)) + " - real: " + str(ans) + " type: " + ansKey[num] + "\n")
            if str(np.around(item[0], 0)) == str(ans):
                right += 1
            total += 1
        percent = np.around((right/(total)) * 100, 2)
        return right, total, percent

    def run(self):
        if hasattr(self, 'outputFile'):
            if self.outputFile:
                self.fileOut = open(self.outputFile, 'a')
                self.writeToFile = True

        if self.trainFlag:
            self.displaySignal.emit("Beginning training...")
            self.nn.train(self.data,self.answers)

        self.displaySignal.emit("Computing dataset...")
        output = self.nn.compute(self.data)

        # Calculate correctness...
        self.displaySignal.emit("Calculating correctness...")
        right, total, percent = self.calculateCorrectness(output, self.answers, self.ansKey)

        # Display correctness....
        self.displaySignal.emit("Data Correct/Total: " + str(right) + "/" + str(total) + " = " + str(percent) + "%")
        if self.writeToFile:
            self.fileOut.write("Correct/Total: " + str(right) + "/" + str(total) + " = " + str(np.around(right/(total) * 100, 2)) + "%")
            self.fileOut.close()


class MainWindow(QWidget):
    
    def __init__(self):
        super().__init__()

        # Need to make the changeable
        self.dataTypesFile = "dataTypesFile.txt"
        self.dataFile = "tmpMsg2.txt"

        self.middleLayerOne = 14
        self.middleLayerTwo = 9
        self.outputLayer = 1

        self.initUI()
        
    def initUI(self):
        self.infoLabel = QLabel('Info:')
        self.infoView = QListWidget()

        self.outputFileLabel = QLabel('Output File:')
        self.outputFileEdit = QLineEdit()
        self.outputFileEdit.setText('outputFileTESTING.txt')

        self.initBtn = QPushButton('Init')
        self.initBtn.clicked.connect(self.initDataReader)

        self.trainBtn = QPushButton('Train')
        self.trainBtn.setEnabled(False)
        self.trainBtn.clicked.connect(self.trainClicked)

        self.runBtn = QPushButton('Run')
        self.runBtn.setEnabled(False)
        self.runBtn.clicked.connect(self.runClicked)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.infoLabel, 1, 0)
        grid.addWidget(self.infoView, 1, 1, 5, 4)

        grid.addWidget(self.outputFileLabel, 6, 0)
        grid.addWidget(self.outputFileEdit, 6, 1, 1, 4)

        grid.addWidget(self.initBtn, 7, 2)
        grid.addWidget(self.trainBtn, 7, 3)
        grid.addWidget(self.runBtn, 7, 4)
        
        self.setLayout(grid) 
        
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('PyIDS')    
        self.show()

    def initDataReader(self):
        self.initBtn.setEnabled(False)
        self.initBtn.hide()
        self.dr = DR.Data_Reader()

        self.dataReaderThread = DataReaderWorker(self.dr)
        self.dataReaderThread.displaySignal.connect(self.displayText)
        self.dataReaderThread.returnSignalSmall.connect(self.getDataSmall)
        self.dataReaderThread.returnSignalLarge.connect(self.getDataLarge)
        self.dataReaderThread.finished.connect(self.initNeuralNetwork)
        self.dataReaderThread.setDataFiles(self.dataTypesFile, self.dataFile)
        self.dataReaderThread.start()

    def getDataSmall(self, data, answers, ansKey):
        self.data = data
        self.answers = answers
        self.ansKey = ansKey

    def getDataLarge(self, data, answers, ansKey):
        self.full_data = data
        self.full_answers = answers
        self.full_ansKey = ansKey

    def initNeuralNetwork(self):
        self.nn = NN.Neural_Network(int(self.data[0].size), self.middleLayerOne, \
                                            self.middleLayerTwo, self.outputLayer)

        self.initBtn.setEnabled(False)
        self.trainBtn.setEnabled(True)

    def trainClicked(self):
        self.trainBtn.setEnabled(False)
        self.runBtn.setEnabled(False)
        self.trainingNeuralThread = NeuralNetworkWorker(self.nn, self.data, self.answers, self.ansKey, self.outputFileEdit.text(), True)
        self.trainingNeuralThread.displaySignal.connect(self.displayText)
        self.trainingNeuralThread.finished.connect(self.finishedNeuralComputing)
        self.trainingNeuralThread.start()

    def runClicked(self):
        self.trainBtn.setEnabled(False)
        self.runBtn.setEnabled(False)
        self.neuralThread = NeuralNetworkWorker(self.nn, self.full_data, self.full_answers, self.full_ansKey, self.outputFileEdit.text(), False)
        self.neuralThread.displaySignal.connect(self.displayText)
        self.neuralThread.finished.connect(self.finishedNeuralComputing)
        self.neuralThread.start()

    def finishedNeuralComputing(self):
        self.trainBtn.setEnabled(True)
        self.runBtn.setEnabled(True)

    def displayText(self, str):
        item = QListWidgetItem()
        item.setText(str)
        self.infoView.addItem(item)
        self.infoView.update()
        self.infoView.scrollToBottom()



if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())