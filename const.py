from selenium.webdriver import Keys
import platform

BLOG_MAIN_URL = "https://section.blog.naver.com"
NAVER_LOGIN_URL = "https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/"
DEV_ID = "fuhafuha9"
DEV_PW = "tofhdl19!"

if platform.system() == "Windows":
    PASTE_KEY = Keys.LEFT_CONTROL + 'v'
elif platform.system() == "Darwin":
    PASTE_KEY = Keys.COMMAND + 'v'



