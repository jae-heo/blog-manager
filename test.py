from const import *
from custom_func import *
from logic import *

driver = get_chrome_driver()

get_page(driver, 'http://www.naver.com')
open_new_window(driver)
get_page(driver, 'http://www.naver.com')
open_new_window(driver)
get_page(driver, 'http://www.naver.com')

close_all_tabs(driver)