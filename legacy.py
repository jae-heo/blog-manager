# 언젠가 참고할만한 코드를 처박아놓는 쓰레기통
def search_in_blog(driver, search_keyword, neighbor_request_message):
    open_new_window(driver)
    get_page(driver, BLOG_MAIN_URL)

    #블로그 검색창에 입력
    search_bar_element = driver.find_element(By.XPATH, '//*[@id="header"]/div[1]/div/div[2]/form/fieldset/div/input')
    key_in(search_bar_element, search_keyword)
    search_button_element = driver.find_element(By.XPATH, '//*[@id="header"]/div[1]/div/div[2]/form/fieldset/a[1]')
    click(search_button_element)

    while True:
        # 페이지 별로 순회하면서 사용자를 얻어내는 코드
        for i in range(0, len(driver.find_elements(By.CSS_SELECTOR, ".pagination span a"))):
            for author in driver.find_elements(By.CSS_SELECTOR, ".writer_info .author"):
                # 페이지에 있는 사용자들을 전부 불러와서 해당 사용자에게 서로이웃을 신청하는 코드
                blog_id = author.get_attribute("href").split("/")[3]
                blog_url = "https://m.blog.naver.com/" + blog_id

                open_new_window(driver)
                get_page(driver, blog_url)

                add_neighbor_button = driver.find_element(By.CLASS_NAME, "add_buddy_btn__oGR_B")
                click(add_neighbor_button)

                try:
                    both_buddy_radio = driver.find_element(By.ID, "bothBuddyRadio")

                    # 만약 서이추가 가능한 사람일 경우
                    if both_buddy_radio.get_attribute("ng-disabled") == "false":
                        # 서이추 버튼 클릭
                        click(both_buddy_radio)
                        # 서이추 메세지 입력
                        neighbor_request_message_text_area = driver.find_element(By.CSS_SELECTOR, ".add_msg textarea")
                        clear(neighbor_request_message_text_area)
                        key_in(neighbor_request_message_text_area, neighbor_request_message)
                        neighbor_request_button = driver.find_element(By.CLASS_NAME, "btn_ok")
                        click(neighbor_request_button)
                except NoSuchElementException as e:
                    # 이경우는 이미 서이추가 되어있는 사람이라서 그냥 넘어가는 것으로..
                    pass

                # 이제 열었던 창을 닫아야 함.
                close_current_window(driver)

            if i != len(driver.find_elements(By.CSS_SELECTOR, ".pagination span a")):
                driver.find_elements(By.CSS_SELECTOR, ".pagination span a")[i + 1].click()
                rand_sleep()

        try:
            driver.find_element(By.CSS_SELECTOR, ".pagination .button_next").click()
            rand_sleep()
        except NoSuchElementException as e:
            logging.getLogger("main").info("블로그의 모든 글을 탐색했습니다.")
            break