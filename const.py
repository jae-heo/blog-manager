from selenium.webdriver import Keys
import platform

BLOG_MAIN_URL = "https://section.blog.naver.com"
NAVER_LOGIN_URL = "https://nid.naver.com/nidlogin.login?mode=form&url=https://www.naver.com/"
DEV_ID = "pgw031203"
DEV_PW = "qkrrjsdn03!@"

if platform.system() == "Windows":
    PASTE_KEY = Keys.LEFT_CONTROL + 'v'
elif platform.system() == "Darwin":
    PASTE_KEY = Keys.COMMAND + 'v'

MAIN_CATEGORIES = {
    "관심주제": "cmn*m.kw0",
    "엔터테인먼트·예술": "cmn*e.book",
    "생활·노하우·쇼핑": "cmn*l.life",
    "취미·여가·여행": "cmn*h.game",
    "지식·동향": "cmn*i.it"
}

SUB_CATEGORIES = {
    "문학·책": "cmn*e.book",
    "영화": "cmn*e.movie",
    "미술·디자인": "cmn*e.art",
    "공연·전시": "cmn*e.perform",
    "음악": "cmn*e.music",
    "드라마": "cmn*e.drama",
    "스타·연예인": "cmn*e.celeb",
    "만화·애니": "cmn*e.comic",
    "방송": "cmn*e.broadcast",
    "일상·생각": "cmn*l.life",
    "육아·결혼": "cmn*l.baby",
    "반려동물": "cmn*l.pet",
    "좋은글·이미지": "cmn*l.story",
    "패션·미용": "cmn*l.fashion",
    "인테리어·DIY": "cmn*l.interior",
    "요리·레시피": "cmn*l.cook",
    "상품리뷰": "cmn*l.review",
    "원예·재배": "cmn*l.garden",
    "게임": "cmn*h.game",
    "스포츠": "cmn*h.sports",
    "사진": "cmn*h.pic",
    "자동차": "cmn*h.car",
    "취미": "cmn*h.hobby",
    "국내여행": "cmn*h.itravel",
    "세계여행": "cmn*h.otravel",
    "맛집": "cmn*h.food",
    "IT·컴퓨터": "cmn*i.it",
    "사회·정치": "cmn*i.society",
    "건강·의학": "cmn*i.health",
    "비즈니스·경제": "cmn*i.economy",
    "어학·외국어": "cmn*i.language",
    "교육·학문": "cmn*i.edu",
}