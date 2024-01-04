import logging

from selenium.webdriver.common.alert import Alert

from const import *
from custom_func import *

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

from db import DbManager
from datetime import datetime, timedelta

def get_blogs_by_search(driver, search_keyword):
    db_instance = DbManager()
    open_new_window(driver)
    get_page(driver, BLOG_MAIN_URL)

    #블로그 검색창에 입력
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
                #########################################################
                db_instance.insert_blog_record_with_id(blog_id)
                #########################################################

            if (i + 1) != len(driver.find_elements(By.CSS_SELECTOR, ".pagination span a")):
                page_next_number_button = driver.find_elements(By.CSS_SELECTOR, ".pagination span a")[i + 1]
                click(page_next_number_button)

        try:
            page_next_button = driver.find_element(By.CSS_SELECTOR, ".pagination .button_next")
            click(page_next_button)
        except NoSuchElementException as e:
            logging.getLogger("main").info("블로그의 모든 글을 탐색했습니다.")
            break
 

def naver_login(driver, username, password):
    open_new_window(driver)
    
    get_page(driver, NAVER_LOGIN_URL)

    id_text_field = driver.find_element(By.CSS_SELECTOR, '#id')
    key_in(id_text_field, username)

    pw_text_field = driver.find_element(By.CSS_SELECTOR, '#pw')
    key_in(pw_text_field, password)

    login_button = driver.find_element(By.XPATH, '//*[@id="log.login"]')
    click(login_button)

    close_current_window(driver)


def get_blogs_by_category(driver, main_category, sub_category):
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
    sub_category_element = WebDriverWait(driver, 1000).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, sub_category_element))
    )
    click(sub_category_element)

    while True:
        # 검색결과의 페이지 별 순회
        for i in range(0, len(driver.find_elements(By.CSS_SELECTOR, ".pagination span a"))):
            # 검색결과 내 Blog를 순회
            for post in driver.find_elements(By.CSS_SELECTOR, ".desc .desc_inner"):
                post_link_splat = post.get_attribute("href").split("/")
                blog_id = post_link_splat[3]
                post_id = post_link_splat[4]
                liked_link = f'https://m.blog.naver.com/SympathyHistoryList.naver?blogId={blog_id}&logNo={post_id}&categoryId=POST'
                open_new_window(driver)
                get_page(driver, liked_link)

                


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

    # 재영
    # 모든 블로그 아이디를 찾는 부분은, blog 의 모든 정보를 메모리에 올려도 될 것 같음
    # DB 를 여러번 접근하면 시간적으로 
    all_blogs = db_instance.get_all_blogs()
    today_date = datetime.now().strftime('%Y-%m-%d')
    for blog in all_blogs:
        if not blog["neighbor_request_current"]:
            if blog["like_count"] >= 5 and blog["comment_count"] >= 5:
                ######
                #서로이웃 신청 코드 작성하기
                ######
                # Update neighbor_request_date in sql_blog_table to today's date
                blog["neighbor_request_date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                db_instance.update_blog(blog)

            else:
                # 블로그로 이동
                blog_url = f"https://m.blog.naver.com/{blog['blog_id']}/"
                get_page(driver, blog_url)

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
                try:
                    rand_sleep(950, 1050)
                    alert = Alert(driver)  # 팝업창으로 메시지 뜰 경우를 대비
                    alert.accept()
                except Exception:
                    continue

                # 댓글 확인
                comment_section = driver.find_element(By.CSS_SELECTOR, '.area_comment .reply_area')
                if 'hidden' in comment_section.get_attribute('class'):
                    # 댓글 섹션이 감춰져 있으면 펼치기
                    driver.execute_script("arguments[0].classList.remove('hidden')", comment_section)
                # 댓글 입력
                comment_input = driver.find_element(By.CSS_SELECTOR, '.reply_write textarea')
                comment_input.send_keys("좋은 글 감사합니다!")  # 원하는 댓글 내용으로 수정
                comment_input.send_keys(Keys.RETURN)
                print(f"블로그 {blog['blog_id']}에 댓글을 작성했습니다.")
                blog['comment_count'] += 1
                db_instance.update_blog(blog)
        else:
            if (today_date - blog["neighbor_request_date"]).days > 7:
                # Update neighbor_request_current to False
                blog["neighbor_request_current"] = 0
                blog["neighbor_request_rmv"] = 1
                db_instance.update_blog(blog)
            else:
                continue




