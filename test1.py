from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

url = "https://m.blog.naver.com/oreore23?categoryNo=0&listStyle=card&tab=1"

# Set up the Chrome WebDriver (you can use other drivers as well)
driver = webdriver.Chrome()

# Function to get the latest post URL
def get_post_id(driver, blog_url, current_xpath):
    # Navigate to the provided blog URL
    driver.get(blog_url)

    # Use WebDriverWait to wait for the elements to be present
    wait = WebDriverWait(driver, 10)

    # Find the latest post element using the provided XPath
    latest_post = wait.until(EC.presence_of_element_located((By.XPATH, current_xpath)))

    # Extract the URL of the latest post
    latest_post_url = latest_post.find_element(By.TAG_NAME, "a").get_attribute("href")

    parsed_url = urlparse(latest_post_url)
    query_params = parse_qs(parsed_url.query)
    post_id = query_params.get('logNo', [''])[0]

    return post_id

# Print the URL of the latest post
print(get_post_id(driver, url, current_xpath='//*[@id="contentslist_block"]/div[2]/div/div[2]/ul/li[1]'))

# Close the WebDriver
driver.quit()