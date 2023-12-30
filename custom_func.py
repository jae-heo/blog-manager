import random
import time
import pyperclip

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from const import *

def rand_sleep():
    time.sleep(random.uniform(1.5, 2.5))

def empty(s: str):
    return True if len(s) == 0 else False

def get_chrome_driver():
    options = Options()
    options.add_experimental_option("detach", True)
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def open_new_window(driver):
    driver.execute_script("window.open('', '_blank');")
    tabs = driver.window_handles
    driver.switch_to.window(tabs[-1])
    rand_sleep()

def close_current_window(driver):
    driver.close()
    tabs = driver.window_handles
    driver.switch_to.window(tabs[-1])

def get_page(driver, url):
    driver.get(url)
    rand_sleep()

def key_in(element, text):
    pyperclip.copy(text)
    element.send_keys(PASTE_KEY)
    rand_sleep()

def clear(element):
    element.clear()
    rand_sleep()

def click(element):
    element.click()
    rand_sleep()

