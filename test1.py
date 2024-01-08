from datetime import datetime
from telnetlib import EC

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from const import DEV_ID, NAVER_LOGIN_URL, DEV_PW
from custom_func import key_in, click, get_page


def today_neighbor_request_current(driver):
    try:
        current_time = datetime.now().strftime('%H:%M:%S')

        get_page(driver, NAVER_LOGIN_URL)

        id_text_field = driver.find_element(By.CSS_SELECTOR, '#id')
        key_in(id_text_field, DEV_ID)

        pw_text_field = driver.find_element(By.CSS_SELECTOR, '#pw')
        key_in(pw_text_field, DEV_PW)

        login_button = driver.find_element(By.XPATH, '//*[@id="log.login"]')
        click(login_button)

        url = f'https://admin.blog.naver.com/{DEV_ID}/stat/today'
        driver.get(url)

        # Wait for the element to be present
        neighbor_count_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="_root"] div ul li:nth-child(5) strong'))
        )

        # Get the text content from the element
        neighbor_count = neighbor_count_element.text.strip()

        print(f"{current_time} : {neighbor_count}")

    except Exception as e:
        print(f"Error: {e}")

# Set up the Chrome WebDriver (you can use other drivers as well)
driver = webdriver.Chrome()

# Call the function with the driver
today_neighbor_request_current(driver)

# Close the WebDriver
driver.quit()