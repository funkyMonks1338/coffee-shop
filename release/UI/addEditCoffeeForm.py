# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'addEditCoffeeForm.ui'
#
# Created by: PyQt5 UI code generator 5.15.5
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_addEditCoffeeForm(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(764, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 10, 741, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.create_coffee_btn = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.create_coffee_btn.setObjectName("create_coffee_btn")
        self.horizontalLayout.addWidget(self.create_coffee_btn)
        self.change_coffee_btn = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.change_coffee_btn.setObjectName("change_coffee_btn")
        self.horizontalLayout.addWidget(self.change_coffee_btn)
        self.show_hint_btn = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.show_hint_btn.setObjectName("show_hint_btn")
        self.horizontalLayout.addWidget(self.show_hint_btn)
        self.show_signatures_btn = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.show_signatures_btn.setObjectName("show_signatures_btn")
        self.horizontalLayout.addWidget(self.show_signatures_btn)
        self.table_widget = QtWidgets.QTableWidget(self.centralwidget)
        self.table_widget.setGeometry(QtCore.QRect(10, 60, 741, 471))
        self.table_widget.setObjectName("table_widget")
        self.table_widget.setColumnCount(0)
        self.table_widget.setRowCount(0)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 764, 31))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Добавьте или измените характеристики кофе"))
        self.create_coffee_btn.setText(_translate("MainWindow", "Создать кофе"))
        self.change_coffee_btn.setText(_translate("MainWindow", "Изменить характеристики кофе"))
        self.show_hint_btn.setText(_translate("MainWindow", "Показать подсказку"))
        self.show_signatures_btn.setText(_translate("MainWindow", "Образцы полей"))