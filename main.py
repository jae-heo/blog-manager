import sys

from PyQt5.QtGui import QStandardItemModel, QStandardItem

from logic import *
from PyQt5 import uic
# from post_save import *
from PyQt5.QtWidgets import *
from PyQt5.QtTest import *
from db import DbManager
from PyQt5.QtWidgets import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import NoSuchElementException
from selenium.webdriver import *
from selenium.webdriver.common.by import By


# 개발 해야할것
# 1. 기능 작동시 중지/종료 빼고 전부 Disable 하기
# 2. 사용자가 기능이 작동중인 것을 알 수 있도록 하단에 ~~기능 작동중 . .. ... 등을 만들어야함
class Program(QMainWindow, uic.loadUiType("requirement.ui")[0]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.init()
        self.driver = get_chrome_driver()
        self.thread_dict = {}

    def init(self):
        self.login_button: QPushButton
        self.collect_by_search_button: QPushButton
        self.collect_by_category_button: QPushButton
        self.stop_button: QPushButton
        self.pause_button: QPushButton
        self.test_button: QPushButton
        self.post_save_button: QPushButton
        self.neighbor_request_button: QPushButton
        self.neighbor_request_progress_bar: QProgressBar
        self.neighbor_request_percent: QLabel
        self.neighbor_request_today_current_listView: QListView
        self.neighbor_request_current_listView: QListView

        self.neighbor_request_model = QStandardItemModel()
        self.neighbor_request_current_listView.setModel(self.neighbor_request_model)

        self.login_button.clicked.connect(self.login)
        self.collect_by_category_button.clicked.connect(self.collect_by_category)
        self.collect_by_search_button.clicked.connect(self.collect_by_search)
        self.stop_button.clicked.connect(self.stop)
        self.pause_button.clicked.connect(self.pause)
        self.test_button.clicked.connect(self.today_neighbor_request_current)
        self.neighbor_request_button.clicked.connect(self.neighbor_request)
        # self.post_save_button.clicked.connect(self.post_save)
        self.post_save_button.setVisible(False)
        self.textBrowser.setVisible(False)

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
        self.show()

    def stop(self):
        print("프로그램이 종료됩니다.")
        self.driver.quit()
        self.close()
        print("프로그램이 종료되었습니다.")
            
    def pause(self):
        for thread_name in self.thread_dict.keys():
            self.thread_dict[thread_name].interrupt_signal = True

    def login(self):
        try:
            print('login_begins')
            self.username_text: QLineEdit
            self.password_text: QLineEdit

            username = self.username_text.text()
            password = self.password_text.text()

            username = DEV_ID
            password = DEV_PW
            self.username = username

            login_thread = LoginThread(self.driver, username, password, self.username)
            # self.thread_dict['login_thread'] = login_thread
            # login_thread.finished_signal.connect(lambda: self.after_login(login_thread.blog_exist))
            
            login_thread.start()
            time.sleep(1)
            print('login_ends')
        except Exception as e:
            logging.getLogger("main").error(e)

    def after_login(self, blog_exist):
        # 만약 사용자가 첫 로그인이라면
        if not blog_exist:
            print('initializing begins')
            initialize_thread = InitializeThread(self.driver, self.username, self.username)
            self.thread_dict['initialize_thread'] = initialize_thread
            initialize_thread.finished_signal.connect(lambda: self.after_initialize())
            initialize_thread.start()
            time.sleep(1)
        else:
            self.today_neighbor_request_current()
            self.reload_data()
            pass
            
    def after_initialize(self):
        self.today_neighbor_request_current()
        self.reload_data()
        print('initializing ends')

    def collect_by_search(self):
        try:
            self.search_keyword_text: QLineEdit
            search_keyword = self.search_keyword_text.text()

            collect_blogs_by_search_thread = CollectBlogBySearchThread(self.driver, search_keyword, self.username)
            self.thread_dict['collect_blogs_by_search_thread'] = collect_blogs_by_search_thread
            collect_blogs_by_search_thread.finished_signal.connect(lambda: self.today_neighbor_request_current())
            collect_blogs_by_search_thread.start()
            time.sleep(1)
        except Exception as e:
            logging.getLogger("main").error(e)
        
    def collect_by_category(self):
        try:
            self.search_main_category_text: QComboBox
            self.search_sub_category_text: QComboBox
            main_category = self.search_main_category_text.currentText()
            sub_category = self.search_sub_category_text.currentText()

            collect_blogs_by_category_thread = CollectBlogByCategoryThread(self.driver, main_category, sub_category, self.username)
            self.thread_dict['collect_blogs_by_category_thread'] = collect_blogs_by_category_thread
            collect_blogs_by_category_thread.finished_signal.connect(lambda: self.today_neighbor_request_current())
            collect_blogs_by_category_thread.start()
            time.sleep(1)
        except Exception as e:
            logging.getLogger("main").error(e)

    def neighbor_request(self):
        try:
            self.neighbor_request_message: QLineEdit
            neighbor_request_message = self.neighbor_request_message.text()          
            neighbor_request_thread = NeighborRequestThread(self.driver, neighbor_request_message, self.username)
            self.thread_dict['neighbor_request_thread'] = neighbor_request_thread
            # neighbor_request_thread.finished_signal.connect(lambda: self.after_neighbor_request())
            neighbor_request_thread.start()
            time.sleep(1)
        except Exception as e:
            logging.getLogger("main").error(e)

    def after_neighbor_request(self):
        self.neighbor_post_collect()

    def neighbor_post_collect(self):
        try:
            neighbor_post_collect_thread = NeighborPostCollectThread(self.driver, self.username)
            self.thread_dict['neighbor_post_collect_thread'] = neighbor_post_collect_thread
            neighbor_post_collect_thread.finished_signal.connect(self.after_neighbor_post_collect)
            neighbor_post_collect_thread.start()
            time.sleep(1)
        except Exception as e:
            logging.getLogger("main").error(e)

    def after_neighbor_post_collect(self):
        self.neighbor_post_comment_like()

    def neighbor_post_comment_like(self):
        try:
            neighbor_post_comment_thread = NeighborPostCommentLikeThread(self.driver, '저희 이웃 해요 ^^', self.username)
            self.thread_dict['neighbor_post_comment_thread'] = neighbor_post_comment_thread
            neighbor_post_comment_thread.finished_signal.connect()
            neighbor_post_comment_thread.start()
            time.sleep(1)
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
        try:
            db_instance = DbManager(self.username)
            all_blogs = db_instance.get_all_blogs()
            current_date = datetime.now().strftime('%Y-%m-%d')

            # neighbor_request_date가 현재 날짜와 today_list_update가 0인 블로그 필터링
            filtered_blogs = [
                blog for blog in all_blogs
                if blog.get("neighbor_request_date") == current_date and blog.get("today_list_update") == 0
            ]

            # 업데이트할 블로그가 없을 경우 예외처리
            if not filtered_blogs:
                print("업데이트할 블로그가 없습니다.")
                return

            # 업데이트할 블로그들에 대해 처리
            for blog in filtered_blogs:
                self.update_neighbor_request_list_view(blog.get("blog_id"))

            # 프로그레스 업데이트
            self.update_progress()
            print("데이터 다시 로드 중...")

        except Exception as e:
            print(f"Error during data reload: {e}")


    def today_neighbor_request_current(self):
        try:
            current_time = datetime.now().strftime('%H:%M:%S')
            url = f'https://admin.blog.naver.com/BuddyGroupManage.naver?blogId={self.username}'
            self.driver.get(url)
            # tr 요소들을 XPath를 통해 가져옵니다.
            tr_elements = self.driver.find_elements(By.XPATH, '//*[@id="wrap"]/table/tbody/tr')
            # tr 개수를 출력합니다.
            tr_count = len(tr_elements)
            print(f"Number of tr elements: {tr_count}")
            total_value = 0

            for i in range(tr_count):
                xpath = f'//*[@id="wrap"]/table/tbody/tr[{i + 1}]/td[4]/span'
                span_element = self.driver.find_element(By.XPATH, xpath)
                value = int(span_element.text)
                total_value += value

            new_item = QStandardItem(f"{current_time} : {total_value}")
            self.neighbor_request_today_model.appendRow(new_item)
            if current_time == "00-00-00":
                self.neighbor_request_today_model.clear()
            #바
            total_items = 5000.0
            progress_percentage = (total_value / total_items) * 100
            # Set progress bar value
            self.neighbor_request_progress_bar.setValue(int(progress_percentage))
            # Set progress label text
            self.neighbor_request_percent.setText(f"{total_value} / 5000")
        except Exception as e:
            print(f"Error: {e}, 여기임")

        close_all_tabs(self.driver)

    # def post_save(self):
    #     try:
    #         self.search_keyword_text: QLineEdit
    #         search_keyword = self.search_keyword_text.text()

    #         post_save_thread = PostSaveThread(self.driver, search_keyword, self.username)
    #         self.thread_dict['post_save_thread'] =post_save_thread
    #         post_save_thread.start()
    #     except Exception as e:
    #         logging.getLogger("main").error(e)



if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        program = Program()
        sys.exit(app.exec_())

    except Exception as e:
        print(e)
