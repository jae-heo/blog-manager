import logging
from urllib.parse import urlparse, parse_qs

from selenium.webdriver.common.alert import Alert
#gh
from const import *
from custom_func import *

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal

from db import DbManager
from datetime import datetime, timedelta


class LoginThread(QThread):
    finished_signal = pyqtSignal()
    interrupt_signal = False

    def __init__(self, driver, username, password, db_name, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.username = username
        self.password = password
        self.db_name = db_name
        self.blog_exist = False

    def run(self):
        db_manager = DbManager(self.db_name)
        open_new_window(self.driver)
        get_page(self.driver, NAVER_LOGIN_URL)  

        id_text_field = self.driver.find_element(By.CSS_SELECTOR, '#id')
        key_in(id_text_field, self.username)

        pw_text_field = self.driver.find_element(By.CSS_SELECTOR, '#pw')
        key_in(pw_text_field, self.password)

        login_button = self.driver.find_element(By.XPATH, '//*[@id="log.login"]')
        click(login_button)

        close_current_window(self.driver)

        if db_manager.get_all_blogs():
            self.blog_exist = True

        self.finished_signal.emit()

class InitializeThread(QThread):
    finished_signal = pyqtSignal()
    interrupt_signal = False

    def __init__(self, driver, username, db_name, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.username = username
        self.db_name = db_name

    def run(self):
        db_manager = DbManager(self.db_name)
        open_new_window(self.driver)
        url = f"https://admin.blog.naver.com/BuddyListManage.naver?blogId={self.username}"
        get_page(self.driver, url)
        buddy_ids = []
        while True:
            if self.interrupt_signal:
                print("InitializeThread interrupted.")
                break

            # 검색결과의 페이지 별 순회
            current_page_element = self.driver.find_element(By.CSS_SELECTOR, '.paginate .paginate_re strong')
            current_page_text = current_page_element.text
            current_page_text_copy = current_page_text
            active_page_buttons = self.driver.find_elements(By.CSS_SELECTOR, '.paginate .paginate_re a')

            # 로직
            buddies = self.driver.find_elements(By.CSS_SELECTOR, ".buddy .ellipsis2 a")
            for buddy in buddies:
                blog_id = buddy.get_attribute("href").split("/")[3]
                buddy_ids.append(blog_id)

            for page_button in active_page_buttons:
                if int(page_button.text) == int(current_page_text) + 1:
                    click(page_button)
                    current_page_text = self.driver.find_element(By.CSS_SELECTOR, '.paginate .paginate_re strong').text
            
            # 만약 다음 페이지가 없다면
            if current_page_text == current_page_text_copy:
                break

        db_manager.insert_blogs_record_with_ids(buddy_ids)
        blogs = db_manager.get_all_blogs()
        for blog in blogs:
            created_date = blog['created_date']
            created_date = datetime.strptime(created_date, '%Y-%m-%d %H:%M:%S')
            blog['created_date'] = created_date - timedelta(days=1)
            db_manager.update_blog(blog)
        close_current_window(self.driver)
        self.finished_signal.emit()


class CollectBlogBySearchThread(QThread):
    finished_signal = pyqtSignal()

    interrupt_signal = False

    def __init__(self, driver, search_keyword, db_name, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.search_keyword = search_keyword
        self.db_name = db_name

    def run(self):
        db_manager = DbManager(self.db_name)

        count = 0
        daily_limit = 100
        today = datetime.now().date()
        blogs = db_manager.get_all_blogs()
        if blogs:
            for blog in blogs:
                blog_date = datetime.strptime(blog['created_date'], "%Y-%m-%d %H:%M:%S").date()
                if today == blog_date:
                    count += 1
        if count >= daily_limit:
            # 이곳에서도, 100명을 추가했다고 알림을 보내야함.
            print('오늘 수집한 블로그가 100개를 넘었습니다.')
            close_all_tabs(self.driver)
            return
        
        open_new_window(self.driver)
        get_page(self.driver, BLOG_MAIN_URL)

        search_bar_element = self.driver.find_element(By.XPATH, '//*[@id="header"]/div[1]/div/div[2]/form/fieldset/div/input')
        key_in(search_bar_element, self.search_keyword)
        search_button_element = self.driver.find_element(By.XPATH, '//*[@id="header"]/div[1]/div/div[2]/form/fieldset/a[1]')
        click(search_button_element)

        while True:
            # 검색결과의 페이지 별 순회
            for i in range(0, len(self.driver.find_elements(By.CSS_SELECTOR, ".pagination span a"))):
                # 검색결과 내 Blog를 순회
                for author in self.driver.find_elements(By.CSS_SELECTOR, ".writer_info .author"):
                    if self.interrupt_signal:
                        close_all_tabs(self.driver)
                        return

                    blog_id = author.get_attribute("href").split("/")[3]
                    # 만약 블로그가 서이추가 가능한 상태면 DB에 추가한다.
                    blog_url = "https://m.blog.naver.com/" + blog_id
                    open_new_window(self.driver)
                    get_page(self.driver, blog_url)
                    try:
                        add_neighbor_button = self.driver.find_element(By.CLASS_NAME, "add_buddy_btn__oGR_B")
                        click(add_neighbor_button)
                        both_buddy_radio = self.driver.find_element(By.ID, "bothBuddyRadio")
                        # 만약 서이추가 가능한 사람일 경우
                        if both_buddy_radio.get_attribute("ng-disabled") == "false":
                            if db_manager.insert_blog_record_with_id(blog_id):
                                count += 1

                            if count >= daily_limit:
                                close_all_tabs(self.driver)
                                print("오늘 100명을 모두 수집했습니다.")
                                return
                    except Exception as e:
                        pass
                    close_current_window(self.driver)

                if (i + 1) != len(self.driver.find_elements(By.CSS_SELECTOR, ".pagination span a")):
                    page_next_number_button = self.driver.find_elements(By.CSS_SELECTOR, ".pagination span a")[i + 1]
                    click(page_next_number_button)
            try:
                page_next_button = self.driver.find_element(By.CSS_SELECTOR, ".pagination .button_next")
                click(page_next_button)
            except NoSuchElementException as e:
                logging.getLogger("main").info("블로그의 모든 글을 탐색했습니다.")
                break
        close_current_window(self.driver)


class CollectBlogByCategoryThread(QThread):
    finished_signal = pyqtSignal()
    interrupt_signal = False

    def __init__(self, driver, main_category, sub_category, db_name, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.main_category = main_category
        self.sub_category = sub_category
        self.db_name = db_name

    def run(self):
        db_manager = DbManager(self.db_name)

        count = 0
        daily_limit = 103

        today = datetime.now().date()
        blogs = db_manager.get_all_blogs()
        if blogs:
            for blog in blogs:
                blog_date = datetime.strptime(blog['created_date'], "%Y-%m-%d %H:%M:%S").date()
                if today == blog_date:
                    count += 1

        if count >= daily_limit:
            close_all_tabs(self.driver)
            print('오늘 수집한 블로그가 100개를 넘었습니다.')
            # 이곳에서도, 100명을 추가했다고 알림을 보내야함.
            return

        open_new_window(self.driver)
        get_page(self.driver, BLOG_MAIN_URL)

        category_discovery_button = self.driver.find_element(By.XPATH, '//*[@id="lnbMenu"]/a[2]')
        click(category_discovery_button)

        main_category_xpath = f"//a[contains(@bg-nclick, '{MAIN_CATEGORIES[self.main_category]}')]"
        main_category_element = WebDriverWait(self.driver, 1000).until(
            EC.element_to_be_clickable((By.XPATH, main_category_xpath))
        )
        main_category_element.click()
        rand_sleep(300, 500)
        sub_category_css_selector = f".navigator_category_sub [bg-nclick='{SUB_CATEGORIES[self.sub_category]}']"
        sub_category_element = WebDriverWait(self.driver, 1000).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, sub_category_css_selector))
        )
        click(sub_category_element)

        while True:
            # 검색결과의 페이지 별 순회
            for i in range(0, len(self.driver.find_elements(By.CSS_SELECTOR, ".pagination span a"))):
                # 검색결과 내 Blog를 순회
                for post_index in range(len(self.driver.find_elements(By.CSS_SELECTOR,
                                                                ".list_post_article .multi_pic .info_post .desc .desc_inner"))):
                    if self.interrupt_signal:
                        close_all_tabs(self.driver)
                        return                     
                    post = self.driver.find_elements(By.CSS_SELECTOR, ".list_post_article .multi_pic .info_post .desc .desc_inner")[
                        post_index]
                    post_link_splat = post.get_attribute("href").split("/")
                    blog_id = post_link_splat[3]
                    post_id = post_link_splat[4]
                    liked_link = f'https://m.blog.naver.com/SympathyHistoryList.naver?blogId={blog_id}&logNo={post_id}&categoryId=POST'
                    open_new_window(self.driver)
                    get_page(self.driver, liked_link)
                    rand_sleep(3000, 5000)
                    for blog_description in self.driver.find_elements(By.CSS_SELECTOR,
                                                                ".sympathy_item___b3xy .bloger_area___eCA_ .link__D9GoZ"):
                        if self.interrupt_signal:
                            close_all_tabs(self.driver)
                            return                        
                        blog_id = blog_description.get_attribute("href").split("/")[3]
                        # 만약 블로그가 서이추가 가능한 상태면 DB에 추가한다.
                        blog_url = "https://m.blog.naver.com/" + blog_id
                        open_new_window(self.driver)
                        get_page(self.driver, blog_url)
                        try:
                            add_neighbor_button = self.driver.find_element(By.CLASS_NAME, "add_buddy_btn__oGR_B")
                            click(add_neighbor_button)
                            both_buddy_radio = self.driver.find_element(By.ID, "bothBuddyRadio")
                            # 만약 서이추가 가능한 사람일 경우
                            if both_buddy_radio.get_attribute("ng-disabled") == "false":
                                if db_manager.insert_blog_record_with_id(blog_id):
                                    count += 1
                                
                                if count >= daily_limit:
                                    close_all_tabs(self.driver)
                                    print("오늘 100명을 모두 수집했습니다.")
                                    return
                        except Exception as e:
                            # 이 경우는 이미 이웃
                            pass
                        # 서로이웃 확인했던 창 끄기.
                        close_current_window(self.driver)
                    # 포스트 공감창 끄기
                    close_current_window(self.driver)
                if (i + 1) < len(self.driver.find_elements(By.CSS_SELECTOR, ".pagination span a")):
                    page_next_number_button = self.driver.find_elements(By.CSS_SELECTOR, ".pagination span a")[i + 1]
                    click(page_next_number_button)
            try:
                page_next_button = self.driver.find_element(By.CSS_SELECTOR, ".pagination .button_next")
                click(page_next_button)
            except NoSuchElementException as e:
                logging.getLogger("main").info("카테고리의 모든 글을 탐색했습니다.")
                break

class NeighborRequestThread(QThread):
    finished_signal = pyqtSignal()
    interrupt_signal = False

    def __init__(self, driver, neighbor_request_message, db_name, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.neighbor_request_message = neighbor_request_message
        self.db_name = db_name
        self.blog_exist = False

    def run(self):
        db_manager = DbManager(self.db_name)
        blogs = db_manager.get_all_blogs()
        request_count = 0
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        date = datetime.now().date()
        if blogs:
            for blog in blogs:
                if blog['neighbor_request_date']:
                    neighbor_request_date = datetime.strptime(blog['neighbor_request_date'], "%Y-%m-%d %H:%M:%S")
                    if neighbor_request_date == date:
                        request_count += 1

            for blog in blogs:
                if self.interrupt_signal or request_count >= 100:
                        close_all_tabs(self.driver)
                        return 
                # 현재 이웃신청이 되지 않은 블로그 중
                if blog["neighbor_request_current"] == 0 and blog["neighbor_request_rmv"] != 1:
                    # 이웃신청 조건이 완료된 경우
                    # if blog["like_count"] >= 5 and blog["comment_count"] >= 5:
                    blog_url = "https://m.blog.naver.com/" + blog['blog_id']
                    open_new_window(self.driver)
                    get_page(self.driver, blog_url)
                    add_neighbor_button = self.driver.find_element(By.CLASS_NAME, "add_buddy_btn__oGR_B")
                    click(add_neighbor_button)
                    try:
                        both_buddy_radio = self.driver.find_element(By.ID, "bothBuddyRadio")
                        # 만약 서이추가 가능한 사람일 경우
                        if both_buddy_radio.get_attribute("ng-disabled") == "false":
                            # 서이추 버튼 클릭
                            click(both_buddy_radio)
                            # 서이추 메세지 입력
                            neighbor_request_message_text_area = self.driver.find_element(By.CSS_SELECTOR, ".add_msg textarea")
                            clear(neighbor_request_message_text_area)
                            key_in(neighbor_request_message_text_area, self.neighbor_request_message)
                            neighbor_request_button = self.driver.find_element(By.CLASS_NAME, "btn_ok")
                            click(neighbor_request_button)

                            blog["neighbor_request_current"] = 1
                            blog["neighbor_request_date"] = now
                            db_manager.update_blog(blog)
                            request_count += 1
                    except Exception as e:
                        pass
        close_all_tabs(self.driver)
        self.finished_signal.emit()

class NeighborPostCollectThread(QThread):
    finished_signal = pyqtSignal()
    interrupt_signal = False

    def __init__(self, driver, db_name, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.db_name = db_name

    def run(self):
        db_manager = DbManager(self.db_name)
        all_blogs = db_manager.get_all_blogs()
        all_posts = db_manager.get_all_blog_posts()

        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        neighbor_request_count = 0
        today = datetime.now().date()
        blogs = db_manager.get_all_blogs()
        if blogs:
            for blog in blogs:
                blog_date = datetime.strptime(blog['neighbor_request_date'], "%Y-%m-%d %H:%M:%S")
                if today == blog_date:
                    neighbor_request_count += 1

        for blog in all_blogs:
            if self.interrupt_signal:
                close_all_tabs(self.driver)
                return
            # 현재 이웃신청이 되지 않은 블로그 중
            if not blog["neighbor_request_current"]:
                # 블로그를 수집해야 하는 경우
                if self.interrupt_signal:
                    close_all_tabs(self.driver)
                    return
                filtered_posts = [
                    post for post in all_posts
                    if post.get("blog_post_id") == blog
                ]

                current_xpath = '//*[@id="contentslist_block"]/div[2]/div/div[2]/ul/li[1]'
                blog_url = f"https://m.blog.naver.com/{blog['blog_id']}"

                if filtered_posts:
                    while True:
                        if self.interrupt_signal:
                            close_all_tabs(self.driver)
                            return
                        recent_post_id = get_post_id(self.driver, blog_url, current_xpath)
                        for post in filtered_posts:
                            if recent_post_id == post.get("post_id"):
                                current_index = int(current_xpath.split('/')[-1][:-1])
                                new_xpath = f'//*[@id="contentslist_block"]/div[2]/div/div[2]/ul/li[{current_index}]'
                                # 다음 검사를 위해 current_xpath 갱신
                                current_xpath = new_xpath
                                break
                        else:
                            if not filtered_posts:  # 만약 필터링된 포스터 테이블이 비어 있다면 새로운 post_id를 추가
                                new_post = {'blog_post_id': blog['blog_id'], 'post_id': recent_post_id, 'is_liked': 0, 'written_comment': ''}
                                db_manager.update_blog(new_post)

                            self.driver.get(blog_url + '/' + recent_post_id)
                            self.driver.find_element(By.XPATH,
                                                '//*[@id="contentslist_block"]/div[2]/div/div[2]/ul/li[1]').click()

                            # 좋아요 버튼 확인
                            rand_sleep(450, 550)
                            try:
                                if self.interrupt_signal:
                                    close_all_tabs(self.driver)
                                    return
                                is_like = self.driver.find_element(by='xpath',
                                                            value='//*[@id="body"]/div[10]/div/div[1]/div/div/a').get_attribute(
                                    'aria-pressed')  # 좋아요 버튼 상태 확인
                                # print(is_like)
                            except Exception:  # 간혹 공감 버튼 자체가 없는 게시글이 존재함
                                print('공감 버튼 없음')
                                continue
                            if is_like == 0:  # 좋아요 버튼 상태가 안눌러져있는 상태일 경우에만 좋아요 버튼 클릭
                                self.driver.find_element(by='xpath',
                                                    value='//*[@id="body"]/div[10]/div/div[1]/div/div/a/span').click()  # 하트 클릭
                                rand_sleep(450, 550)
                                blog['like_count'] += 1
                                post['is_liked'] = 1

                            if self.interrupt_signal:
                                close_all_tabs(self.driver)
                                return

                            # 댓글 확인
                            # 클릭할 부분을 xpath로 찾아서 클릭
                            try:
                                click_button = self.driver.find_element(By.XPATH, '//*[@id="body"]/div[10]/div/div[2]/a[1]')
                                click_button.click()

                                # 댓글 입력란을 찾아서 내용 입력
                                comment_input_1 = self.driver.find_element(By.XPATH,
                                                                    '//*[@id="naverComment"]/div/div[7]/div[1]/form/fieldset/div/div/div[2]/div/label')
                                click(comment_input_1)

                                rand_sleep(450, 550)
                                comment_input = self.driver.find_element(By.XPATH, '//*[@id="naverComment__write_textarea"]')
                                click(comment_input)
                                rand_sleep(450, 550)
                                comment_input.send_keys("좋은 글 감사합니다!")  # 원하는 댓글 내용으로 수정
                                blog['comment_count'] += 1
                                post['written_comment'] = comment_input.get_attribute('좋은 글 감사합니다!')

                                # 댓글 작성 버튼을 찾아서 클릭
                                rand_sleep(450, 550)
                                comment_button = self.driver.find_element(By.XPATH,
                                                                    '//*[@id="naverComment"]/div/div[7]/div[1]/form/fieldset/div/div/div[6]/button')
                                comment_button.click()

                                # 댓글 작성 완료 메시지 출력
                                print("댓글을 작성했습니다.")

                                db_manager.update_blog(blog)
                                db_manager.update_post(post)
                                if self.interrupt_signal:
                                    close_all_tabs(self.driver)
                                    return

                                close_current_window(self.driver)
                            except Exception as e:
                                print(f"An error occurred: {str(e)}")
                                # Handle the error as needed, e.g., logging or additional actions.
            else:
                if (now - blog["neighbor_request_date"]).days > 7:
                    # Update neighbor_request_current to False
                    blog["neighbor_request_current"] = 0
                    blog["neighbor_request_rmv"] = 1
                    db_manager.update_blog(blog)
                else:
                    continue

            close_current_window(self.driver)

        self.finished_signal.emit()

class NeighborPostCommentLikeThread(QThread):
    finished_signal = pyqtSignal()
    interrupt_signal = False

    def __init__(self, driver, comment, db_name, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.comment = comment
        self.db_name = db_name
    # 포스트 글이 얼마 없는 사람들은 특정 플래그로 바로 이웃신청을 할 수 있도록 세팅해줘야함
    def run(self):
        db_manager = DbManager(self.db_name)
        all_blogs = db_manager.get_all_blogs()
        all_posts = db_manager.get_all_blog_posts()
        if not all_posts:
            close_all_tabs(self.driver)
            return
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for blog in all_blogs:
            if self.interrupt_signal:
                close_all_tabs(self.driver)
                return
            
            if blog["neighbor_request_rmv"] == 1:
                continue
            # 현재 이웃신청이 되지 않은 블로그 중 조건을 만족하지 못한 블로그들에 대해서 Post에 좋아요와 댓글을 달도록 만듬
            if not blog["neighbor_request_current"]:
                if blog["like_count"] < 5 and blog["comment_count"] < 5:
                    filtered_posts = [
                        post for post in all_posts
                        if post.get("blog_post_id") == blog
                    ]
                    blog_url = f"https://m.blog.naver.com/{blog['blog_id']}"
                    if filtered_posts:
                        for post in filtered_posts:
                            if self.interrupt_signal:
                                close_all_tabs(self.driver)
                                return
                            post_url = blog_url + '/' + post['post_id']
                            get_page(self.driver, post_url)
                            # 좋아요 버튼 확인
                            try:
                                if self.interrupt_signal:
                                    close_all_tabs(self.driver)
                                    return
                                is_liked = self.driver.find_element(by='xpath',
                                                            value='//*[@id="body"]/div[10]/div/div[1]/div/div/a').get_attribute(
                                    'aria-pressed')  # 좋아요 버튼 상태 확인
                                if is_liked == 0:  
                                    like_button = self.driver.find_element(By.XPATH, '//*[@id="body"]/div[10]/div/div[1]/div/div/a/span')
                                    click(like_button)
                                    rand_sleep(450, 550)
                                    blog['like_count'] += 1
                                    post['is_liked'] = 1
                            except Exception:
                                # print('공감 버튼 없음')
                                pass
                            
                            # 댓글 확인
                            try:
                                comment_button = self.driver.find_element(By.XPATH, '//*[@id="body"]/div[10]/div/div[2]/a[1]')
                                click(comment_button)
                                # 댓글 입력란을 찾아서 내용 입력
                                comment_input_1 = self.driver.find_element(By.XPATH,
                                                                    '//*[@id="naverComment"]/div/div[7]/div[1]/form/fieldset/div/div/div[2]/div/label')
                                click(comment_input_1)
                                comment_input = self.driver.find_element(By.XPATH, '//*[@id="naverComment__write_textarea"]')
                                click(comment_input)

                                comment_input.send_keys(self.comment)  # 원하는 댓글 내용으로 수정

                                # 댓글 작성 버튼을 찾아서 클릭
                                rand_sleep(450, 550)
                                comment_button = self.driver.find_element(By.XPATH,
                                                                    '//*[@id="naverComment"]/div/div[7]/div[1]/form/fieldset/div/div/div[6]/button')
                                comment_button.click()
                                blog['comment_count'] += 1
                                post['written_comment'] = self.comment
                                # 댓글 작성 완료 메시지 출력
                                print("댓글을 작성했습니다.")
                                db_manager.update_blog(blog)
                                db_manager.update_post(post)

                                close_current_window(self.driver)
                            except Exception as e:
                                print(f"An error occurred: {str(e)}")
                                # Handle the error as needed, e.g., logging or additional actions.
            else:
                if (now - blog["neighbor_request_date"]).days > 7:
                    # Update neighbor_request_current to False
                    blog["neighbor_request_current"] = 0
                    blog["neighbor_request_rmv"] = 1
                    db_manager.update_blog(blog)
                else:
                    continue
        close_all_tabs(self.driver)
        self.finished_signal.emit()


def neighbor_request_to_blog(driver, blog_id):
    blog_url = "https://m.blog.naver.com/" + blog_id
    open_new_window(driver)
    get_page(driver, blog_url)
    add_neighbor_button = driver.find_element(By.CLASS_NAME, "add_buddy_btn__oGR_B")
    click(add_neighbor_button)
    try:
        both_buddy_radio = driver.find_element(By.ID, "bothBuddyRadio")
        # 만약 서이추가 가능한 사람일 경우
        if both_buddy_radio.get_attribute("ng-disabled") == "false":
            # 서이추 버튼 클릭
            click(both_buddy_radio)
            # 서이추 메세지 입력
            neighbor_request_message_text_area = driver.find_element(By.CSS_SELECTOR, ".add_msg textarea")
            clear(neighbor_request_message_text_area)
            #이부분에 서이추 메세지 추가해야함!!!
            neighbor_request_message = "안녕하세요 저희 서이추 해요 ^^"
            key_in(neighbor_request_message_text_area, neighbor_request_message)
            neighbor_request_button = driver.find_element(By.CLASS_NAME, "btn_ok")
            click(neighbor_request_button)
            return True
    except Exception as e:
        return False
    
    close_current_window(driver)

def neighbor_request_logic(driver):
    db_manager = DbManager()
    all_blogs = db_manager.get_all_blogs()
    all_posts = db_manager.get_all_blog_posts()

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    neighbor_request_count = 0
    today = datetime.now().date()
    blogs = db_manager.get_all_blogs()
    if blogs:
        for blog in blogs:
            blog_date = datetime.strptime(blog['neighbor_request_date'], "%Y-%m-%d %H:%M:%S").date()
            if today == blog_date:
                neighbor_request_count += 1


    for blog in all_blogs:
        if not blog["neighbor_request_current"]:
            if blog["like_count"] >= 5 and blog["comment_count"] >= 5:
                blog_url = "https://m.blog.naver.com/" + blog["blog_id"]

                open_new_window(driver)
                get_page(driver, blog_url)
                rand_sleep(300, 500)
                add_neighbor_button = driver.find_element(By.CLASS_NAME, "add_buddy_btn__oGR_B")
                click(add_neighbor_button)
                try:
                    if neighbor_request_count > 100:
                        continue
                    both_buddy_radio = driver.find_element(By.ID, "bothBuddyRadio")
                    # 만약 서이추가 가능한 사람일 경우
                    if both_buddy_radio.get_attribute("ng-disabled") == "false":
                        # 서이추 버튼 클릭
                        click(both_buddy_radio)
                        # 서이추 메세지 입력
                        neighbor_request_message_text_area = driver.find_element(By.CSS_SELECTOR, ".add_msg textarea")
                        clear(neighbor_request_message_text_area)

                        #이부분에 서이추 메세지 추가해야함!!!
                        neighbor_request_message = "안녕하세요 저희 서이추 해요 ^^"
                        key_in(neighbor_request_message_text_area, neighbor_request_message)
                        neighbor_request_button = driver.find_element(By.CLASS_NAME, "btn_ok")
                        click(neighbor_request_button)

                        neighbor_request_count += 1

                except Exception as e:
                    # 이경우는 이미 서이추가 되어있는 사람이라서 그냥 넘어가는 것으로..
                    pass
                # 이제 열었던 창을 닫아야 함.
                close_current_window(driver)

                # Update neighbor_request_date in sql_blog_table to today's date
                blog["neighbor_request_date"] = now
                db_manager.update_blog(blog)

            else:
                filtered_posts = [
                    post for post in all_posts
                    if post.get("blog_post_id") == blog
                ]

                current_xpath = '//*[@id="contentslist_block"]/div[2]/div/div[2]/ul/li[1]'
                blog_url = f"https://m.blog.naver.com/{blog['blog_id']}"

                if filtered_posts:
                    while True:
                        recent_post_id = get_post_id(driver, blog_url, current_xpath)
                        for post in filtered_posts:
                            if recent_post_id == post.get("post_id"):
                                current_index = int(current_xpath.split('/')[-1][:-1])
                                new_xpath = f'//*[@id="contentslist_block"]/div[2]/div/div[2]/ul/li[{current_index}]'
                                # 다음 검사를 위해 current_xpath 갱신
                                current_xpath = new_xpath
                                break
                        else:
                            if not filtered_posts:  # 만약 필터링된 포스터 테이블이 비어 있다면 새로운 post_id를 추가
                                new_post = {'blog_post_id': blog['blog_id'], 'post_id': recent_post_id, 'is_liked': 0, 'written_comment': ''}
                                db_manager.update_blog(new_post)

                            driver.get(blog_url + '/' + recent_post_id)
                            driver.find_element(By.XPATH,
                                                '//*[@id="contentslist_block"]/div[2]/div/div[2]/ul/li[1]').click()

                            # 좋아요 버튼 확인
                            rand_sleep(450, 550)
                            try:
                                is_like = driver.find_element(by='xpath',
                                                              value='//*[@id="body"]/div[10]/div/div[1]/div/div/a').get_attribute(
                                    'aria-pressed')  # 좋아요 버튼 상태 확인
                                # print(is_like)
                            except Exception:  # 간혹 공감 버튼 자체가 없는 게시글이 존재함
                                print('공감 버튼 없음')
                                continue
                            if is_like == 0:  # 좋아요 버튼 상태가 안눌러져있는 상태일 경우에만 좋아요 버튼 클릭
                                driver.find_element(by='xpath',
                                                    value='//*[@id="body"]/div[10]/div/div[1]/div/div/a/span').click()  # 하트 클릭
                                rand_sleep(450, 550)
                                blog['like_count'] += 1
                                post['is_liked'] = 1

                            # 댓글 확인
                            # 클릭할 부분을 xpath로 찾아서 클릭
                            try:
                                click_button = driver.find_element(By.XPATH, '//*[@id="body"]/div[10]/div/div[2]/a[1]')
                                click_button.click()

                                # 댓글 입력란을 찾아서 내용 입력
                                comment_input_1 = driver.find_element(By.XPATH,
                                                                      '//*[@id="naverComment"]/div/div[7]/div[1]/form/fieldset/div/div/div[2]/div/label')
                                click(comment_input_1)

                                rand_sleep(450, 550)
                                comment_input = driver.find_element(By.XPATH, '//*[@id="naverComment__write_textarea"]')
                                click(comment_input)
                                rand_sleep(450, 550)
                                comment_input.send_keys("좋은 글 감사합니다!")  # 원하는 댓글 내용으로 수정
                                blog['comment_count'] += 1
                                post['written_comment'] = comment_input.get_attribute('좋은 글 감사합니다!')

                                # 댓글 작성 버튼을 찾아서 클릭
                                rand_sleep(450, 550)
                                comment_button = driver.find_element(By.XPATH,
                                                                     '//*[@id="naverComment"]/div/div[7]/div[1]/form/fieldset/div/div/div[6]/button')
                                comment_button.click()

                                # 댓글 작성 완료 메시지 출력
                                print("댓글을 작성했습니다.")

                                db_manager.update_blog(blog)
                                db_manager.update_post(post)

                                close_current_window(driver)
                            except Exception as e:
                                print(f"An error occurred: {str(e)}")
                                # Handle the error as needed, e.g., logging or additional actions.
        else:
            if (now - blog["neighbor_request_date"]).days > 7:
                # Update neighbor_request_current to False
                blog["neighbor_request_current"] = 0
                blog["neighbor_request_rmv"] = 1
                db_manager.update_blog(blog)
            else:
                continue
        close_current_window(driver)

def get_post_id(driver, blog_url, current_xpath):
    # Navigate to the provided blog URL
    driver.get(blog_url)

    # Use WebDriverWait to wait for the elements to be present
    wait = WebDriverWait(driver, 10)

    # Find the latest post element using the provided XPath
    latest_post = wait.until(EC.presence_of_element_located((By.XPATH, current_xpath)))

    # Extract the URL of the latest post
    latest_post_url = latest_post.find_element(By.TAG_NAME, "a").get_attribute("href")

    parsed_url = urlparse(latest_post_url)
    query_params = parse_qs(parsed_url.query)
    post_id = query_params.get('logNo', [''])[0]

    return post_id