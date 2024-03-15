# -*- coding: utf-8 -*-
from selenium.webdriver import ActionChains

from controller.logic import *
from gensim.summarization.summarizer import summarize
from bs4 import BeautifulSoup
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
from collections import defaultdict
from common.util_function import get_chrome_driver, get_page
from PyQt5.QtCore import QThread, pyqtSignal

# Function to fetch URLs and keywords from Naver based on a search quer
client = OpenAI(api_key= "")

def fetch_urls(search_query):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    url = 'https://m.search.naver.com/search.naver?sm=mtp_hty.top&where=m&query=' + search_query
    driver.get(url)
    time.sleep(3)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    container_selector = '.fds-collection-root.nnh9m4aD2z5Tg5EMzmrA'
    title_url_selector = '.fds-comps-right-image-text-title'
    keyword_selector = ".fds-comps-header-headline.nNseP5yoY8oYoAgsI8sL"

    containers = soup.select(container_selector)
    url_data = []

    for container in containers:
        keyword_element = container.select_one(keyword_selector)
        keyword_text = keyword_element.get_text(strip=True) if keyword_element else "Keyword Not Found"

        title_url_elements = container.select(title_url_selector)
        for element in title_url_elements:
            link = element['href']
            if 'https://m.blog.naver.com/' in link or    'https://in.naver.com/' in link:
                url_data.append((keyword_text, link))

    driver.quit()
    return url_data

