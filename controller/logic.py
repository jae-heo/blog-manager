from urllib.parse import urlparse, parse_qs
from common.const import *
from common.util_function import *
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from controller.db import DbManager
from datetime import datetime
from common.custom_class import NThread
import time

class LoginThread(NThread):
    def __init__(self, driver, username, password, db_name, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.username = username
        self.password = password
        self.db_name = db_name
        self.blog_exist = False

    def run(self):
        open_new_window(self.driver)
        get_page(self.driver, NAVER_LOGIN_URL)  
        id_text_field = self.driver.find_element(By.CSS_SELECTOR, '#id')
        key_in(id_text_field, self.username)
        pw_text_field = self.driver.find_element(By.CSS_SELECTOR, '#pw')
        key_in(pw_text_field, self.password)
        login_button = self.driver.find_element(By.XPATH, '//*[@id="log.login"]')
        click(login_button)
        try:
            self.driver.find_element(By.CSS_SELECTOR, '.MyView-module__desc_email___JwAKa')
            self.finished_signal.emit(0)
        except Exception as e:
            self.finished_signal.emit(1)
        close_all_tabs(self.driver)
    
class CollectBlogByKeywordThread(NThread):
    def __init__(self, driver, search_keyword, db_name, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.search_keyword = search_keyword
        self.db_name = db_name

    def run(self):
        db_manager = DbManager(self.db_name)

        count = 0
        today = datetime.now().date()
        blogs = db_manager.get_all_blogs()
        if blogs:
            for blog in blogs:
                blog_date = datetime.strptime(blog['created_date'], "%Y-%m-%d %H:%M:%S").date()
                if today == blog_date:
                    count += 1
        if count >= DAILY_LIMIT:
            self.log_ui(f"오늘 {DAILY_LIMIT}명을 모두 수집했습니다.")
            self.finish()
            return
        
        self.log_ui(f'오늘 수집한 블로그는 {count}개 입니다.')
        self.set_progress(count/DAILY_LIMIT)
        self.log_ui(f'블로그 수집을 시작합니다.')

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
                        self.interrupt()
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
                                self.log_ui(f"{blog_id} 블로그를 수집했습니다... ({count}/100)")
                                self.set_progress(count/DAILY_LIMIT)

                            if count >= DAILY_LIMIT:
                                self.log_ui(f"오늘 {DAILY_LIMIT}명을 모두 수집했습니다.")
                                self.finish()
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
                self.log_ui(f"키워드에 속한 블로그를 모두 수집했습니다.")
                break
        close_current_window(self.driver)

class CollectBlogByCategoryThread(NThread):
    def __init__(self, driver, main_category, sub_category, db_name, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.main_category = main_category
        self.sub_category = sub_category
        self.db_name = db_name

    def run(self):
        db_manager = DbManager(self.db_name)
        count = 0
        today = datetime.now().date()
        blogs = db_manager.get_all_blogs()
        if blogs:
            for blog in blogs:
                blog_date = datetime.strptime(blog['created_date'], "%Y-%m-%d %H:%M:%S").date()
                if today == blog_date:
                    count += 1

        if count >= DAILY_LIMIT:
            self.log_ui(f"오늘 {DAILY_LIMIT}명을 모두 수집했습니다.")
            self.finish()
            return
        
        self.log_ui(f'오늘 수집한 블로그는 {count}개 입니다.')
        self.set_progress(count/DAILY_LIMIT)
        self.log_ui(f'블로그 수집을 시작합니다.')

        # 블로그창 열고 카테고리 선택하기
        open_new_window(self.driver)
        get_page(self.driver, BLOG_MAIN_URL)
        category_discovery_button = self.driver.find_element(By.XPATH, '//*[@id="lnbMenu"]/a[2]')
        click(category_discovery_button)
        main_category_xpath = f"//a[contains(@bg-nclick, '{MAIN_CATEGORIES[self.main_category]}')]"
        main_category_element = WebDriverWait(self.driver, 1000).until(
            EC.element_to_be_clickable((By.XPATH, main_category_xpath))
        )
        click(main_category_element)
        sub_category_css_selector = f".navigator_category_sub [bg-nclick='{SUB_CATEGORIES[self.sub_category]}']"
        sub_category_element = WebDriverWait(self.driver, 1000).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, sub_category_css_selector))
        )
        click(sub_category_element)

        while True:
            # 검색결과의 페이지 별 순회
            for i in range(0, len(self.driver.find_elements(By.CSS_SELECTOR, ".pagination span a"))):
                # 검색결과 내 Blog를 순회
                for post_index in range(len(self.driver.find_elements(By.CSS_SELECTOR, ".list_post_article .multi_pic .info_post .desc .desc_inner"))):
                    if self.interrupt_signal:
                        self.interrupt()
                        return

                    post = self.driver.find_elements(By.CSS_SELECTOR, ".list_post_article .multi_pic .info_post .desc .desc_inner")[post_index]
                    post_link_splat = post.get_attribute("href").split("/")
                    blog_id = post_link_splat[3]
                    post_id = post_link_splat[4]
                    liked_link = f'https://m.blog.naver.com/SympathyHistoryList.naver?blogId={blog_id}&logNo={post_id}&categoryId=POST'
                    open_new_window(self.driver)
                    get_page(self.driver, liked_link)
                    for blog_description in self.driver.find_elements(By.CSS_SELECTOR, ".sympathy_item___b3xy .bloger_area___eCA_ .link__D9GoZ"):
                        if self.interrupt_signal:
                            self.interrupt()
                            return                    
                        blog_id = blog_description.get_attribute("href").split("/")[3]
                        # 만약 블로그가 서이추가 가능한 상태면 DB에 추가한다.
                        open_new_window(self.driver)
                        get_page(self.driver, "https://m.blog.naver.com/" + blog_id)
                        try:
                            add_neighbor_button = self.driver.find_element(By.CLASS_NAME, "add_buddy_btn__oGR_B")
                            click(add_neighbor_button)
                            both_buddy_radio = self.driver.find_element(By.ID, "bothBuddyRadio")
                            # 만약 서이추가 가능한 사람일 경우
                            if both_buddy_radio.get_attribute("ng-disabled") == "false":
                                if db_manager.insert_blog_record_with_id(blog_id):
                                    count += 1
                                    self.log_ui(f"{blog_id} 블로그를 수집했습니다... ({count}/100)")
                                    self.set_progress(count/DAILY_LIMIT)
                                
                                if count >= DAILY_LIMIT:
                                    self.log_ui(f"오늘 {DAILY_LIMIT}명을 모두 수집했습니다.")
                                    self.finish()
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
                self.log_ui("카테고리의 모든 글을 탐색했습니다.")
                break

