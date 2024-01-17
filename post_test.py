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

# Function to fetch URLs and keywords from Naver based on a search quer


def fetch_urls(search_query):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    url = 'https://m.search.naver.com/search.naver?sm=mtp_hty.top&where=m&query=' + search_query
    driver.get(url)
    time.sleep(3)

    html_content = driver.page_source
    soup = BeautifulSoup(html_content, 'html.parser')

    container_selector = '.fds-collection-root.cKb9yIrmHdM7ZPaospZ3'
    title_url_selector = '.fds-comps-right-image-text-title'
    keyword_selector = ".fds-comps-header-headline.cR7J2pBJXWSm_NIcJO9d"

    containers = soup.select(container_selector)
    url_data = []

    for container in containers:
        keyword_element = container.select_one(keyword_selector)
        keyword_text = keyword_element.get_text(strip=True) if keyword_element else "Keyword Not Found"

        title_url_elements = container.select(title_url_selector)
        for element in title_url_elements:
            link = element['href']
            if 'https://m.blog.naver.com/' in link or 'https://in.naver.com/' in link:
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
                content = summarize(content, ratio=0.2)
                if not content:
                    content = "Content not found"
            else:
                content = "Content not found"

            scraped_data[keyword].append({'URL': url, 'Title': title, 'Content': content})
        except Exception as e:
            scraped_data[keyword].append({'URL': url, 'Error': f"Error: {e}"})

    return scraped_data

# Integration
search_query = input("키워드를 입력해주세요: ")
url_data = fetch_urls(search_query)
all_scraped_data = scrape_blogs(url_data)

for keyword in all_scraped_data:
    print(f"Keyword: {keyword}")
    for data in all_scraped_data[keyword]:
        print(f"  URL: {data['URL']}")
        print(f"  Title: {data['Title']}")
        print(f"  Content: {data['Content']}\n")


#제목과 부제목 선정하기

