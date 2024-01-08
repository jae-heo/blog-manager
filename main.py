import sys

import requests
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from logic import *
from PyQt5 import uic
from PyQt5.QtWidgets import *
from PyQt5.QtTest import *
from db import DbManager
from PyQt5.QtWidgets import *
from bs4 import BeautifulSoup

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
        self.neighbor_request_progress_bar: QProgressBar
        self.neighbor_request_percent: QLabel
        self.neighbor_request_current_listView: QListView
        self.neighbor_request_today_current_listView: QListView


        self.login_button.clicked.connect(self.login)
        self.collect_by_category_button.clicked.connect(self.collect_by_category)
        self.collect_by_search_button.clicked.connect(self.collect_by_search)
        self.stop_button.clicked.connect(self.stop)


        self.neighbor_request_model = QStandardItemModel()
        self.neighbor_request_current_listView.setModel(self.neighbor_request_model)
        self.neighbor_request_today_model = QStandardItemModel()
        self.neighbor_request_today_current_listView.setModel(self.neighbor_request_today_model)

        self.search_main_category_text: QComboBox
        self.search_main_category_text.addItems(["엔터테인먼트·예술", "생활·노하우·쇼핑", "취미·여가·여행", "지식·동향"])
        self.search_main_category_text.currentIndexChanged.connect(self.update_sub_keyword_combo_box)

        # Initialize sub keyword combo box
        self.search_sub_category_text: QComboBox
        self.search_sub_category_text.addItems(["문학·책", "영화", "미술·디자인", "공연·전시", "음악", "드라마", "스타·연예인", "만화·애니", "방송"])

        self.update_neighbor_request_list_view("TemporaryItem1")
        self.update_neighbor_request_list_view("TemporaryItem2")
        self.update_neighbor_request_list_view("TemporaryItem3")
        self.update_neighbor_request_today_list_view("pgw031203")

        self.show()

        self.reload_timer = QTimer(self)
        self.reload_timer.timeout.connect(self.reload_data)
        self.reload_timer.start(600000)  # 600,000 milliseconds = 10 minutes

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

    def update_progress(self):
        total_true_values = DbManager.get_true_blog_neighbor_request_count(self)
        total_items = 5000
        progress_percentage = (total_true_values / total_items) * 100

        # Set progress bar value
        self.neighbor_request_progress_bar.setValue(int(progress_percentage))

        # Set progress label text
        self.neighbor_request_percent.setText(f"{total_true_values:.2f}% / 5000")

    def update_neighbor_request_list_view(self, username):
        # Create a new item for the list view
        new_item = QStandardItem(f"{username} 신청완료")

        # Add the new item to the model
        self.neighbor_request_model.appendRow(new_item)

        # Limit the number of items to 6
        if self.neighbor_request_model.rowCount() > 12:
            # Remove the first item
            self.neighbor_request_model.removeRow(0)


    def reload_data(self):
        print("데이터 다시 로드 중...")


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        program = Program()
        sys.exit(app.exec_())

    except Exception as e:
        print(e)
