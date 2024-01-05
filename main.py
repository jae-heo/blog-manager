import sys

from logic import *
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtTest import *

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

        self.search_main_keyword_text: QComboBox
        self.search_main_keyword_text.addItems(["엔터테인먼트·예술", "생활·노하우·쇼핑", "취미·여가·여행", "지식·동향"])
        self.search_main_keyword_text.currentIndexChanged.connect(self.update_sub_keyword_combo_box)

        # Initialize sub keyword combo box
        self.search_sub_keyword_text: QComboBox
        self.search_sub_keyword_text.addItems(["문학·책", "영화", "미술·디자인", "공연·전시", "음악", "드라마", "스타·연예인", "만화·애니", "방송"])

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

    def update_sub_keyword_combo_box(self):
        # Clear the current items in the sub-keyword combo box
        self.search_sub_keyword_text.clear()

        # Get the selected main keyword
        selected_main_keyword = self.search_main_keyword_text.currentText()

        if selected_main_keyword == "엔터테인먼트·예술":
            self.search_sub_keyword_text.addItems(["문학·책", "영화", "미술·디자인", "공연·전시", "음악", "드라마", "스타·연예인", "만화·애니", "방송"])
        elif selected_main_keyword == "생활·노하우·쇼핑":
            self.search_sub_keyword_text.addItems(["일상·생각", "육아·결혼", "반려동물", "좋은글·이미지", "패션·미용", "인테리어·DIY", "요리·레시피", "상품리뷰", "원예·재배"])
        elif selected_main_keyword == "취미·여가·여행":
            self.search_sub_keyword_text.addItems(["게임", "스포츠", "사진", "자동차", "취미", "국내여행", "세계여행", "맛집"])
        elif selected_main_keyword == "지식·동향":
            self.search_sub_keyword_text.addItems(["IT·컴퓨터", "사회·정치", "건강·의학", "비즈니스·경제", "어학·외국어", "교육·학문"])
        else:
            # Add default items or handle other cases
            self.search_sub_keyword_text.addItems(["All"])

    def get_inputs(self):
        self.username_text: QLineEdit
        self.password_text: QLineEdit
        self.neighbor_request_message_text: QLineEdit
        self.search_main_keyword_text: QComboBox
        self.search_sub_keyword_text: QComboBox

        self.search_main_keyword_text.addItems(["Entertainment", "Sports"])


        username = self.username_text.text()
        password = self.password_text.text()
        search_main_keyword = self.search_main_keyword_text.currentText()
        search_sub_keyword = self.search_sub_keyword_text.currentText()
        neighbor_request_message = self.neighbor_request_message_text.text()
        if empty(username) or empty(password) or empty(neighbor_request_message) or empty(search_main_keyword) or empty(search_sub_keyword):
            # 이곳에서 에러메세지 출력
            raise Exception("빈칸이 있습니다.")
        else:
            return username, password, search_main_keyword, search_sub_keyword, neighbor_request_message


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        program = Program()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
