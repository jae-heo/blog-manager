import sys

from logic import *
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtTest import *
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import sqlite3

class Program(QMainWindow, uic.loadUiType("TestUi.ui")[0]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init()

    def init(self):
        self.run_button: QPushButton
        self.stop_button: QPushButton

        self.run_button.clicked.connect(self.run)
        self.stop_button.clicked.connect(self.stop)

        self.show()

    def stop(self):
        self.close()

    def run(self):
        try:
            # 1 프로그램에서 입력된 정보 네 가지를 가져온다. (아이디 비밀번호 검색어 서이추메세지)
            username, password, search_keyword, neighbor_request_message = self.get_inputs()
            print(username)
            driver = get_chrome_driver()
            # 2 네이버 로그인을 실시한다.
            naver_login(driver, DEV_ID, DEV_PW)

        except Exception as e:
            logging.getLogger("main").error(e)

    def get_inputs(self):
        self.username_text: QLineEdit
        self.password_text: QLineEdit
        self.neighbor_request_message_text: QLineEdit
        self.search_keyword_text: QLineEdit

        username = self.username_text.text()
        password = self.password_text.text()
        search_keyword = self.search_keyword_text.text()
        neighbor_request_message = self.neighbor_request_message_text.text()
        if empty(username) or empty(password) or empty(neighbor_request_message) or empty(search_keyword):
            # 이곳에서 에러메세지 출력
            raise Exception("빈칸이 있습니다.")
        else:
            return username, password, search_keyword, neighbor_request_message


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        program = Program()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