# Function to scrape blogs from a list of URLs
def scrape_blogs(url_data):
    title_selector = "div.se-module.se-module-text.se-title-text"
    content_selector = "div.se-main-container"  # Adjusted to a more generic container
    scraped_data = defaultdict(list)

    for keyword, url in url_data:
        try:
            response = requests.get(url)
            response.raise_for_status()

            time.sleep(10)  # Increased sleep time

            soup = BeautifulSoup(response.content, 'html.parser')
            title_element = soup.select_one(title_selector)
            title = title_element.get_text(strip=True) if title_element else "Title not found"

            # Scrape all text within the main content container
            content_element = soup.select_one(content_selector)
            if content_element:
                # Remove all link elements
                for link in content_element.find_all("a"):
                    link.decompose()  # Remove the link and its contents

                content = ' '.join(element.get_text(strip=True) for element in content_element.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li']))
                content = summarize(content, ratio=0.1)
                if not content:
                    content = "Content not found"
            else:
                content = "Content not found"

            scraped_data[keyword].append({'URL': url, 'Title': title, 'Content': content})
        except Exception as e:
            scraped_data[keyword].append({'URL': url, 'Error': f"Error: {e}"})

    return scraped_data


class PostSaveThread(QThread):
    finished_signal = pyqtSignal()
    interrupt_signal = False

    def __init__(self, driver, keyword, username, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.username = username
        self.keyword = keyword

    def run(self):
        # Integration
        search_query = self.keyword
        url_data = fetch_urls(search_query)
        all_scraped_data = scrape_blogs(url_data)
        if self.interrupt_signal:
            close_all_tabs(self.driver)
            return

        combined_data = {}

        # 모든 스크랩된 데이터에 대해 반복
        for keyword in all_scraped_data:
            if self.interrupt_signal:
                close_all_tabs(self.driver)
                return
            # 현재 키워드의 모든 데이터에 대해 반복
            titles = []  # 현재 키워드의 모든 Title을 저장할 리스트
            contents = []  # 현재 키워드의 모든 Content를 저장할 리스트

            for data in all_scraped_data[keyword]:
                if self.interrupt_signal:
                    close_all_tabs(self.driver)
                    return
                # 현재 데이터의 Title과 Content를 리스트에 추가
                titles.append(data['Title'])
                contents.append(data['Content'])

            # 현재 키워드의 모든 Title과 Content를 콤마로 구분하여 하나의 문자열로 합치기
            combined_title = ', '.join(titles)
            combined_content = ', '.join(contents)

            # 현재 키워드의 합쳐진 데이터를 combined_data 딕셔너리에 저장
            combined_data[keyword] = {'Combined_Title': combined_title, 'Combined_Content': combined_content}

        # 전체 합쳐진 Title과 Content 출력
        all_combined_titles = ', '.join(data['Combined_Title'] for keyword, data in combined_data.items())
        all_combined_contents = ', '.join(data['Combined_Content'] for keyword, data in combined_data.items())

        print(f"All Combined Titles: {{{all_combined_titles}}}")
        print(f"All Combined Contents: {{{all_combined_contents}}}")

        #제목과 부제목 선정하기
        gpt_title = all_combined_titles
        gpt_content = all_combined_contents

        response_analyze = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "read the content, but do not respond."},
                {"role": "user", "content": gpt_title + gpt_content},
                {"role": "system",
                 "content": "You are SEO Master Naver, a professional SEO analyst and optimizer with an added capability: browsing the internet for real-time information, specializing in analyzing Korean blogs, particularly those on Naver. Your role is to provide both detailed, technical aspects of SEO and general overviews suitable for a broader audience, in Korean. You maintain a balance between professionalism and accessibility, avoiding technical jargon unless specifically requested"},
                {"role": "user",
                 "content": "analyze " + gpt_title + gpt_content + " and find out the common but main keywords, questions, and phrase of each blogs without translating or altering them strictly adhere to the original Korean word. do not respond."},
                {"role": "user",
                 "content": "generate a new title and three subtitles using a common keyword from the analyzed title and content. Each subtitles should be formulated as a standalone question. The structure should be in this form: '제목: {title} , 부제목1: {subtitle},부제목2: {subtitle},부제목3: {subtitle}'. Output in Korean."},
            ]
        )
        if self.interrupt_signal:
            close_all_tabs(self.driver)
            return

        title_and_subtitles = response_analyze.choices[0].message.content
        generated_title = title_and_subtitles.split(",")[0].split(":")[1].strip()

        print(title_and_subtitles)

        example = "\n부심작입니다. 오늘은 가독성이 높은 글쓰기 방법에 대해 알아보겠습니다. 가독성이 높은 글은 독자가 읽기 쉬운 글을 말합니다. 그렇기 때문에 누구를 위한 글인지 먼저 고민하는 것이 중요합니다. 읽는 사람이 누구냐에 따라 글의 수준이나 단어 선택이 달라지기 때문입니다.예를 들면, 초등학생을 대상으로 하는 글과 임원을 대상으로 하는 글은 달라야 합니다. 왜냐하면 초등학생과 임원의 배경지식이 다르기 때문입니다. 만약 초등학생에게 어른 조차 이해하기 힘든 전문용어로 글을 쓴다면 아마 아무도 이해하지 못할 것입니다. 즉, 그 글은 읽히지 않을 것입니다. 글을 쓰는 가장 큰 목적은 독자가 읽게 만드는 것입니다. 읽히지 않는 글은 죽은 글입니다. 그래서 오늘은 잘 읽히는 글쓰기 방법에 대해 알아보겠습니다.다음 세 가지 원칙만 잘 지켜도 글은 잘 읽히게 됩니다.\n**글쓰기 세 가지 원칙(sutitles)**\n1. 핵심이 보이게 써라\n2. 짧고 명확하게 써라\n3. 가능한 많이 고쳐라"


        response_write = client.chat.completions.create(
            model="gpt-4",
            messages=[

                {"role": "user", "content": "Analyze " + example + "'s' structure, but do not respond."},
                {"role": "assistant",
                 "content": "You are a psychologist, martial counselor, and a Korean Naver Expert blogger. You are writing for people who have a relationship issue or mental issue"},
                {"role": "user",
                 "content": "write " + title_and_subtitles + " title's introduction more than 250 word Using only analyzed sentence structure. Use korean style conversational tone when writing for example, '안녕하세요! 부부상담을 받아보셨나요? 저는 상담을 받는 동안에는 많이 힘들더라구요.'. Output in Korean. Only response the introduction paragraph.  Show only subtitle and the post but do not show as such as'부제목1:' or '포스트:'."}
            ]
        )
        if self.interrupt_signal:
            close_all_tabs(self.driver)
            return

        introduction = response_write.choices[0].message.content
        print(introduction)

        response_first_subtitle = client.chat.completions.create(
          model="gpt-4",
          messages=[
            {"role": "system", "content": "read the content and title_and_subtitles, but do not respond."},
            {"role": "user", "content": title_and_subtitles},
            {"role": "user", "content": "write a professional, informative post of 부제목1 from title_and_subtitles using information of the content. write at least 200 words. Do not use 극존칭 as such as '~습니다,' but rather use 존칭 '~해요, ~네요,~죠'.Output in Korean. Show only subtitle and the post but do not show as such as'부제목1:' or '포스트:'."},

          ]
        )

        first_subtitle = response_first_subtitle.choices[0].message.content

        response_second_subtitle = client.chat.completions.create(
          model="gpt-4",
          messages=[
            {"role": "system", "content": "read the content, title_and_subtitles,and first_subtitle. Do not respond."},
            {"role": "user", "content": title_and_subtitles + first_subtitle},
            {"role": "user", "content": "write a professional, informative post of 부제목2 from title_and_subtitles using information of the content. write at least 200 words. Do not use 극존칭 as such as '~습니다,' but rather use 존칭 '~해요, ~네요,~죠'.Output in Korean. reply only subtitle and the post response. try not to write information that is already said on 'first_subtitle'. Show only subtitle and the post but do not show as such as'부제목2:' or '포스트:'."},


          ]
        )
        if self.interrupt_signal:
            close_all_tabs(self.driver)
            return


        second_subtitle = response_second_subtitle.choices[0].message.content

        response_third_subtitle = client.chat.completions.create(
          model="gpt-4",
          messages=[
            {"role": "system", "content": "read the content, title_and_subtitles,and second_subtitle. Do not respond."},
            {"role": "user", "content": title_and_subtitles + second_subtitle},
            {"role": "user", "content": "write a professional, informative post of 부제목3 from title_and_subtitles using information of the content. write at least 200 words. Do not use 극존칭 as such as '~습니다,' but rather use 존칭 '~해요, ~네요,~죠'.Output in Korean. reply only subtitle and the post response. try not to write information that is already said on 'first_subtitle'. Show only subtitle and the post but do not show as such as'부제목3:' or '포스트:'."},

          ]
        )


        third_subtitle = response_third_subtitle.choices[0].message.content



        print(first_subtitle)
        print(" ")
        print(second_subtitle)
        print(" ")
        print(third_subtitle)
        if self.interrupt_signal:
            close_all_tabs(self.driver)
            return

        url = f'https://blog.naver.com/{self.username}/postwrite'

        self.driver.get(url)

        rand_sleep(800, 900)
        if self.interrupt_signal:
            close_all_tabs(self.driver)
            return

        try:
            reload_close_button = self.driver.find_element(By.CSS_SELECTOR, '.se-popup-button-cancel')
            click(reload_close_button)
        except Exception as e:
            pass
        rand_sleep(400, 500)
        try:
            ad_close_button = self.driver.find_element(By.CSS_SELECTOR, '.se-help-panel-close-button')
            click(ad_close_button)
        except Exception as e:
            pass
        if self.interrupt_signal:
            close_all_tabs(self.driver)
            return
        rand_sleep(400, 500)
        title_field_click = self.driver.find_element(By.CSS_SELECTOR, '.se-documentTitle div div div p')
        click(title_field_click)
        rand_sleep(400, 500)
        ActionChains(self.driver).send_keys(generated_title).perform()
        rand_sleep(400, 500)
        content_field_click = self.driver.find_element(By.CSS_SELECTOR, '.se-component-content div div div p.se-text-paragraph')
        click(content_field_click)
        rand_sleep(400, 500)
        ActionChains(self.driver).send_keys(introduction).perform()
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        rand_sleep(400, 500)
        ActionChains(self.driver).send_keys(first_subtitle).perform()
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        rand_sleep(400, 500)
        ActionChains(self.driver).send_keys(second_subtitle).perform()
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        ActionChains(self.driver).send_keys(Keys.ENTER).perform()
        rand_sleep(400, 500)
        ActionChains(self.driver).send_keys(third_subtitle).perform()
        rand_sleep(400, 500)
        save_button_click = self.driver.find_element(By.CSS_SELECTOR, '.save_btn___RzjY')
        click(save_button_click)

        close_current_window(self.driver)

        self.finished_signal.emit()