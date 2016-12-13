import sys, time
import numpy as np
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import QThread, pyqtSignal, Qt, SIGNAL
import Neural_Network as NN
import Data_Reader as DR
import Network_Traffic_Reader as NTR


class DataReaderWorker(QThread):
    displaySignal = pyqtSignal(str)
    updateStatus = pyqtSignal(str)
    returnSignalSmall = pyqtSignal(np.ndarray, np.ndarray, list)
    returnSignalLarge = pyqtSignal(np.ndarray, np.ndarray, list)

    def __init__(self, dr):
        super().__init__()
        self.dataReader = dr

    def setDataFiles(self, dataTypesFile, dataFile):
        self.dataTypesFile = dataTypesFile
        self.dataFile = dataFile

    def run(self):
        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(Qt.BusyCursor))
        self.updateStatus.emit("Initializing")

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
        
        self.updateStatus.emit("Initilized")
        QtGui.QApplication.restoreOverrideCursor()
        QtGui.QApplication.processEvents()

class NeuralNetworkWorker(QThread):
    displaySignal = pyqtSignal(str)
    updateStatus = pyqtSignal(str)
    returnSignal = pyqtSignal(np.ndarray, np.ndarray, list)

    def __init__(self, nn, data, answers, ansKey, accuracy):
        super().__init__()
        self.nn = nn
        self.data = data
        self.answers = answers
        self.ansKey = ansKey
        self.accuracy = accuracy

    def calculateCorrectness(self, output, answers, ansKey):
        # Calculate correctness...
        right = 0
        total = 0
        for num, item in enumerate(output, 0):
            ans = str(answers[num][0])
            if str(np.around(item[0], 0)) == str(ans):
                right += 1
            total += 1
        percent = np.around((right/(total)) * 100, 2)
        return right, total, percent

    def run(self):
        self.updateStatus.emit("Training")

        QtGui.QApplication.setOverrideCursor(QtGui.QCursor(Qt.BusyCursor))

        self.displaySignal.emit("Beginning training...")
        self.nn.train(self.data,self.answers,self.accuracy)

        self.displaySignal.emit("Computing dataset...")
        output = self.nn.compute(self.data)

        # Calculate correctness...
        self.displaySignal.emit("Calculating correctness...")
        right, total, percent = self.calculateCorrectness(output, self.answers, self.ansKey)

        # Display correctness....
        self.displaySignal.emit("DETAIL:Data Correct/Total: " + str(right) + "/" + str(total))
        self.displaySignal.emit("Trained Accuracy: " + str(percent) + "%\n")
        
        self.updateStatus.emit("Trained")
        QtGui.QApplication.restoreOverrideCursor()
        QtGui.QApplication.processEvents()

class NeuralNetworkDeciderWorker(QThread):
    displaySignal = pyqtSignal(str)
    updateStatus = pyqtSignal(str)
    notifySignal = pyqtSignal(str)
    returnSignal = pyqtSignal(np.ndarray, np.ndarray, list)

    def __init__(self, nn, dataReader):
        super().__init__()
        self.nn = nn
        self.dataReader = dataReader
        self.ntf = NTR.Network_Traffic_Reader()
        self.stopFlag = False
        self.count = 0

    def run(self):
        self.updateStatus.emit("Running")
        self.displaySignal.emit("Running...")

        while not self.stopFlag:
            data = self.ntf.getNextPacket()
            self.count += 1
            newData = self.dataReader.convertSymbolic(data)
            output = self.nn.compute(newData)
            if str(np.around(output[0][0], 0)) == '1.0':
                outputType = "MALICIOUS"
            else:
                outputType = "NORMAL"

            if outputType == "MALICIOUS":
                self.displaySignal.emit(outputType + ": " + str(data) + " VAL: " + str(output[0][0]))
                self.notifySignal.emit(outputType + ": " + str(data))
            else:
                self.displaySignal.emit("DETAIL:" + outputType + ": " + str(data) + " VAL: " + str(output[0][0]))

    def stop(self):
        self.displaySignal.emit("DETAIL:Total read packets: " + str(self.count))
        self.updateStatus.emit("Stopped")
        self.stopFlag = True


