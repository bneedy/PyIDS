import sys
import Recorder as REC
from PyQt4 import QtGui
from PyQt4.QtCore import QThread, pyqtSignal, Qt, SIGNAL


class MainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()

        self.initUI()
        
    def initUI(self):
        # Create Main Widgets
        self.createActions()
        self.createMenuBar()
        self.createStatusBar()
        self.createRecorder()

        # Set the main widget - Recorder
        self.setCentralWidget(self.rec)

        # Create all connections after initializing
        self.createConnections()
        
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('PyIDS')    
        self.setWindowIcon(QtGui.QIcon("Icons/Engineering-64.png"))
        self.show()

    def createConnections(self):
        self.exitAct.triggered.connect(QtGui.qApp.quit)
        self.logAct.triggered.connect(self.rec.testLog)
        self.readPacketAct.triggered.connect(self.rec.readPacket)
        self.runNNAct.triggered.connect(self.rec.testClicked)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_L), self), SIGNAL('activated()'), self.rec.testLog)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_R), self), SIGNAL('activated()'), self.rec.readPacket)
        self.connect(QtGui.QShortcut(QtGui.QKeySequence(Qt.CTRL + Qt.Key_N), self), SIGNAL('activated()'), self.rec.testClicked)

    def createActions(self):
        # Exit Action
        self.exitAct = QtGui.QAction("Exit", self)
        self.exitAct.setShortcut("Ctrl+Q")
        self.exitAct.setToolTip("Exit Application")

        # Print to log test
        self.logAct = QtGui.QAction("Log Print\tCtrl+L", self)
        self.logAct.setToolTip("Print test output to log")

        # Read Packet
        self.readPacketAct = QtGui.QAction("Read Packet\tCtrl+R", self)
        self.readPacketAct.setToolTip("Read Packet")

        # Test Neural Network
        self.runNNAct = QtGui.QAction("Test Neural Network\tCtrl+N", self)
        self.runNNAct.setToolTip("Test Neural Network")

    def createMenuBar(self):
        self.menuBar = QtGui.QMenuBar()
        
        # File Menu
        self.fileMenu = self.menuBar.addMenu("File")
        self.fileMenu.addAction(self.exitAct)

        # Test Menu
        self.testMenu = self.menuBar.addMenu("Test")
        self.testMenu.addAction(self.logAct)
        self.testMenu.addAction(self.readPacketAct)
        self.testMenu.addAction(self.runNNAct)

        self.setMenuBar(self.menuBar)

    def createStatusBar(self):
        self.sb = QtGui.QStatusBar()

        self.setStatusBar(self.sb)
        self.sb.showMessage("Status: Ready")

    def createRecorder(self):
        self.rec = REC.Recorder()



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())