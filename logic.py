import logging
from urllib.parse import urlparse, parse_qs

from selenium.webdriver.common.alert import Alert

from const import *
from custom_func import *

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from db import DbManager
from datetime import datetime


# 블로그 추가하려면 서이추가 가능한 사람만 추가하기..
def naver_login(driver, username, password):
    db_manager = DbManager()
    open_new_window(driver)

    get_page(driver, NAVER_LOGIN_URL)

    id_text_field = driver.find_element(By.CSS_SELECTOR, '#id')
    key_in(id_text_field, username)

    pw_text_field = driver.find_element(By.CSS_SELECTOR, '#pw')
    key_in(pw_text_field, password)

    login_button = driver.find_element(By.XPATH, '//*[@id="log.login"]')
    click(login_button)

    close_current_window(driver)


def initialize(driver, username):
    db_manager = DbManager()
    open_new_window(driver)
    url = f"https://admin.blog.naver.com/BuddyListManage.naver?blogId={username}"
    get_page(driver, url)
    buddy_ids = []
    while True:

        print("while 돌았음")
        # 검색결과의 페이지 별 순회
        current_page_element = driver.find_element(By.CSS_SELECTOR, '.paginate .paginate_re strong')
        current_page_text = current_page_element.text
        current_page_text_copy = current_page_text
        active_page_buttons = driver.find_elements(By.CSS_SELECTOR, '.paginate .paginate_re a')

        # 로직
        buddies = driver.find_elements(By.CSS_SELECTOR, ".buddy .ellipsis2 a")
        for buddy in buddies:
            blog_id = buddy.get_attribute("href").split("/")[3]
            buddy_ids.append(blog_id)

        for page_button in active_page_buttons:
            if int(page_button.text) == int(current_page_text) + 1:
                click(page_button)
                current_page_text = driver.find_element(By.CSS_SELECTOR, '.paginate .paginate_re strong').text
        
        # 만약 다음 페이지가 없다면
        if current_page_text == current_page_text_copy:
            break

    db_manager.insert_blogs_record_with_ids(buddy_ids)
    close_current_window(driver)
    

def get_blogs_by_search(driver, search_keyword):
    db_instance = DbManager()
    open_new_window(driver)
    get_page(driver, BLOG_MAIN_URL)

    # 블로그 검색창에 입력
    search_bar_element = driver.find_element(By.XPATH, '//*[@id="header"]/div[1]/div/div[2]/form/fieldset/div/input')
    key_in(search_bar_element, search_keyword)
    search_button_element = driver.find_element(By.XPATH, '//*[@id="header"]/div[1]/div/div[2]/form/fieldset/a[1]')
    click(search_button_element)

    while True:
        # 검색결과의 페이지 별 순회
        for i in range(0, len(driver.find_elements(By.CSS_SELECTOR, ".pagination span a"))):
            # 검색결과 내 Blog를 순회
            for author in driver.find_elements(By.CSS_SELECTOR, ".writer_info .author"):
                blog_id = author.get_attribute("href").split("/")[3]
                # 만약 블로그가 서이추가 가능한 상태면 DB에 추가한다.
                blog_url = "https://m.blog.naver.com/" + blog_id
                open_new_window(driver)
                get_page(driver, blog_url)
                try:
                    add_neighbor_button = driver.find_element(By.CLASS_NAME, "add_buddy_btn__oGR_B")
                    click(add_neighbor_button)
                    both_buddy_radio = driver.find_element(By.ID, "bothBuddyRadio")
                    # 만약 서이추가 가능한 사람일 경우
                    if both_buddy_radio.get_attribute("ng-disabled") == "false":
                        db_instance.insert_blog_record_with_id(blog_id)
                except Exception as e:
                    # 이 경우는 이미 이웃
                    pass

                # 이제 열었던 창을 닫아야 함.
                close_current_window(driver)

            if (i + 1) != len(driver.find_elements(By.CSS_SELECTOR, ".pagination span a")):
                page_next_number_button = driver.find_elements(By.CSS_SELECTOR, ".pagination span a")[i + 1]
                click(page_next_number_button)
        try:
            page_next_button = driver.find_element(By.CSS_SELECTOR, ".pagination .button_next")
            click(page_next_button)
        except NoSuchElementException as e:
            logging.getLogger("main").info("블로그의 모든 글을 탐색했습니다.")
            break


