import logging
from const import *
from custom_func import *

from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By


def get_blogs_by_search(driver, search_keyword):
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
                # 이곳에서 blog_id를 기존에 있는지 확인하고, 없으면 저장해준다.
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