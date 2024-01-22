import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from const import DEV_ID, NAVER_LOGIN_URL, DEV_PW
from custom_func import key_in, click, get_page, rand_sleep


def today_neighbor_request_current(driver):
    try:
        get_page(driver, NAVER_LOGIN_URL)

        id_text_field = driver.find_element(By.CSS_SELECTOR, '#id')
        key_in(id_text_field, DEV_ID)

        pw_text_field = driver.find_element(By.CSS_SELECTOR, '#pw')
        key_in(pw_text_field, DEV_PW)

        login_button = driver.find_element(By.XPATH, '//*[@id="log.login"]')
        click(login_button)
        rand_sleep(450, 550)

        url = f'https://m.blog.naver.com/yj6658/223308901671'
        driver.get(url)
        rand_sleep(450, 550)


        is_like = driver.find_element(by='xpath',
                                          value='//*[@id="body"]/div[10]/div/div[1]/div/div/a').get_attribute(
                'aria-pressed')  # 좋아요 버튼 상태 확인

        if is_like == 'false':  # 좋아요 버튼 상태가 안눌러져있는 상태일 경우에만 좋아요 버튼 클릭
            driver.find_element(by='xpath',
                                value='//*[@id="body"]/div[10]/div/div[1]/div/div/a/span').click()  # 하트 클릭
            rand_sleep(750, 850)


        click_button = driver.find_element(By.XPATH, '//*[@id="body"]/div[10]/div/div[2]/a[1]')
        click_button.click()

        # 댓글 입력란을 찾아서 내용 입력
        rand_sleep(2050, 2150)

        comment_input_1 = driver.find_element(By.XPATH,
                                            '//*[@id="naverComment"]/div/div[7]/div[1]/form/fieldset/div/div/div[2]/div/label')
        click(comment_input_1)
        rand_sleep(2050, 2150)
        comment_input = driver.find_element(By.XPATH, '//*[@id="naverComment__write_textarea"]')
        click(comment_input)
        rand_sleep(2050, 2150)
        comment_input.send_keys("좋은 글 감사합니다!") # 원하는 댓글 내용으로 수정

        # 댓글 작성 버튼을 찾아서 클릭
        rand_sleep(2050, 2150)
        comment_button = driver.find_element(By.XPATH,
                                             '//*[@id="naverComment"]/div/div[7]/div[1]/form/fieldset/div/div/div[6]/button')
        comment_button.click()
        rand_sleep(2050, 2150)
    except Exception as e:
        print(f"Error: {e}")

# Set up the Chrome WebDriver (you can use other drivers as well)
driver = webdriver.Chrome()

# Call the function with the driver
today_neighbor_request_current(driver)

rand_sleep(2050, 2150)
# Close the WebDriver
driver.quit()