def get_blogs_by_category(driver, main_category, sub_category):
    db_instance = DbManager()
    open_new_window(driver)
    get_page(driver, BLOG_MAIN_URL)

    category_discovery_button = driver.find_element(By.XPATH, '//*[@id="lnbMenu"]/a[2]')
    click(category_discovery_button)

    main_category_xpath = f"//a[contains(@bg-nclick, '{MAIN_CATEGORIES[main_category]}')]"
    main_category_element = WebDriverWait(driver, 1000).until(
        EC.element_to_be_clickable((By.XPATH, main_category_xpath))
    )
    main_category_element.click()
    rand_sleep(300, 500)
    sub_category_css_selector = f".navigator_category_sub [bg-nclick='{SUB_CATEGORIES[sub_category]}']"
    sub_category_element = WebDriverWait(driver, 1000).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, sub_category_css_selector))
    )
    click(sub_category_element)

    while True:
        # 검색결과의 페이지 별 순회
        for i in range(0, len(driver.find_elements(By.CSS_SELECTOR, ".pagination span a"))):
            # 검색결과 내 Blog를 순회
            for post_index in range(len(driver.find_elements(By.CSS_SELECTOR,
                                                             ".list_post_article .multi_pic .info_post .desc .desc_inner"))):
                post = \
                driver.find_elements(By.CSS_SELECTOR, ".list_post_article .multi_pic .info_post .desc .desc_inner")[
                    post_index]
                post_link_splat = post.get_attribute("href").split("/")
                blog_id = post_link_splat[3]
                post_id = post_link_splat[4]
                liked_link = f'https://m.blog.naver.com/SympathyHistoryList.naver?blogId={blog_id}&logNo={post_id}&categoryId=POST'
                open_new_window(driver)
                get_page(driver, liked_link)
                rand_sleep(3000, 5000)
                for blog_description in driver.find_elements(By.CSS_SELECTOR,
                                                             ".sympathy_item___b3xy .bloger_area___eCA_ .link__D9GoZ"):
                    blog_id = blog_description.get_attribute("href").split("/")[3]
                    # 만약 블로그가 서이추가 가능한 상태면 DB에 추가한다.
                    blog_url = "https://m.blog.naver.com/" + blog_id
                    open_new_window(driver)
                    get_page(driver, blog_url)
                    try:
                        add_neighbor_button = driver.find_element(By.CLASS_NAME, "add_buddy_btn__oGR_B")
                        click(add_neighbor_button)
                        both_buddy_radio = driver.find_element(By.ID, "bothBuddyRadio")
                        # 만약 서이추가 가능한 사람일 경우
                        if both_buddy_radio.get_attribute("ng-disabled") == "false":
                            db_instance.insert_blog_record_with_id(blog_id)
                    except Exception as e:
                        # 이 경우는 이미 이웃
                        pass
                    # 서로이웃 확인했던 창 끄기.
                    close_current_window(driver)

                # 포스트 공감창 끄기
                close_current_window(driver)
            if (i + 1) < len(driver.find_elements(By.CSS_SELECTOR, ".pagination span a")):
                page_next_number_button = driver.find_elements(By.CSS_SELECTOR, ".pagination span a")[i + 1]
                click(page_next_number_button)
        try:
            page_next_button = driver.find_element(By.CSS_SELECTOR, ".pagination .button_next")
            click(page_next_button)
        except NoSuchElementException as e:
            logging.getLogger("main").info("카테고리의 모든 글을 탐색했습니다.")
            break


def neighbor_request_logic(driver):
    db_instance = DbManager()
    all_blogs = db_instance.get_all_blogs()
    all_posts = db_instance.get_all_blog_posts()

    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for blog in all_blogs:
        blog["like_count"] = 5
        blog["comment_count"] = 5
        if not blog["neighbor_request_current"]:
            if blog["like_count"] >= 5 and blog["comment_count"] >= 5:
                blog_url = "https://m.blog.naver.com/" + blog["blog_id"]

                open_new_window(driver)
                get_page(driver, blog_url)
                rand_sleep(300, 500)
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
                except Exception as e:
                    # 이경우는 이미 서이추가 되어있는 사람이라서 그냥 넘어가는 것으로..
                    pass
                # 이제 열었던 창을 닫아야 함.
                close_current_window(driver)

                # Update neighbor_request_date in sql_blog_table to today's date
                blog["neighbor_request_date"] = now
                db_instance.update_blog(blog)

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
                                new_post = {'blog_post_id': blog['blog_id'], 'post_id': recent_post_id, 'is_liked': False, 'written_comment': ''}
                                db_instance.update_blog(new_post)

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
                            if is_like == 'false':  # 좋아요 버튼 상태가 안눌러져있는 상태일 경우에만 좋아요 버튼 클릭
                                driver.find_element(by='xpath',
                                                    value='//*[@id="body"]/div[10]/div/div[1]/div/div/a/span').click()  # 하트 클릭
                                rand_sleep(450, 550)
                                blog['like_count'] += 1
                                post['is_liked'] = True
                            try:
                                rand_sleep(950, 1050)
                                alert = Alert(driver)  # 팝업창으로 메시지 뜰 경우를 대비
                                alert.accept()
                            except Exception:
                                continue

                            # 댓글 확인
                            # 클릭할 부분을 xpath로 찾아서 클릭
                            try:
                                click_button = driver.find_element(By.XPATH, '//*[@id="body"]/div[10]/div/div[2]/a[1]')
                                click_button.click()

                                # 댓글 입력란을 찾아서 내용 입력
                                rand_sleep(450, 550)
                                comment_input = driver.find_element(By.XPATH,
                                                                    '//*[@id="naverComment"]/div/div[7]/div[1]/form/fieldset/div/div/div[2]/div/label')
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

                                db_instance.update_blog(blog)
                                db_instance.update_post(post)

                                close_current_window(driver)
                            except Exception as e:
                                print(f"An error occurred: {str(e)}")
                                # Handle the error as needed, e.g., logging or additional actions.
        else:
            if (now - blog["neighbor_request_date"]).days > 7:
                # Update neighbor_request_current to False
                blog["neighbor_request_current"] = 0
                blog["neighbor_request_rmv"] = 1
                db_instance.update_blog(blog)
            else:
                continue


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