from const import *
from custom_func import *
from logic import *

driver = get_chrome_driver()
naver_login(driver, DEV_ID, DEV_PW)


# get_blogs_by_search(driver, "롤 고수")
get_blogs_by_category(driver, "생활·노하우·쇼핑", "반려동물")