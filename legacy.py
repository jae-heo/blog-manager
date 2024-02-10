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
        

# #주제별 보기 클릭
# button = driver.find_element(By.CSS_SELECTOR, "a[bg-nclick='lnb.catergory']")
# button.click()
# rand_sleep()
# # 엔터테인먼트 예술, 생활 노하우 쇼핑, 취미 여가 여행, 지식 동향 중 하나를 클릭해야함
# buttons = driver.find_elements(By.CSS_SELECTOR, ".navigator_category .item")
# button_list = []
# # 각 버튼의 정보를 리스트에 추가
# for button in buttons:
#     button_text = button.find_element(By.CLASS_NAME, "category_name").text
#     button_list.append({"text": button_text, "element": button})
# # 리스트 출력 또는 활용
# for button_info in button_list:
#     print(f"버튼 텍스트: {button_info['text']}")
# # button_list에서 텍스트를 돌면서 원하는 분야의 글을 선택한다.
# button_list[1]["element"].click()
# rand_sleep()



class InitializeThread(NThread):
    def __init__(self, driver, username, db_name, parent=None):
        super().__init__(parent)
        self.driver = driver
        self.username = username
        self.db_name = db_name

    def run(self):
        db_manager = DbManager(self.db_name)
        open_new_window(self.driver)
        url = f"https://admin.blog.naver.com/BuddyListManage.naver?blogId={self.username}"
        get_page(self.driver, url)
        buddy_ids = []
        while True:
            if self.interrupt_signal:
                print("InitializeThread interrupted.")
                break

            # 검색결과의 페이지 별 순회
            current_page_element = self.driver.find_element(By.CSS_SELECTOR, '.paginate .paginate_re strong')
            current_page_text = current_page_element.text
            current_page_text_copy = current_page_text
            active_page_buttons = self.driver.find_elements(By.CSS_SELECTOR, '.paginate .paginate_re a')

            # 로직
            buddies = self.driver.find_elements(By.CSS_SELECTOR, ".buddy .ellipsis2 a")
            for buddy in buddies:
                blog_id = buddy.get_attribute("href").split("/")[3]
                buddy_ids.append(blog_id)

            for page_button in active_page_buttons:
                if int(page_button.text) == int(current_page_text) + 1:
                    click(page_button)
                    current_page_text = self.driver.find_element(By.CSS_SELECTOR, '.paginate .paginate_re strong').text
            
            # 만약 다음 페이지가 없다면
            if current_page_text == current_page_text_copy:
                break

        db_manager.insert_blogs_record_with_ids(buddy_ids)
        blogs = db_manager.get_all_blogs()
        for blog in blogs:
            created_date = blog['created_date']
            created_date = datetime.strptime(created_date, '%Y-%m-%d %H:%M:%S')
            blog['created_date'] = created_date - timedelta(days=1)
            db_manager.update_blog(blog)
        close_current_window(self.driver)
        self.finished_signal.emit()
