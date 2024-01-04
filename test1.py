from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://m.blog.naver.com/oreore23?categoryNo=0&listStyle=card&tab=1"

# 크롬 WebDriver 설정 (다른 드라이버를 사용해도 됩니다)
driver = webdriver.Chrome()

# URL로 이동
driver.get(url)

# 요소가 나타날 때까지 대기하기 위해 WebDriverWait 사용
wait = WebDriverWait(driver, 10)

# 페이지에 있는 모든 게시물 요소 찾기
post_elements = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "item__O332w")))

# 페이지에 최소한 두 개의 게시물이 있는지 확인
if len(post_elements) >= 2:
    # 두 번째로 최신 게시물의 URL 추출 및 출력
    second_latest_post_url = post_elements[0].find_element(By.TAG_NAME, "a").get_attribute("href")
    print("두 번째 최신 게시물 URL:", second_latest_post_url)
else:
    print("페이지에 충분한 수의 게시물이 없습니다.")

# WebDriver 닫기
driver.quit()