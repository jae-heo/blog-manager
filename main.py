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
        self.driver = get_chrome_driver()

    def init(self):
        self.login_button: QPushButton
        self.collect_by_search_button: QPushButton
        self.collect_by_category_button: QPushButton
        self.stop_button: QPushButton

        self.login_button.clicked.connect(self.login)
        self.collect_by_category_button.clicked.connect(self.collect_by_category)
        self.collect_by_search_button.clicked.connect(self.collect_by_search)
        self.stop_button.clicked.connect(self.stop)

        self.search_main_category_text: QComboBox
        self.search_main_category_text.addItems(["엔터테인먼트·예술", "생활·노하우·쇼핑", "취미·여가·여행", "지식·동향"])
        self.search_main_category_text.currentIndexChanged.connect(self.update_sub_keyword_combo_box)

        # Initialize sub keyword combo box
        self.search_sub_category_text: QComboBox
        self.search_sub_category_text.addItems(["문학·책", "영화", "미술·디자인", "공연·전시", "음악", "드라마", "스타·연예인", "만화·애니", "방송"])

        self.show()

    def stop(self):
        self.close()

    def login(self):
        try:
            self.username_text: QLineEdit
            self.password_text: QLineEdit

            username = self.username_text.text()
            password = self.password_text.text()
            naver_login(self.driver, DEV_ID, DEV_PW)

        except Exception as e:
            logging.getLogger("main").error(e)

    def collect_by_search(self):
        try:
            self.search_keyword_text: QLineEdit
            search_keyword = self.search_keyword_text.text()
            get_blogs_by_search(self.driver, search_keyword)
        except Exception as e:
            logging.getLogger("main").error(e)
        
    def collect_by_category(self):
        try:
            self.search_main_category_text: QComboBox
            self.search_sub_category_text: QComboBox
            main_category = self.search_main_category_text.currentText()
            sub_category = self.search_sub_category_text.currentText()
            get_blogs_by_category(self.driver, main_category, sub_category)
        except Exception as e:
            logging.getLogger("main").error(e)

    def update_sub_keyword_combo_box(self):
        # Clear the current items in the sub-keyword combo box
        self.search_sub_category_text.clear()

        # Get the selected main keyword
        selected_main_category = self.search_main_category_text.currentText()

        if selected_main_category == "엔터테인먼트·예술":
            self.search_sub_category_text.addItems(["문학·책", "영화", "미술·디자인", "공연·전시", "음악", "드라마", "스타·연예인", "만화·애니", "방송"])
        elif selected_main_category == "생활·노하우·쇼핑":
            self.search_sub_category_text.addItems(["일상·생각", "육아·결혼", "반려동물", "좋은글·이미지", "패션·미용", "인테리어·DIY", "요리·레시피", "상품리뷰", "원예·재배"])
        elif selected_main_category == "취미·여가·여행":
            self.search_sub_category_text.addItems(["게임", "스포츠", "사진", "자동차", "취미", "국내여행", "세계여행", "맛집"])
        elif selected_main_category == "지식·동향":
            self.search_sub_category_text.addItems(["IT·컴퓨터", "사회·정치", "건강·의학", "비즈니스·경제", "어학·외국어", "교육·학문"])
        else:
            # Add default items or handle other cases
            self.search_sub_category_text.addItems(["All"])


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        program = Program()
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
