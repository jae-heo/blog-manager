from const import *
from custom_func import *
from logic import *

driver = get_chrome_driver()
# naver_login(driver, DEV_ID, DEV_PW)

get_blogs_by_category(driver, "취미·여가·여행", "국내여행")