class Recorder(QtGui.QPlainTextEdit):
    updateStatusLabel = pyqtSignal(str)

    def __init__(self):
        super(Recorder, self).__init__()

        self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.setReadOnly(True)

        self.dataTypesFile = "dataTypesFile.txt"
        self.dataFile = "tmpMsg2.txt"

        self.middleLayerOne = 12
        self.middleLayerTwo = 8
        self.outputLayer = 1 

        self.log = []
        self.notifications = True
        self.detailedLogFlag = False
        self.accuracyValue = 90

        self.trained = False
        self.trainingOrRunning = False

        self.dr = DR.Data_Reader()
        self.nn = NN.Neural_Network(20, self.middleLayerOne, self.middleLayerTwo, self.outputLayer)
        self.dataReaderThread = DataReaderWorker(self.dr)
        self.trainingNeuralThread = NeuralNetworkWorker(self.nn, [], [], [], self.accuracyValue)
        self.neuralDeciderThread = NeuralNetworkDeciderWorker(self.nn, self.dr)

    # Initialize by reading data
    def initDataReader(self):
        self.dataReaderThread = DataReaderWorker(self.dr)
        self.dataReaderThread.displaySignal.connect(self.displayText)
        self.dataReaderThread.updateStatus.connect(self.emitStatusUpdate)
        self.dataReaderThread.returnSignalSmall.connect(self.getDataSmall)
        self.dataReaderThread.returnSignalLarge.connect(self.getDataLarge)
        self.dataReaderThread.finished.connect(self.initNeuralNetwork)
        self.dataReaderThread.setDataFiles(self.dataTypesFile, self.dataFile)
        self.dataReaderThread.start()

    # Initialize the Neural Network
    def initNeuralNetwork(self):

        self.nn = NN.Neural_Network(int(self.data[0].size), self.middleLayerOne, \
                                            self.middleLayerTwo, self.outputLayer)

        self.trainingNeuralThread = NeuralNetworkWorker(self.nn, self.data, self.answers, self.ansKey, self.accuracyValue)
        self.trainingNeuralThread.displaySignal.connect(self.displayText)
        self.trainingNeuralThread.updateStatus.connect(self.emitStatusUpdate)
        self.trainingNeuralThread.finished.connect(self.finishedNeuralComputing)
        self.trainingNeuralThread.start()

    def run(self):
        self.neuralDeciderThread = NeuralNetworkDeciderWorker(self.nn, self.dr)
        self.neuralDeciderThread.displaySignal.connect(self.displayText)
        self.neuralDeciderThread.updateStatus.connect(self.emitStatusUpdate)
        self.neuralDeciderThread.notifySignal.connect(self.notify)
        self.neuralDeciderThread.finished.connect(self.finishedRunning)
        self.neuralDeciderThread.start()

    def finishedNeuralComputing(self):
        self.trained = True
        if self.runAfter:
            self.run()
        else:
            self.trainingOrRunning = False

    def finishedRunning(self):
        self.trainingOrRunning = False

    def getDataSmall(self, data, answers, ansKey):
        self.data = data
        self.answers = answers
        self.ansKey = ansKey

    def getDataLarge(self, data, answers, ansKey):
        self.full_data = data
        self.full_answers = answers
        self.full_ansKey = ansKey

    def readPacket(self):
        reader = NTR.Network_Traffic_Reader()
        pkt = reader.getSinglePacket()

        self.displayText("Read packet:\n" + pkt)
        self.notify(pkt)

    # Log Information
    def displayText(self, str):
        prefix = "DETAIL:"
        if str.startswith(prefix):
            str = str[len(prefix):]
            if self.detailedLogFlag:
                self.appendPlainText(str)
        else:
            self.appendPlainText(str)

        self.log.append(str + "\n")
    
    # Notify Information
    def notify(self, str):
        if self.notifications:
            notification = QtGui.QSystemTrayIcon(self)
            notification.setIcon(QtGui.QIcon("Icons/pyIDSmain.png"))
            notification.setVisible(True)
            notification.showMessage("PyIDS: Alert!", str, QtGui.QSystemTrayIcon.Critical, 10000)

    def emitStatusUpdate(self, str):
        self.updateStatusLabel.emit(str)

    ####################
    ## Button Clicks ###
    ####################

    def saveLogFile(self, saveFilename):
        file = open(saveFilename, 'w')
        for line in self.log:
            file.write(line)
        file.close()

    def loadWeights(self, loadFilename):
        self.nn.loadWeights(loadFilename)
        self.trained = True

    def saveWeights(self, saveFilename):
        self.nn.saveWeights(saveFilename)

    def setNotificationToggle(self, notif):
        self.notifications = notif

    def setDetailedLogToggle(self, detailLog):
        self.detailedLogFlag = detailLog

    def setAccuracy(self, accVal):
        self.accuracyValue = accVal

    def trainClicked(self):
        if not self.trainingOrRunning:
            self.trainingOrRunning = True
            self.runAfter = False
            self.initDataReader()

    def runClicked(self):
        if not self.trainingOrRunning:
            self.trainingOrRunning = True
            if not self.trained:
                self.runAfter = True
                self.initDataReader()
            else:
                self.runAfter = False
                self.run()

    def stopClicked(self):
        if (self.neuralDeciderThread.isRunning()):
            self.neuralDeciderThread.stop()
            self.neuralDeciderThread.wait(2000)
            if (self.neuralDeciderThread.isRunning()):
                self.neuralDeciderThread.terminate()
        self.finishedRunning()

    def printPacket(self):
        self.readPacket()

    def clearLog(self):
        self.clear()