class NeighborRequestThread(NThread):
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
                if self.interrupt_signal:
                    self.interrupt()
                    return
                if request_count >= 100:
                    self.finish()
                    return
                # 현재 이웃신청이 되지 않은 블로그 중
                if blog["neighbor_request_current"] == 0 and blog["neighbor_request_rmv"] != 1:
                    # 이웃신청 조건이 완료된 경우
                    if blog["like_count"] >= 1 and blog["comment_count"] >= 1:
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
        self.finish()

class NeighborPostCollectThread(NThread):
    def __init__(self, driver, db_name, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.db_name = db_name
    def run(self):
        db_manager = DbManager(self.db_name)
        all_blogs = db_manager.get_all_blogs()
        all_posts = db_manager.get_all_blog_posts()

        count = 0
        today = datetime.now().date()

        daily_limit = len(all_blogs)

        if all_posts:
            for post in all_posts:
                post_date = datetime.strptime(post['created_date'], "%Y-%m-%d %H:%M:%S").date()
                if today == post_date:
                    count += 1

        if count >= daily_limit:
            self.log_ui('포스트 수집을 이미 완료했습니다.')
            self.finish()
            return

        self.log_ui(f'오늘 수집한 블로그 포스트는 {count}개 입니다.~')
        self.set_progress(count / daily_limit)

        open_new_window(self.driver)

        self.log_signal.emit(f'포스트 수집을 시작합니다.')
        for blog in all_blogs:
            if self.interrupt_signal:
                self.interrupt()
                return
            self.progress_signal.emit(count / daily_limit)
            if count > daily_limit:
                self.log_ui('포스트 수집을 이미 완료했습니다.')
                self.finish()
                return

            if all_posts:
                filtered_posts = [
                    post for post in all_posts
                    if post and post.get("blog_id") is not None and post.get("blog_id") == blog.get("blog_id")
                ]
            else:
                filtered_posts = []

            url = f"https://m.blog.naver.com/{blog['blog_id']}"
            get_page(self.driver, url)

            current_number = 1

            try:
                button = self.driver.find_element(By.CSS_SELECTOR,
                                             '#contentslist_block > div > div > div > button:nth-child(2)')
                click(button)
                while True:
                    selector = f'#contentslist_block > div > div > div:nth-child(2) > ul > li:nth-child({current_number})'
                    selector_title = f'{selector} > div > a > div > strong > span > span'
                    selector_content = f'{selector} > div > a > div > p > span > span'

                    post_title = self.driver.find_element(By.CSS_SELECTOR, selector_title).text
                    post_content = self.driver.find_element(By.CSS_SELECTOR, selector_content).text
                    if post_content == "":
                        post_content = "Post Content is None"
                    latest_post = self.driver.find_element(By.CSS_SELECTOR, selector)
                    # Extract the URL of the latest post
                    latest_post_url = latest_post.find_element(By.TAG_NAME, "a").get_attribute("href")

                    # Find the last occurrence of '/'
                    last_slash_index = latest_post_url.rfind('/')

                    # Find the index of '?' after the last '/'
                    question_mark_index = latest_post_url.find('?', last_slash_index)
                    if last_slash_index != -1 and question_mark_index != -1:
                        extracted_part = latest_post_url[last_slash_index + 1:question_mark_index]
                        continue_flag = False
                        for post in filtered_posts:
                            if post["post_id"] == extracted_part:
                                current_number += 1
                                continue_flag = True
                                break
                        if continue_flag:
                            continue
                        print(extracted_part)
                        print(post_title)
                        print(post_content)
                        db_manager.insert_blog_post(blog["blog_id"], extracted_part, post_title, post_content)
                        count += 1
                        self.log_signal.emit(f"{blog['blog_id']} 포스트를 수집했습니다... ({count}/{daily_limit})")
                        break

                    else:
                        print("Pattern not found.")
            except:
                count += 1
                self.log_signal.emit(f"글이 없어서 자동으로 count를 올립니다. ({count}/{daily_limit})")
                continue
        self.log_signal.emit(f"모든 블로그의 포스터 수집을 완료했습니다.")
        self.finish()

class NeighborPostCommentLikeThread(NThread):
    def __init__(self, driver, comment, db_name, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.comment = comment
        self.db_name = db_name
    # 포스트 글이 얼마 없는 사람들은 특정 플래그로 바로 이웃신청을 할 수 있도록 세팅해줘야함
    def run(self):

        self.log_signal.emit(f'좋아요, 댓글작업을 시작합니다.')

        db_manager = DbManager(self.db_name)
        all_blogs = db_manager.get_all_blogs()
        all_posts = db_manager.get_all_blog_posts()

        now = datetime.now().date()

        count = 0
        daily_limit = 0

        for post in all_posts:
            post_date = datetime.strptime(post['created_date'], "%Y-%m-%d %H:%M:%S").date()
            if now == post_date:
                daily_limit += 1

        if all_posts:
            for post in all_posts:
                if post['is_liked'] == 1 and post['written_comment'] is not None:
                    count += 1

        self.set_progress(count / daily_limit)

        rand_sleep(300, 500)

        if count > daily_limit:
            self.log_signal.emit('좋아요, 댓글 작업을 이미 완료했습니다.')
            close_all_tabs(self.driver)
            self.finish()
            return

        for blog in all_blogs:
            if self.interrupt_signal:
                self.interrupt()
                return
            self.set_progress(count / daily_limit)
            if count >= daily_limit:
                self.log_signal.emit('좋아요, 댓글 작업을 이미 완료했습니다.')
                self.finish()
                return

            if all_posts:
                filtered_posts = [
                    post for post in all_posts
                    if post and post.get("blog_id") is not None and post.get("blog_id") == blog.get("blog_id") and (post.get(
                        "is_liked") == 0 or post.get("written_comment") is None)
                ]
            else:
                filtered_posts = []

            if blog["neighbor_request_rmv"] == 1:
                continue
            blog_url = f"https://m.blog.naver.com/{blog['blog_id']}"
            if blog["neighbor_request_current"] == 0:
                if blog["like_count"] < 5 and blog["comment_count"] < 5:
                    for post in filtered_posts:
                        if self.interrupt_signal:
                            self.interrupt()
                            return
                        post_url = blog_url + '/' + post['post_id']
                        get_page(self.driver, post_url)
                        # 좋아요 버튼 확인
                        try:
                            is_liked = self.driver.find_element(By.CSS_SELECTOR,
                                                           "#body > div.floating_menu > div > div.btn_like_w > div > div > a").get_attribute(
                                'aria-pressed')  # 좋아요 버튼 상태 확인
                            print(is_liked)
                            if is_liked == "false":
                                like_button = self.driver.find_element(By.CSS_SELECTOR,
                                                                  '#body > div.floating_menu > div > div.btn_like_w > div > div > a')
                                click(like_button)
                                rand_sleep(450, 550)
                                blog['like_count'] += 1
                                post['is_liked'] = 1

                                self.log_signal.emit(f"{blog['blog_id']} 블로그의 포스터에 좋아요를 눌렀습니다.")

                            else:
                                pass
                        except Exception:
                            # print('공감 버튼 없음')
                            pass
                        # 댓글 확인
                        try:
                            if post['written_comment'] is not None:
                                continue
                            comment_button = self.driver.find_element(By.CSS_SELECTOR,
                                                                 '#body > div.floating_menu > div > div.btn_r > a.btn_reply')
                            click(comment_button)
                            rand_sleep(3500, 4000)
                            # 댓글 입력란을 찾아서 내용 입력
                            comment_input_1 = self.driver.find_element(By.CSS_SELECTOR,
                                                                  '#naverComment > div > div.u_cbox_write_wrap > div.u_cbox_write_box.u_cbox_type_logged_in > form > fieldset > div > div > div.u_cbox_write_area > div > label')
                            click(comment_input_1)
                            comment_input = self.driver.find_element(By.CSS_SELECTOR, '#naverComment__write_textarea')
                            click(comment_input)

                            comment_input.send_keys(self.comment)  # 원하는 댓글 내용으로 수정

                            # 댓글 작성 버튼을 찾아서 클릭
                            rand_sleep(450, 550)
                            comment_button = self.driver.find_element(By.CSS_SELECTOR,
                                                                 '#naverComment > div > div.u_cbox_write_wrap > div.u_cbox_write_box.u_cbox_type_logged_in > form > fieldset > div > div > div.u_cbox_upload > button')
                            comment_button.click()
                            blog['comment_count'] += 1
                            post['written_comment'] = self.comment
                            # 댓글 작성 완료 메시지 출력
                            self.log_signal.emit(f"{blog['blog_id']} 블로그의 포스터에 댓글을 작성했습니다.")

                            db_manager.update_blog(blog)
                            db_manager.update_post(post)

                        except Exception as e:
                            count += 1
                            self.log_signal.emit(f"글이 없어서 자동으로 count를 올립니다. ({count}/{daily_limit})")
                            if post['is_liked'] == 0:
                                blog['like_count'] += 1
                                post['is_liked'] = 1
                            if post['written_comment'] is None:
                                blog['comment_count'] += 1
                                post['written_comment'] = self.comment
                            db_manager.update_blog(blog)
                            db_manager.update_post(post)
                            continue
                                # Handle the error as needed, e.g., logging or additional actions.
                        if post['is_liked'] == 1 and post['written_comment'] is not None:
                            count += 1
                else:
                    continue
            else:
                if (now - blog["neighbor_request_date"]).days > 7:
                    # Update neighbor_request_current to False
                    blog["neighbor_request_current"] = 0
                    blog["neighbor_request_rmv"] = 1
                    db_manager.update_blog(blog)
                    continue
                else:
                    continue
        self.log_signal.emit(f"모든 블로그에 좋아요, 댓글작업을 완료했습니다.")
        self.set_progress(count / daily_limit)
        self.finish()
