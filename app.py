import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.uic import loadUi
from controller.logic import *
from PyQt5.QtWidgets import *
from PyQt5.QtTest import *
import argparse
from common.custom_class import NMainWindow
from ui.blog_manager import Ui_MainWindow
import requests

license_server_ip = "http://3.35.102.165:8000"
headers = {"secret_code": "onyubabo"}

class BlogManagerApp(NMainWindow, Ui_MainWindow):
# class BlogManagerApp(NMainWindow):
    def __init__(self, mode):
        super().__init__(mode)
        # loadUi("ui/blog_manager.ui", self)
        # ui_initializer = Ui_MainWindow()
        # ui_initializer.setupUi(self)
        self.setupUi(self)
        self.driver = get_chrome_driver()

        self.pushButton_login.clicked.connect(self.login)
        self.mode = mode

        # 종료 및 중지버튼 설정
        self.pushButton_quit.clicked.connect(QApplication.instance().quit)
        self.pushButton_stop.clicked.connect(self.stop_all_thread)
        
        # 탭 관련 설정
        self.tab_main.setTabEnabled(1, False)
        self.tab_main.setTabEnabled(2, False)
        if mode == "DEV":
            self.tab_main.setTabEnabled(1, True)
            self.tab_main.setTabEnabled(2, True)

        # 카테고리 관련 설정
        self.comboBox_mainCategory.addItems(["엔터테인먼트·예술", "생활·노하우·쇼핑", "취미·여가·여행", "지식·동향"])
        self.comboBox_mainCategory.currentIndexChanged.connect(self.update_sub_category)
        self.comboBox_mainCategory.setVisible(False)
        self.comboBox_subCategory.addItems(["문학·책", "영화", "미술·디자인", "공연·전시", "음악", "드라마", "스타·연예인", "만화·애니", "방송"])
        self.comboBox_subCategory.setVisible(False)
        self.lineEdit_keyword.setVisible(False)

        # 라디오 버튼 설정
        self.radioButton_category.clicked.connect(self.category_selected)
        self.radioButton_keyword.clicked.connect(self.keyword_selected)

        # 메인기능 실행 버튼
        self.pushButton_run.clicked.connect(self.run_main)

    def category_selected(self):
        self.comboBox_mainCategory.setVisible(True)
        self.comboBox_subCategory.setVisible(True)
        self.lineEdit_keyword.setVisible(False)

    def keyword_selected(self):
        self.comboBox_mainCategory.setVisible(False)
        self.comboBox_subCategory.setVisible(False)
        self.lineEdit_keyword.setVisible(True)

    def login(self):
        self.username = self.lineEdit_username.text()
        password = self.lineEdit_password.text()
        if self.mode == "DEV":
            self.username = DEV_ID
            password = DEV_PW

        self.lineEdit_username.setDisabled(True)
        self.lineEdit_password.setDisabled(True)
        self.pushButton_login.setDisabled(True)

        login_thread = LoginThread(self.driver, self.username, password, self.username)
        self.thread_dict['login_thread'] = login_thread
        login_thread.finished_signal.connect(self.after_login)
        login_thread.start()
        time.sleep(1)

    def after_login(self, status):
        if status == 0:
            self.tab_main.setTabEnabled(1, True)
            self.tab_main.setCurrentIndex(1)
            show_message(self, "로그인 성공.")
        else:
            show_message(self, "로그인 실패. 다시 로그인 해주세요.")
            self.lineEdit_username.setDisabled(False)
            self.lineEdit_password.setDisabled(False)
            self.pushButton_login.setDisabled(False)

    def run_main(self):
        response = requests.get(f"{license_server_ip}/licenses/{self.username}", headers=headers)
        if response.status_code != 200:
            show_message(self, "라이센스가 없습니다. 프로그램을 종료합니다.")
            QApplication.instance().quit()
        else:
            expiration_date = datetime.strptime(response.json()["expiration_date"], '%Y-%m-%dT%H:%M:%S.%f')
            current_date = datetime.now()
            if expiration_date < current_date:
                show_message(self, "라이센스가 만료되었습니다. 프로그램을 종료합니다.")
                QApplication.instance().quit()

        if not (self.radioButton_category.isChecked() or self.radioButton_keyword.isChecked()):
            show_message(self, "블로그 아이디 수집방법을 선택해주세요.")
            return
        if self.radioButton_keyword.isChecked() and self.lineEdit_keyword.text().strip() == "":
            show_message(self, "검색 키워드를 입력해주세요.")
            return
        if self.plainTextEdit_requestMessage.toPlainText().strip() == "":
            show_message(self, "이웃신청 메세지를 입력해주세요.")
            return
        if self.plainTextEdit_postComment.toPlainText().strip() == "":
            show_message(self, "댓글 내용을 입력해주세요.")
            return

        self.tab_main.setTabEnabled(2, True)
        self.comboBox_mainCategory.setDisabled(True)
        self.comboBox_subCategory.setDisabled(True)
        self.lineEdit_keyword.setDisabled(True)
        self.radioButton_category.setDisabled(True)
        self.radioButton_keyword.setDisabled(True)
        self.plainTextEdit_requestMessage.setDisabled(True)
        self.pushButton_run.setDisabled(True)
        self.plainTextEdit_postComment.setDisabled(True)
        self.tab_main.setCurrentIndex(2)

        self.progressBar_run.setValue(0)

        if self.radioButton_keyword.isChecked():
            keyword = self.lineEdit_keyword.text()
            self.build_thread(
                CollectBlogByKeywordThread(self.driver, keyword, self.username),
                'collect_blogs_by_keyword_thread',
                self.after_collect_by_keyword,
                True)
        if self.radioButton_category.isChecked():
            main_category = self.comboBox_mainCategory.currentText()
            sub_category = self.comboBox_subCategory.currentText()
            self.build_thread(
                CollectBlogByCategoryThread(self.driver, main_category, sub_category, self.username),
                'collect_blogs_by_category_thread',
                self.after_collect_by_category,
                True)
        self.set_current_task_text("블로그 수집중...")

    def after_neighbor_post_collect(self, status):
        if status == 0:
            self.log_to_ui_logger("블로그의 포스트 수집을 완료했습니다.")
            self.neighbor_post_like_comment()

        if status == 1:
            self.log_to_ui_logger("블로그의 포스트 수집이 중지되었습니다.")
            self.after_interrupt()

    def neighbor_post_like_comment(self):
        self.log_to_ui_logger("좋아요 누르기, 댓글 작성을 시작하겠습니다.")

        text = self.plainTextEdit_postComment.toPlainText()

        neighbor_post_comment_thread = NeighborPostCommentLikeThread(self.driver, text, self.username)
        self.thread_dict['neighbor_post_comment_thread'] = neighbor_post_comment_thread
        self.set_current_task_text("좋아요, 댓글기능 작업중...")
        neighbor_post_comment_thread.progress_signal.connect(self.progress_bar_update)
        neighbor_post_comment_thread.log_signal.connect(self.log_to_ui_logger)
        neighbor_post_comment_thread.finished_signal.connect(self.after_neighbor_post_like_comment)
        neighbor_post_comment_thread.start()
        time.sleep(1)

    def after_neighbor_post_like_comment(self, status):
        if status == 0:
            self.log_to_ui_logger("좋아요 누르기, 댓글 작성을 완료했습니다.")
            self.neighbor_request()
        if status == 1:
            self.log_to_ui_logger("좋아요 누르기, 댓글 작성이 중지되었습니다.")
            self.after_interrupt()

    def neighbor_request(self):
        self.log_to_ui_logger("이웃 신청을 시작하겠습니다.")

        request_message = self.plainTextEdit_requestMessage.toPlainText()
        neighbor_request_thread = NeighborRequestThread(self.driver, request_message, self.username)
        self.thread_dict['neighbor_request_thread'] = neighbor_request_thread
        self.set_current_task_text("이웃 신청 작업중...")
        neighbor_request_thread.progress_signal.connect(self.progress_bar_update)
        neighbor_request_thread.log_signal.connect(self.log_to_ui_logger)
        neighbor_request_thread.finished_signal.connect(self.after_neighbor_request)
        neighbor_request_thread.start()
        time.sleep(1)

    def after_neighbor_request(self, status):
        if status == 0:
            self.log_to_ui_logger("이웃 신청을 완료했습니다.")
            self.set_current_task_text("완료")
            self.set_current_task_text("완료")
            
            show_message(self, "프로그램이 끝났습니다. 내일 다시 실행해주세요.")
            
        if status == 1:
            self.log_to_ui_logger("이웃 신청이 중지되었습니다.")
            self.after_interrupt()
            
    def set_current_task_text(self, s):
        self.label_run.setText(s)

    def after_collect_by_keyword(self, status):
        if status == 0:
            self.log_to_ui_logger("블로그 수집을 완료했습니다.")
            self.collect_neighbor_post()

        if status == 1:
            self.log_to_ui_logger("블로그 수집을 중지했습니다.")
            self.after_interrupt()
        
    def after_collect_by_category(self, status):
        if status == 0:
            self.log_to_ui_logger("블로그 수집을 완료했습니다.")
            self.collect_neighbor_post()
        if status == 1:
            self.log_to_ui_logger("블로그 수집을 중지했습니다.")
            self.after_interrupt()

    def collect_neighbor_post(self):
        self.log_to_ui_logger("포스트 수집을 시작하겠습니다.")
        neighbor_post_collect_thread = NeighborPostCollectThread(self.driver, self.username)
        self.thread_dict['neighbor_post_collect_thread'] = neighbor_post_collect_thread

        self.set_current_task_text("포스트 수집중...")
        neighbor_post_collect_thread.log_signal.connect(self.log_to_ui_logger)
        neighbor_post_collect_thread.progress_signal.connect(self.progress_bar_update)
        neighbor_post_collect_thread.finished_signal.connect(self.after_neighbor_post_collect)
        neighbor_post_collect_thread.start()
        time.sleep(1)

    def after_interrupt(self):
        self.comboBox_mainCategory.setDisabled(False)
        self.comboBox_subCategory.setDisabled(False)
        self.lineEdit_keyword.setDisabled(False)
        self.radioButton_category.setDisabled(False)
        self.radioButton_keyword.setDisabled(False)
        self.plainTextEdit_requestMessage.setDisabled(False)
        self.pushButton_run.setDisabled(False)
        self.plainTextEdit_postComment.setDisabled(False)
        self.tab_main.setCurrentIndex(1)
        show_message(self, "기능이 중지되었습니다.")


    def log_to_ui_logger(self, s):
        self.plainTextEdit_run.appendPlainText(f'{s}')

    def progress_bar_update(self, value):
        self.progressBar_run.setValue(int(value * 100))

    def update_sub_category(self):
        self.comboBox_subCategory.clear()
        selected_main_category = self.comboBox_mainCategory.currentText()

        if selected_main_category == "엔터테인먼트·예술":
            self.comboBox_subCategory.addItems(["문학·책", "영화", "미술·디자인", "공연·전시", "음악", "드라마", "스타·연예인", "만화·애니", "방송"])
        elif selected_main_category == "생활·노하우·쇼핑":
            self.comboBox_subCategory.addItems(["일상·생각", "육아·결혼", "반려동물", "좋은글·이미지", "패션·미용", "인테리어·DIY", "요리·레시피", "상품리뷰", "원예·재배"])
        elif selected_main_category == "취미·여가·여행":
            self.comboBox_subCategory.addItems(["게임", "스포츠", "사진", "자동차", "취미", "국내여행", "세계여행", "맛집"])
        elif selected_main_category == "지식·동향":
            self.comboBox_subCategory.addItems(["IT·컴퓨터", "사회·정치", "건강·의학", "비즈니스·경제", "어학·외국어", "교육·학문"])
        else:
            self.comboBox_subCategory.addItems(["All"])
    
    def stop_all_thread(self):
        for _, value in self.thread_dict.items():
            value.interrupt_signal = True


def main():
    parser = argparse.ArgumentParser(description='Add two numbers.')
    parser.add_argument('--mode', type=str, help='PROD or DEV', default="PROD")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    main_window = BlogManagerApp(args.mode)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()