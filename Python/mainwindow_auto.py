# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1900, 1000)
        MainWindow.setMinimumSize(QtCore.QSize(460, 320))
        MainWindow.setMaximumSize(QtCore.QSize(1920, 1000))
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.labelCamera1 = QtWidgets.QLabel(self.centralWidget)
        self.labelCamera1.setGeometry(QtCore.QRect(20, 20, 800, 600))
        self.labelCamera1.setStyleSheet("image: url(:/HydraBot/media/Media/Rice_OwlBlack.jpg) no-repeat center center fixed;")
        self.labelCamera1.setText("")
        self.labelCamera1.setScaledContents(False)
        self.labelCamera1.setObjectName("labelCamera1")
        self.btnWebCam01 = QtWidgets.QPushButton(self.centralWidget)
        self.btnWebCam01.setGeometry(QtCore.QRect(820, 100, 131, 61))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.btnWebCam01.setFont(font)
        self.btnWebCam01.setObjectName("btnWebCam01")
        MainWindow.setCentralWidget(self.centralWidget)
        self.menuBar = QtWidgets.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 1900, 21))
        self.menuBar.setObjectName("menuBar")
        MainWindow.setMenuBar(self.menuBar)
        self.mainToolBar = QtWidgets.QToolBar(MainWindow)
        self.mainToolBar.setObjectName("mainToolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.mainToolBar)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.btnWebCam01.setText(_translate("MainWindow", "WebCam"))

