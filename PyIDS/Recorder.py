import sys
import numpy as np
from PyQt4 import QtGui
from PyQt4.QtCore import QThread, pyqtSignal, Qt, SIGNAL
import Neural_Network as NN
import Data_Reader as DR
import Network_Traffic_Reader as NTR


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
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
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
        
        QtGui.QApplication.restoreOverrideCursor()

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
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
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

        QtGui.QApplication.restoreOverrideCursor()

class NeuralNetworkDeciderWorker(QThread):
    displaySignal = pyqtSignal(str)
    notifySignal = pyqtSignal(str)
    returnSignal = pyqtSignal(np.ndarray, np.ndarray, list)

    def __init__(self, nn, dataReader):
        super().__init__()
        self.nn = nn
        self.dataReader = dataReader
        self.ntf = NTR.Network_Traffic_Reader()

    def run(self):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(Qt.WaitCursor))
        
        for x in range(0, 11):
            if x < 10:
                data = self.ntf.getNextPacket()
            # Test Malicious
            else:
                data = ['tcp', 'S0', '1']

            newData = self.dataReader.convertSymbolic(data)
            output = self.nn.compute(newData)
            if str(np.around(output[0][0], 0)) == '1.0':
                outputType = "MALICIOUS"
            else:
                outputType = "NORMAL"

            self.displaySignal.emit(outputType + ": " + str(data) + " VAL: " + str(output[0][0]))
            if outputType == "MALICIOUS":
                self.notifySignal.emit(outputType + ": " + str(data))

        QtGui.QApplication.restoreOverrideCursor()



