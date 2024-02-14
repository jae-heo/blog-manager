from common.util_function import *
import time

from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import *
from PyQt5.QtTest import *
from PyQt5.QtCore import QThread, pyqtSignal

class NThread(QThread):
    finished_signal = pyqtSignal(int)
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(float)
    interrupt_signal = False

    def __init__(self, parent=None):
        super().__init__(parent)

    def finish(self):
        self.finished_signal.emit(0)
        close_all_tabs(self.driver)

    def interrupt(self):
        self.finished_signal.emit(1)
        close_all_tabs(self.driver)
    
    def log_ui(self, s):
        self.log_signal.emit(s)

    def set_progress(self, value):
        self.progress_signal.emit(value)

class NMainWindow(QMainWindow):
    thread_dict = {}

    def __init__(self, mode:str):
        super().__init__()

        self.mode = mode

        self.tab_main: QTabWidget

        self.pushButton_quit: QPushButton
        self.pushButton_stop: QPushButton
        self.pushButton_run: QPushButton
        self.pushButton_login: QPushButton

        self.comboBox_mainCategory: QComboBox
        self.comboBox_subCategory: QComboBox

        self.radioButton_category:QRadioButton
        self.radioButton_keyword:QRadioButton

        self.lineEdit_keyword: QLineEdit
        self.lineEdit_username: QLineEdit
        self.lineEdit_password: QLineEdit

        self.comboBox_mainCategory: QComboBox
        self.comboBox_subCategory: QComboBox

        self.progressBar_run: QProgressBar

        self.label_run:QLabel

        self.plainTextEdit_run: QPlainTextEdit
        self.plainTextEdit_postComment: QPlainTextEdit
        self.plainTextEdit_requestMessage: QPlainTextEdit

    def build_thread(self, thread: NThread, name, finished_function, start = False):
        self.thread_dict[name] = thread
        thread.progress_signal.connect(self.progress_bar_update)
        thread.log_signal.connect(self.log_to_ui_logger)
        thread.finished_signal.connect(finished_function)
        if start:
            thread.start()
            time.sleep(1)
        return thread
    

