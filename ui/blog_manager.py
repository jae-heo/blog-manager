# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ui\blog_manager.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(623, 351)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tab_main = QtWidgets.QTabWidget(self.centralwidget)
        self.tab_main.setGeometry(QtCore.QRect(0, 0, 621, 281))
        self.tab_main.setObjectName("tab_main")
        self.tab_login = QtWidgets.QWidget()
        self.tab_login.setObjectName("tab_login")
        self.lineEdit_username = QtWidgets.QLineEdit(self.tab_login)
        self.lineEdit_username.setGeometry(QtCore.QRect(90, 120, 181, 31))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(12)
        self.lineEdit_username.setFont(font)
        self.lineEdit_username.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.lineEdit_username.setInputMask("")
        self.lineEdit_username.setText("")
        self.lineEdit_username.setMaxLength(30)
        self.lineEdit_username.setPlaceholderText("")
        self.lineEdit_username.setClearButtonEnabled(False)
        self.lineEdit_username.setObjectName("lineEdit_username")
        self.lineEdit_password = QtWidgets.QLineEdit(self.tab_login)
        self.lineEdit_password.setGeometry(QtCore.QRect(90, 160, 181, 31))
        font = QtGui.QFont()
        font.setFamily("Arial Black")
        font.setPointSize(12)
        self.lineEdit_password.setFont(font)
        self.lineEdit_password.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
        self.lineEdit_password.setInputMask("")
        self.lineEdit_password.setText("")
        self.lineEdit_password.setMaxLength(30)
        self.lineEdit_password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_password.setPlaceholderText("")
        self.lineEdit_password.setClearButtonEnabled(False)
        self.lineEdit_password.setObjectName("lineEdit_password")
        self.label_1 = QtWidgets.QLabel(self.tab_login)
        self.label_1.setGeometry(QtCore.QRect(50, 120, 31, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_1.setFont(font)
        self.label_1.setObjectName("label_1")
        self.label_2 = QtWidgets.QLabel(self.tab_login)
        self.label_2.setGeometry(QtCore.QRect(50, 160, 31, 21))
        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.pushButton_login = QtWidgets.QPushButton(self.tab_login)
        self.pushButton_login.setGeometry(QtCore.QRect(290, 130, 61, 51))
        self.pushButton_login.setObjectName("pushButton_login")
        self.label = QtWidgets.QLabel(self.tab_login)
        self.label.setGeometry(QtCore.QRect(50, 45, 191, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.tab_main.addTab(self.tab_login, "")
        self.tab_configuration = QtWidgets.QWidget()
        self.tab_configuration.setObjectName("tab_configuration")
        self.label_3 = QtWidgets.QLabel(self.tab_configuration)
        self.label_3.setGeometry(QtCore.QRect(20, 20, 131, 21))
        self.label_3.setObjectName("label_3")
        self.radioButton_category = QtWidgets.QRadioButton(self.tab_configuration)
        self.radioButton_category.setGeometry(QtCore.QRect(20, 50, 90, 16))
        self.radioButton_category.setObjectName("radioButton_category")
        self.radioButton_keyword = QtWidgets.QRadioButton(self.tab_configuration)
        self.radioButton_keyword.setGeometry(QtCore.QRect(20, 70, 90, 16))
        self.radioButton_keyword.setObjectName("radioButton_keyword")
        self.label_4 = QtWidgets.QLabel(self.tab_configuration)
        self.label_4.setGeometry(QtCore.QRect(20, 110, 131, 21))
        self.label_4.setObjectName("label_4")
        self.plainTextEdit_requestMessage = QtWidgets.QPlainTextEdit(self.tab_configuration)
        self.plainTextEdit_requestMessage.setGeometry(QtCore.QRect(20, 140, 181, 81))
        self.plainTextEdit_requestMessage.setObjectName("plainTextEdit_requestMessage")
        self.comboBox_mainCategory = QtWidgets.QComboBox(self.tab_configuration)
        self.comboBox_mainCategory.setGeometry(QtCore.QRect(140, 50, 111, 22))
        self.comboBox_mainCategory.setObjectName("comboBox_mainCategory")
        self.comboBox_subCategory = QtWidgets.QComboBox(self.tab_configuration)
        self.comboBox_subCategory.setGeometry(QtCore.QRect(260, 50, 111, 22))
        self.comboBox_subCategory.setObjectName("comboBox_subCategory")
        self.lineEdit_keyword = QtWidgets.QLineEdit(self.tab_configuration)
        self.lineEdit_keyword.setGeometry(QtCore.QRect(140, 50, 141, 20))
        self.lineEdit_keyword.setObjectName("lineEdit_keyword")
        self.pushButton_run = QtWidgets.QPushButton(self.tab_configuration)
        self.pushButton_run.setGeometry(QtCore.QRect(440, 170, 121, 51))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_run.setFont(font)
        self.pushButton_run.setObjectName("pushButton_run")
        self.plainTextEdit_postComment = QtWidgets.QPlainTextEdit(self.tab_configuration)
        self.plainTextEdit_postComment.setGeometry(QtCore.QRect(220, 140, 181, 81))
        self.plainTextEdit_postComment.setObjectName("plainTextEdit_postComment")
        self.label_6 = QtWidgets.QLabel(self.tab_configuration)
        self.label_6.setGeometry(QtCore.QRect(220, 110, 131, 21))
        self.label_6.setObjectName("label_6")
        self.tab_main.addTab(self.tab_configuration, "")
        self.tab_run = QtWidgets.QWidget()
        self.tab_run.setObjectName("tab_run")
        self.plainTextEdit_run = QtWidgets.QPlainTextEdit(self.tab_run)
        self.plainTextEdit_run.setGeometry(QtCore.QRect(10, 70, 591, 181))
        self.plainTextEdit_run.setReadOnly(True)
        self.plainTextEdit_run.setObjectName("plainTextEdit_run")
        self.progressBar_run = QtWidgets.QProgressBar(self.tab_run)
        self.progressBar_run.setGeometry(QtCore.QRect(10, 20, 591, 16))
        self.progressBar_run.setProperty("value", 24)
        self.progressBar_run.setObjectName("progressBar_run")
        self.label_run = QtWidgets.QLabel(self.tab_run)
        self.label_run.setGeometry(QtCore.QRect(70, 40, 511, 21))
        self.label_run.setText("")
        self.label_run.setObjectName("label_run")
        self.label_5 = QtWidgets.QLabel(self.tab_run)
        self.label_5.setGeometry(QtCore.QRect(10, 40, 56, 21))
        self.label_5.setObjectName("label_5")
        self.tab_main.addTab(self.tab_run, "")
        self.pushButton_quit = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_quit.setGeometry(QtCore.QRect(540, 280, 71, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_quit.setFont(font)
        self.pushButton_quit.setObjectName("pushButton_quit")
        self.pushButton_stop = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_stop.setGeometry(QtCore.QRect(460, 280, 71, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_stop.setFont(font)
        self.pushButton_stop.setObjectName("pushButton_stop")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 623, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.menubar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        self.tab_main.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Blog Manager"))
        self.label_1.setText(_translate("MainWindow", "ID"))
        self.label_2.setText(_translate("MainWindow", "PW"))
        self.pushButton_login.setText(_translate("MainWindow", "로그인"))
        self.label.setText(_translate("MainWindow", "Naver Login"))
        self.tab_main.setTabText(self.tab_main.indexOf(self.tab_login), _translate("MainWindow", "Login"))
        self.label_3.setText(_translate("MainWindow", "블로그 아이디 수집방법"))
        self.radioButton_category.setText(_translate("MainWindow", "카테고리"))
        self.radioButton_keyword.setText(_translate("MainWindow", "키워드 검색"))
        self.label_4.setText(_translate("MainWindow", "이웃신청 메세지"))
        self.pushButton_run.setText(_translate("MainWindow", "기능 실행"))
        self.label_6.setText(_translate("MainWindow", "댓글 내용"))
        self.tab_main.setTabText(self.tab_main.indexOf(self.tab_configuration), _translate("MainWindow", "Configuration"))
        self.label_5.setText(_translate("MainWindow", "진행상황:"))
        self.tab_main.setTabText(self.tab_main.indexOf(self.tab_run), _translate("MainWindow", "Run"))
        self.pushButton_quit.setText(_translate("MainWindow", "종료"))
        self.pushButton_stop.setText(_translate("MainWindow", "중지"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