class Recorder(QtGui.QWidget):
    def __init__(self):
        super(Recorder, self).__init__()

        # Need to make the changeable
        self.dataTypesFile = "dataTypesFile.txt"
        self.dataFile = "tmpMsg2.txt"

        self.middleLayerOne = 12
        self.middleLayerTwo = 8
        self.outputLayer = 1

        self.initUI()

    def initUI(self):
        self.infoLabel = QtGui.QLabel('Info:')
        self.infoView = QtGui.QPlainTextEdit()
        self.infoView.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.infoView.setReadOnly(True)

        self.outputFileLabel = QtGui.QLabel('Output File:')
        self.outputFileEdit = QtGui.QLineEdit()
        #self.outputFileEdit.setText('outputFileTESTING.txt')

        self.initBtn = QtGui.QPushButton('Init')
        self.initBtn.clicked.connect(self.initDataReader)

        self.trainBtn = QtGui.QPushButton('Train')
        self.trainBtn.setEnabled(False)
        self.trainBtn.clicked.connect(self.trainClicked)

        self.testBtn = QtGui.QPushButton('Test')
        self.testBtn.setEnabled(False)
        self.testBtn.clicked.connect(self.testClicked)

        self.runBtn = QtGui.QPushButton('Run')
        self.runBtn.setEnabled(False)
        self.runBtn.clicked.connect(self.runClicked)

        self.saveWeightsBtn = QtGui.QPushButton('Save Weights')
        self.saveWeightsBtn.setEnabled(False)
        self.saveWeightsBtn.clicked.connect(self.saveWeightsClicked)

        self.loadWeightsBtn = QtGui.QPushButton('Load Weights')
        self.loadWeightsBtn.setEnabled(False)
        self.loadWeightsBtn.clicked.connect(self.loadWeightsClicked)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(self.infoLabel, 1, 0)
        grid.addWidget(self.infoView, 1, 1, 5, 4)

        grid.addWidget(self.outputFileLabel, 6, 0)
        grid.addWidget(self.outputFileEdit, 6, 1, 1, 4)

        grid.addWidget(self.saveWeightsBtn, 7, 3)
        grid.addWidget(self.loadWeightsBtn, 7, 4)

        grid.addWidget(self.initBtn, 8, 1)
        grid.addWidget(self.trainBtn, 8, 2)
        grid.addWidget(self.testBtn, 8, 3)
        grid.addWidget(self.runBtn, 8, 4)
        
        self.setLayout(grid) 


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
        self.loadWeightsBtn.setEnabled(True)

    def trainClicked(self):
        self.runBtn.setEnabled(False)
        self.trainBtn.setEnabled(False)
        self.testBtn.setEnabled(False)
        self.saveWeightsBtn.setEnabled(False)
        self.loadWeightsBtn.setEnabled(False)
        self.trainingNeuralThread = NeuralNetworkWorker(self.nn, self.data, self.answers, self.ansKey, self.outputFileEdit.text(), True)
        self.trainingNeuralThread.displaySignal.connect(self.displayText)
        self.trainingNeuralThread.finished.connect(self.finishedNeuralComputing)
        self.trainingNeuralThread.start()

    def testClicked(self):
        self.runBtn.setEnabled(False)
        self.trainBtn.setEnabled(False)
        self.testBtn.setEnabled(False)
        self.saveWeightsBtn.setEnabled(False)
        self.loadWeightsBtn.setEnabled(False)
        self.neuralThread = NeuralNetworkWorker(self.nn, self.full_data, self.full_answers, self.full_ansKey, self.outputFileEdit.text(), False)
        self.neuralThread.displaySignal.connect(self.displayText)
        self.neuralThread.finished.connect(self.finishedNeuralComputing)
        self.neuralThread.start()

    def runClicked(self):
        self.runBtn.setEnabled(False)
        self.trainBtn.setEnabled(False)
        self.testBtn.setEnabled(False)
        self.saveWeightsBtn.setEnabled(False)
        self.loadWeightsBtn.setEnabled(False)
        self.neuralDeciderThread = NeuralNetworkDeciderWorker(self.nn, self.dr)
        self.neuralDeciderThread.displaySignal.connect(self.displayText)
        self.neuralDeciderThread.notifySignal.connect(self.notify)
        self.neuralDeciderThread.finished.connect(self.finishedNeuralComputing)
        self.neuralDeciderThread.start()

    def saveWeightsClicked(self):
        self.runBtn.setEnabled(False)
        self.trainBtn.setEnabled(False)
        self.testBtn.setEnabled(False)
        self.saveWeightsBtn.setEnabled(False)
        self.loadWeightsBtn.setEnabled(False)

        self.nn.saveWeights()

        self.runBtn.setEnabled(True)
        self.trainBtn.setEnabled(True)
        self.testBtn.setEnabled(True)
        self.saveWeightsBtn.setEnabled(True)
        self.loadWeightsBtn.setEnabled(True)

    def loadWeightsClicked(self):
        self.runBtn.setEnabled(False)
        self.trainBtn.setEnabled(False)
        self.testBtn.setEnabled(False)
        self.saveWeightsBtn.setEnabled(False)
        self.loadWeightsBtn.setEnabled(False)

        self.nn.loadWeights()

        self.runBtn.setEnabled(True)
        self.trainBtn.setEnabled(True)
        self.testBtn.setEnabled(True)
        self.saveWeightsBtn.setEnabled(True)
        self.loadWeightsBtn.setEnabled(True)

    def finishedNeuralComputing(self):
        self.runBtn.setEnabled(True)
        self.trainBtn.setEnabled(True)
        self.testBtn.setEnabled(True)
        self.saveWeightsBtn.setEnabled(True)
        self.loadWeightsBtn.setEnabled(True)

    def readPacket(self):
        reader = NTR.Network_Traffic_Reader()
        pkt = reader.getSinglePacket()
        if pkt != "":
            self.displayText(pkt)
            self.notify(pkt)
        else:
            self.displayText("Packet was not TCP/UDP.\nTrying again...")
            self.readPacket()

    def displayText(self, str):
        self.infoView.appendPlainText(str)

    def testLog(self):
        self.infoView.appendPlainText("TEST LOG OUTPUT")

    def notify(self, str):
        notification = QtGui.QSystemTrayIcon(self)
        notification.setVisible(True)
        notification.showMessage("Alert!", str, QtGui.QSystemTrayIcon.Critical, 10000)