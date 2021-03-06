# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dashboard.ui'
#
# Created: Mon Mar 31 22:52:15 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1004, 691)
        MainWindow.setMouseTracking(False)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../../../usr/share/pixmaps/cubeview48.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setWindowOpacity(1.0)
        MainWindow.setToolTip("")
        MainWindow.setAutoFillBackground(False)
        MainWindow.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        MainWindow.setTabShape(QtGui.QTabWidget.Rounded)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(420, 0, 271, 21))
        font = QtGui.QFont()
        font.setFamily("URW Chancery L")
        font.setPointSize(12)
        font.setWeight(75)
        font.setItalic(True)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.graph = PlotWidget(self.centralwidget)
        self.graph.setGeometry(QtCore.QRect(20, 30, 981, 351))
        self.graph.setObjectName("graph")
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(920, 650, 81, 31))
        font = QtGui.QFont()
        font.setPointSize(7)
        font.setWeight(75)
        font.setItalic(True)
        font.setBold(True)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.editedgraph = PlotWidget(self.centralwidget)
        self.editedgraph.setGeometry(QtCore.QRect(20, 390, 471, 281))
        self.editedgraph.setObjectName("editedgraph")
        self.dIdVval = QtGui.QLabel(self.centralwidget)
        self.dIdVval.setGeometry(QtCore.QRect(670, 390, 151, 16))
        self.dIdVval.setText("")
        self.dIdVval.setObjectName("dIdVval")
        self.dVdIval = QtGui.QLabel(self.centralwidget)
        self.dVdIval.setGeometry(QtCore.QRect(670, 420, 151, 16))
        self.dVdIval.setText("")
        self.dVdIval.setObjectName("dVdIval")
        self.fitgraph = PlotWidget(self.centralwidget)
        self.fitgraph.setGeometry(QtCore.QRect(500, 390, 501, 281))
        self.fitgraph.setObjectName("fitgraph")
        MainWindow.setCentralWidget(self.centralwidget)
        self.actionSave_as = QtGui.QAction(MainWindow)
        self.actionSave_as.setObjectName("actionSave_as")

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "graph editing", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MainWindow", "Linear fit curve segments and find intersections", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MainWindow", "Author: Jithin B.P.", None, QtGui.QApplication.UnicodeUTF8))
        self.actionSave_as.setText(QtGui.QApplication.translate("MainWindow", "Save as", None, QtGui.QApplication.UnicodeUTF8))

from pyqtgraph import PlotWidget
