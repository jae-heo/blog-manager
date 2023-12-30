from const import *
from custom_func import *
from logic import *

driver = get_chrome_driver()
naver_login(driver, DEV_ID, DEV_PW)