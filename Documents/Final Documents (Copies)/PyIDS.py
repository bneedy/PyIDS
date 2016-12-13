import sys
import Recorder as REC
from PyQt4 import QtGui
from PyQt4.QtCore import QThread, pyqtSignal, Qt, QUrl, SIGNAL

class SpinBoxAction(QtGui.QWidgetAction):
    def __init__(self, parent):
        super(SpinBoxAction, self).__init__(parent)
        self.initUI()

    def initUI(self):
        widget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout()
        self.spinBox = QtGui.QSpinBox()
        self.spinBox.setMinimum(0)
        self.spinBox.setValue(90)
        self.spinBox.setMaximum(100)
        layout.addWidget(self.spinBox)
        widget.setLayout(layout)
        self.setDefaultWidget(widget)
    
    def getSpinBox(self):
        return self.spinBox
        

class MainWindow(QtGui.QMainWindow):
    
    def __init__(self):
        super(MainWindow, self).__init__()

        self.initUI()
        
    def initUI(self):
        # Create Main Widgets
        self.createActions()
        self.createMenuBar()
        self.createToolBar()
        self.createStatusBar()
        self.createRecorder()

        # Set the main widget - Recorder
        self.setCentralWidget(self.rec)

        # Create all connections after initializing
        self.createConnections()
        
        self.setGeometry(300, 300, 350, 300)
        self.setWindowTitle('PyIDS')    
        self.setWindowIcon(QtGui.QIcon("Icons/pyIDSmain.png"))
        self.show()

    def setNotificationsOn(self):
        self.rec.setNotificationToggle(True)

    def setNotificationsOff(self):
        self.rec.setNotificationToggle(False)

    def setDetailedLogOn(self):
        self.rec.setDetailedLogToggle(True)

    def setDetailedLogOff(self):
        self.rec.setDetailedLogToggle(False)

    def setAccuracy(self):
        self.rec.setAccuracy(int(self.accuracyAct.getSpinBox().value()))

    def saveLogFile(self):
        file = QtGui.QFileDialog.getSaveFileName(self, 'Save File', filter="Log file (*.log)")

        if len(file) > 0:
            self.rec.saveLogFile(file)

    def loadWeights(self):
        file = QtGui.QFileDialog.getOpenFileName(self, 'Open File', filter="Synapse Weight files (*.np)")

        if len(file) > 0:
            self.rec.loadWeights(file)

    def saveWeights(self):
        file = QtGui.QFileDialog.getSaveFileName(self, 'Save File', filter="Synapse Weight files (*.np)")

        if len(file) > 0:
            self.rec.saveWeights(file)

    def showAbout(self):
        about = QtGui.QMessageBox()
        about.setIcon(QtGui.QMessageBox.Information)
        about.setText("PyIDS is an Intrusion Detection System developed by Blake Knedler")
        about.setStandardButtons(QtGui.QMessageBox.Ok)
        about.setWindowTitle("PyIDS About")
        about.setWindowIcon(QtGui.QIcon("Icons/pyIDSmain.png"))
        about.exec_()

    def openGitRepo(self):
        QtGui.QDesktopServices.openUrl(QUrl("https://github.com/bneedy/PyIDS"))

    def setStatusLabel(self, info):
        self.statusLabel.setText("Status: " + info)

    def createConnections(self):
        self.rec.updateStatusLabel.connect(self.setStatusLabel)

        # Action connections
        self.saveLogFileAct.triggered.connect(self.saveLogFile)
        self.loadWeightsAct.triggered.connect(self.loadWeights)
        self.saveWeightsAct.triggered.connect(self.saveWeights)
        self.exitAct.triggered.connect(QtGui.qApp.quit)

        self.accuracyAct.getSpinBox().valueChanged.connect(self.setAccuracy)
        self.notificationsOnAct.triggered.connect(self.setNotificationsOn)
        self.notificationsOffAct.triggered.connect(self.setNotificationsOff)
        self.detailedLogOnAct.triggered.connect(self.setDetailedLogOn)
        self.detailedLogOffAct.triggered.connect(self.setDetailedLogOff)

        self.trainAct.triggered.connect(self.rec.trainClicked)
        self.runAct.triggered.connect(self.rec.runClicked)
        self.stopAct.triggered.connect(self.rec.stopClicked)
        self.printPktAct.triggered.connect(self.rec.printPacket)
        self.clearLogAct.triggered.connect(self.rec.clearLog)

        self.gitHubRepoAct.triggered.connect(self.openGitRepo)
        self.aboutAct.triggered.connect(self.showAbout)

    def createActions(self):
        # Save Log File
        self.saveLogFileAct = QtGui.QAction("Save Log File", self)
        self.saveLogFileAct.setShortcut("Ctrl+S")
        self.saveLogFileAct.setStatusTip("Save Log File")
        self.saveLogFileAct.setIcon(QtGui.QIcon("Icons/saveLog.png"))

        # Load Weights
        self.loadWeightsAct = QtGui.QAction("Load Weights", self)
        self.loadWeightsAct.setShortcut("Ctrl+L")
        self.loadWeightsAct.setStatusTip("Load Weights")
        self.loadWeightsAct.setIcon(QtGui.QIcon("Icons/load.png"))

        # Save Weights
        self.saveWeightsAct = QtGui.QAction("Save Weights", self)
        self.saveWeightsAct.setShortcut("Ctrl+W")
        self.saveWeightsAct.setStatusTip("Save Weights")
        self.saveWeightsAct.setIcon(QtGui.QIcon("Icons/save.png"))

        # Exit Action
        self.exitAct = QtGui.QAction("Exit", self)
        self.exitAct.setShortcut("Ctrl+Q")
        self.exitAct.setStatusTip("Exit Application")
        self.exitAct.setIcon(QtGui.QIcon("Icons/exit.png"))

        # Set Accuracy
        self.accuracyAct = SpinBoxAction(self)
        self.accuracyAct.setStatusTip("Set Accuracy Requirement")

        # Toggle Notifications On
        self.notificationsOnAct = QtGui.QAction("On", self)
        self.notificationsOnAct.setStatusTip("Turn Notifications On")
        self.notificationsOnAct.setCheckable(True)
        # Toggle Notifications Off
        self.notificationsOffAct = QtGui.QAction("Off", self)
        self.notificationsOffAct.setStatusTip("Turn Notifications Off")
        self.notificationsOffAct.setCheckable(True)
        # Toggle Notifications On/Off
        self.notificationsGroupAct = QtGui.QActionGroup(self)
        self.notificationsGroupAct.addAction(self.notificationsOnAct)
        self.notificationsGroupAct.addAction(self.notificationsOffAct)
        self.notificationsOnAct.setChecked(True)

        # Toggle Detailed Log On
        self.detailedLogOnAct = QtGui.QAction("On", self)
        self.detailedLogOnAct.setStatusTip("Turn Detailed Log On")
        self.detailedLogOnAct.setCheckable(True)
        # Toggle Detailed Off
        self.detailedLogOffAct = QtGui.QAction("Off", self)
        self.detailedLogOffAct.setStatusTip("Turn Detailed Log Off")
        self.detailedLogOffAct.setCheckable(True)
        # Toggle Detailed On/Off
        self.detailedLogGroupAct = QtGui.QActionGroup(self)
        self.detailedLogGroupAct.addAction(self.detailedLogOnAct)
        self.detailedLogGroupAct.addAction(self.detailedLogOffAct)
        self.detailedLogOffAct.setChecked(True)

        # Train
        self.trainAct = QtGui.QAction("Train", self)
        self.trainAct.setShortcut("Ctrl+T")
        self.trainAct.setStatusTip("Train PyIDS")
        self.trainAct.setIcon(QtGui.QIcon("Icons/train.png"))

        # Run
        self.runAct = QtGui.QAction("Run", self)
        self.runAct.setShortcut("Ctrl+R")
        self.runAct.setStatusTip("Run PyIDS")
        self.runAct.setIcon(QtGui.QIcon("Icons/run.png"))

        # Stop
        self.stopAct = QtGui.QAction("Stop", self)
        self.stopAct.setShortcut("Ctrl+X")
        self.stopAct.setStatusTip("Stop PyIDS from Running")
        self.stopAct.setIcon(QtGui.QIcon("Icons/stop.png"))

        # Print Packet
        self.printPktAct = QtGui.QAction("Print Packet", self)
        self.printPktAct.setShortcut("Ctrl+P")
        self.printPktAct.setStatusTip("Print a packet")
        self.printPktAct.setIcon(QtGui.QIcon("Icons/packet.png"))

        # Clear Log
        self.clearLogAct = QtGui.QAction("Clear Log", self)
        self.clearLogAct.setShortcut("Ctrl+C")
        self.clearLogAct.setStatusTip("Clear the Output Log")
        self.clearLogAct.setIcon(QtGui.QIcon("Icons/clear.png"))

        # GitHub Repo
        self.gitHubRepoAct = QtGui.QAction("PyIDS GitHub", self)
        self.gitHubRepoAct.setStatusTip("Go to PyIDS GitHub")
        self.gitHubRepoAct.setIcon(QtGui.QIcon("Icons/gitRepo.png"))

        # About
        self.aboutAct = QtGui.QAction("About", self)
        self.aboutAct.setStatusTip("About PyIDS")
        self.aboutAct.setIcon(QtGui.QIcon("Icons/about.png"))

    def createMenuBar(self):
        self.menuBar = QtGui.QMenuBar()
        
        # File Menu
        self.fileMenu = self.menuBar.addMenu("File")
        self.fileMenu.setStatusTip("Open PyIDS File Menu")
        self.fileMenu.addAction(self.saveLogFileAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.loadWeightsAct)
        self.fileMenu.addAction(self.saveWeightsAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        # Settings Menu
        self.settingsMenu = self.menuBar.addMenu("Settings")
        self.settingsMenu.setStatusTip("Open PyIDS Settings Menu")
        self.accuracyMenu = QtGui.QMenu("Set Accuracy")
        self.accuracyMenu.setStatusTip("Set Accuracy Requirement")
        self.accuracyMenu.setIcon(QtGui.QIcon("Icons/accuracy.png"))
        self.settingsMenu.addMenu(self.accuracyMenu)
        self.accuracyMenu.addAction(self.accuracyAct)
        self.notificationMenu = QtGui.QMenu("Toggle Notifications")
        self.notificationMenu.setStatusTip("Toggle Notifications On/Off")
        self.notificationMenu.setIcon(QtGui.QIcon("Icons/notifications.png"))
        self.settingsMenu.addMenu(self.notificationMenu)
        self.notificationMenu.addAction(self.notificationsOnAct)
        self.notificationMenu.addAction(self.notificationsOffAct)
        self.detailedLogMenu = QtGui.QMenu("Toggle Detailed Log")
        self.detailedLogMenu.setStatusTip("Toggle Detailed Log On/Off")
        self.detailedLogMenu.setIcon(QtGui.QIcon("Icons/log.png"))
        self.settingsMenu.addMenu(self.detailedLogMenu)
        self.detailedLogMenu.addAction(self.detailedLogOnAct)
        self.detailedLogMenu.addAction(self.detailedLogOffAct)

        # Commands Menu
        self.commandMenu = self.menuBar.addMenu("Commands")
        self.commandMenu.setStatusTip("Open PyIDS Commands Menu")
        self.commandMenu.addAction(self.trainAct)
        self.commandMenu.addAction(self.runAct)
        self.commandMenu.addAction(self.stopAct)
        self.commandMenu.addSeparator()
        self.commandMenu.addAction(self.printPktAct)
        self.commandMenu.addSeparator()
        self.commandMenu.addAction(self.clearLogAct)

        # Help Menu
        self.helpMenu = self.menuBar.addMenu("Help")
        self.helpMenu.setStatusTip("Open PyIDS Help Menu")
        self.helpMenu.addAction(self.gitHubRepoAct)
        self.helpMenu.addAction(self.aboutAct)

        self.setMenuBar(self.menuBar)

    def createToolBar(self):
        self.toolBar = QtGui.QToolBar()
        
        self.toolBar.addAction(self.saveLogFileAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.loadWeightsAct)
        self.toolBar.addAction(self.saveWeightsAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.trainAct)
        self.toolBar.addAction(self.runAct)
        self.toolBar.addAction(self.stopAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.printPktAct)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.clearLogAct)

        self.addToolBar(self.toolBar)

    def createStatusBar(self):
        self.sb = QtGui.QStatusBar()
        self.statusLabel = QtGui.QLabel()
        self.statusLabel.setText("Status: Ready")

        self.setStatusBar(self.sb)
        self.sb.addPermanentWidget(self.statusLabel)

    def createRecorder(self):
        self.rec = REC.Recorder()



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())