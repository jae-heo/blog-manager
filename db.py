import sqlite3
from datetime import datetime

# BlogTable
# id (autogeneration)
# blog_id (str)
# comment_count (int)
# like_count (int)
# neighbor_request_date (date) 일주일동안 안받으면 삭제하는 로직이 필요
# neighbor_request_current (boolean)
# neighbor_request_rmv (boolean) true = 삭제되었다.
# created_date
# updated_date
# today_list_update (0, 1)

# BlogPostTable
# id (user key)
# blog_post_id (str)
# post_id (str)
# post_name (str)
# post_body (str)
# written_comment (str)
# is_liked (boolean)
# created_date
# updated_date

class DbManager:
    def __init__(self, path = "./test.db"):
        self.con = sqlite3.connect(path)
        self.c = self.con.cursor()

        # UserTable 생성
        sql_blog_table = """
                    CREATE TABLE IF NOT EXISTS BlogTable (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        blog_id TEXT NOT NULL,
                        comment_count INTEGER DEFAULT 0 NOT NULL,
                        like_count INTEGER DEFAULT 0 NOT NULL,
                        today_list_update INTEGER DEFAULT 0 NOT NULL,
                        neighbor_request_date DATE,
                        neighbor_request_current DEFAULT FALSE NOT NULL,
                        neighbor_request_rmv DEFAULT FALSE NOT NULL,
                        created_date DATE DEFAULT CURRENT_TIMESTAMP NOT NULL,
                        updated_date DATE DEFAULT CURRENT_TIMESTAMP NOT NULL
                    );
                """
        self.c.execute(sql_blog_table)

        # UserPostTable 생성
        sql_blog_post_table = """
                    CREATE TABLE IF NOT EXISTS BlogPostTable (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        blog_post_id TEXT NOT NULL,
                        post_id TEXT NOT NULL,
                        post_name TEXT NOT NULL,
                        post_body TEXT NOT NULL,
                        written_comment TEXT NOT NULL,
                        is_liked BOOLEAN DEFAULT FALSE NOT NULL,
                        created_date DATE DEFAULT CURRENT_DATE NOT NULL,
                        updated_date DATE DEFAULT CURRENT_DATE NOT NULL
                    );
                """
        self.c.execute(sql_blog_post_table)

    # BlogTable 관련 함수
    ############################################################################################

    # 특정 blog id의 정보를 삭제하는 코드
    def delete_blog(self, blog_id):
        # Delete the record from BlogTable
        sql_delete_blog = "DELETE FROM BlogTable WHERE blog_id = ?"
        self.c.execute(sql_delete_blog, (blog_id,))
        # Delete the record from BlogPostTable
        sql_delete_blog_posts = "DELETE FROM BlogPostTable WHERE blog_post_id = ?"
        self.c.execute(sql_delete_blog_posts, (blog_id,))
        self.con.commit()

        print(f"이 Blog ID {blog_id} 의 정보는 삭제되었습니다.")

    # BlogTable에 blog_id 저장하는 함수, id 중복 확인하기 기능 추가하기
    def insert_blog_record_with_id(self, blog_id):
        sql_check_duplicate = """
            SELECT blog_id FROM BlogTable WHERE blog_id = ?;
        """
        self.c.execute(sql_check_duplicate, (blog_id,))
        existing_blog = self.c.fetchone()

        if existing_blog:
            print(f"Blog with ID {blog_id} already exists. Skipping insertion.")
            return

        sql_insert_blog = """
            INSERT INTO BlogTable (blog_id)
            VALUES (?);
        """
        self.c.execute(sql_insert_blog, (blog_id,))
        self.con.commit()
        print(f"Blog with ID {blog_id} inserted successfully.")

        # BlogTable에 blog_id 저장하는 함수, id 중복 확인하기 기능 추가하기
    def insert_blogs_record_with_ids(self, blog_ids):
        count = 0
        all_blogs = self.get_all_blogs()
        if all_blogs:
            all_ids = [blog["blog_id"] for blog in all_blogs]
        else:
            all_ids = None

        for blog_id in blog_ids:
            if all_ids:
                if blog_id in all_ids:
                    print(f"Blog with ID {blog_id} already exists. Skipping insertion.")
                    continue
            else:
                sql_insert_blog = """
                    INSERT INTO BlogTable (blog_id)
                    VALUES (?);
                """
                self.c.execute(sql_insert_blog, (blog_id,))
                count += 1

        self.con.commit()
        print(f"{count} blogs inserted successfully.")

    # Blogtable blog_id 전체 출력
    def get_all_blog_ids(self):
        sql_get_all_blog_ids = "SELECT blog_id FROM BlogTable"
        self.c.execute(sql_get_all_blog_ids)
        blog_ids = self.c.fetchall()
        if not blog_ids:
            print("BlogTable에서 찾지 못했습니다.")
        else:
            print("모든 Blog IDs:")
            for blog_id in blog_ids:
                print(blog_id[0])


    # BlogTable의 comment_counts 출력
    def get_blog_comment_count(self, blog_id):
        sql_get_blog_comment_count = "SELECT comment_count FROM BlogTable WHERE blog_id = ?"
        self.c.execute(sql_get_blog_comment_count, (blog_id,))
        comment_count = self.c.fetchone()
        if comment_count is None:
            print(f"No Comments found for Blog ID: {blog_id}.")
        else:
            print(f"Blog ID: {blog_id}, Comment Count: {comment_count[0]}")
            return comment_count[0]

    # BlogTable의 like_counts 출력
    def get_blog_like_count(self, blog_id):
        sql_get_blog_like_count = "SELECT like_count FROM BlogTable WHERE blog_id = ?"
        self.c.execute(sql_get_blog_like_count, (blog_id,))
        like_count = self.c.fetchone()
        if like_count is None:
            print(f"No Likes found for Blog ID: {blog_id}.")
        else:
            print(f"Blog ID: {blog_id}, Like Count: {like_count[0]}")
            return like_count[0]

    # BlogTable의 neighbor_request_date 출력
    def get_blog_neighbor_request_date(self, blog_id):
        sql_get_blog_neighbor_request_date = "SELECT neighbor_request_date FROM BlogTable WHERE blog_id = ?"
        self.c.execute(sql_get_blog_neighbor_request_date, (blog_id,))
        neighbor_request_date = self.c.fetchone()
        if neighbor_request_date is None:
            print(f"No Neighbor Request Date found for Blog ID: {blog_id}.")
        else:
            print(f"Blog ID: {blog_id}, Neighbor Request Date: {neighbor_request_date[0]}")
            return neighbor_request_date[0]

    # BlogTable의 neighbor_request_current count 반환
    def get_true_blog_neighbor_request_count(self):
        sql_get_true_blog_neighbor_request_count = "SELECT COUNT(*) FROM BlogTable WHERE neighbor_request_current = ?"
        # True인 경우만 count
        true_count = 0
        self.c.execute(sql_get_true_blog_neighbor_request_count, (True,))
        true_count += self.c.fetchone()[0]

        return true_count

    # BlogTable의 neighbor_request_current 반환
    def get_blog_neighbor_request_current(self, blog_id):
        sql_get_blog_neighbor_request_current = "SELECT neighbor_request_current FROM BlogTable WHERE blog_id = ?"
        self.c.execute(sql_get_blog_neighbor_request_current, (blog_id,))
        result = self.c.fetchone()

        if result:
            return result[0]  # neighbor_request_current의 값 반환 (True 또는 False)
        else:
            return None  # blog_id에 해당하는 레코드가 없을 경우 None 반환


    # BlogTable의 created_date 출력
    def get_blog_created_date(self, blog_id):
        sql_get_blog_created_date = "SELECT created_date FROM BlogTable WHERE blog_id = ?"
        self.c.execute(sql_get_blog_created_date, (blog_id,))
        created_date = self.c.fetchone()
        if created_date is None:
            print(f"No Created Date found for Blog ID: {blog_id}.")
        else:
            print(f"Blog ID: {blog_id}, Created Date: {created_date[0]}")

    # BlogTable의 updated_date 출력
    def get_blog_updated_date(self, blog_id):
        sql_get_blog_updated_date = "SELECT updated_date FROM BlogTable WHERE blog_id = ?"
        self.c.execute(sql_get_blog_updated_date, (blog_id,))
        updated_date = self.c.fetchone()
        if updated_date is None:
            print(f"No Updated Date found for Blog ID: {blog_id}.")
        else:
            print(f"Blog ID: {blog_id}, Updated Date: {updated_date[0]}")


    #BlogTable의 neighbor_request_date 업데이트
    def update_neighbor_request_date(self, blog_id, current_date):
        if not isinstance(current_date, str):
            print("잘못된 current_date 형식입니다. 날짜 문자열을 입력하세요.")
            return

        # neighbor_request_date를 주어진 current_date 값으로 업데이트
        sql_update_date = "UPDATE BlogTable SET neighbor_request_date = ? WHERE blog_id = ?"
        self.c.execute(sql_update_date, (current_date, blog_id))
        self.con.commit()

        print(f"Blog ID {blog_id}에 대한 이웃 요청 날짜가 {current_date}로 업데이트되었습니다.")

    # BlogTable의 neighbor_request_current 업데이트
    def update_neighbor_request_current(self, blog_id, neighbor_request_status):
        if neighbor_request_status not in [True, False]:
            print("잘못된 neighbor_request_status입니다. True 또는 False를 입력하세요.")
            return

        # neighbor_request_current를 주어진 neighbor_request_status 값으로 업데이트
        sql_update_current = "UPDATE BlogTable SET neighbor_request_current = ? WHERE blog_id = ?"
        self.c.execute(sql_update_current, (neighbor_request_status, blog_id))
        self.con.commit()

        print(f"Blog ID {blog_id}에 대한 이웃 요청 상태가 {neighbor_request_status}로 업데이트되었습니다.")


    #이웃 신청 삭제 확인
    def update_neighbor_request_rmv(self, blog_id, neighbor_request_status):
        if neighbor_request_status not in [True, False]:
            print("잘못된 neighbor_request_status입니다. True 또는 False를 입력하세요.")
            return

        # neighbor_request_rmv를 주어진 neighbor_request_status 값으로 업데이트
        sql_update_current = "UPDATE BlogTable SET neighbor_request_rmv = ? WHERE blog_id = ?"
        self.c.execute(sql_update_current, (neighbor_request_status, blog_id))
        self.con.commit()

        print(f"Blog ID {blog_id}에 대한 이웃 요청 삭제 현황 상태가 {neighbor_request_status}로 업데이트되었습니다.")


    #like count 증가
    def update_like_count(self, blog_id):
        sql_get_blog_like_count = "SELECT like_count FROM BlogTable WHERE blog_id = ?"
        self.c.execute(sql_get_blog_like_count, (blog_id,))
        current_like_count = self.c.fetchone()

        updated_like_count = current_like_count[0] + 1
        print(f"Blog ID: {blog_id}, Updated Like Count: {updated_like_count}")

        # 추가된 부분: like_count를 1 증가시켜 업데이트
        sql_update_like_count = "UPDATE BlogTable SET like_count = ? WHERE blog_id = ?"
        self.c.execute(sql_update_like_count, (updated_like_count, blog_id))
        self.con.commit()

    # like count 증가
    def update_comment_count(self, blog_id):
        sql_get_blog_comment_count = "SELECT comment_count FROM BlogTable WHERE blog_id = ?"
        self.c.execute(sql_get_blog_comment_count, (blog_id,))
        current_comment_count = self.c.fetchone()

        updated_comment_count = current_comment_count[0] + 1
        print(f"Blog ID: {blog_id}, Updated Like Count: {updated_comment_count}")

        # 추가된 부분: comment_count를 1 증가시켜 업데이트
        sql_update_comment_count = "UPDATE BlogTable SET comment_count = ? WHERE blog_id = ?"
        self.c.execute(sql_update_comment_count, (updated_comment_count, blog_id))
        self.con.commit()

    ############################################################################################

    # BlogPostTable 관련 함수
    ############################################################################################

    # BlogPostTable의 post 정보 출력

    def get_post_id(self, blog_id):
        sql_get_post_details = """
                    SELECT post_id
                    FROM BlogPostTable
                    WHERE blog_post_id = ?
                """

        self.c.execute(sql_get_post_details, (blog_id,))
        post_details = self.c.fetchall()

    def get_blog_post_details_by_blog_id(self, blog_id):
        # Assuming there's a foreign key relationship between BlogTable and BlogPostTable
        sql_get_post_details = """
            SELECT post_id, post_name, post_body, written_comment,
                   is_liked, created_date, updated_date
            FROM BlogPostTable
            WHERE blog_post_id = ?
        """

        self.c.execute(sql_get_post_details, (blog_id,))
        post_details = self.c.fetchall()

        if not post_details:
            print(f"No posts found for Blog ID: {blog_id}.")
        else:
            print(f"Posts for Blog ID: {blog_id}:")
            for post in post_details:
                post_id, post_name, post_body, written_comment, is_liked, created_date, updated_date = post
                print(f"Post ID: {post_id}, Post Name: {post_name}, Post Body: {post_body}")
                print(f"Written Comment: {written_comment}, is_liked: {is_liked}")
                print(f"Created Date: {created_date}, Updated Date: {updated_date}")
                print("\n")


    ############################################################################################


    # 테이블 출력 함수
    def list_tables(self):
        sql_list_tables = "SELECT name FROM sqlite_master WHERE type='table';"
        self.c.execute(sql_list_tables)
        tables = self.c.fetchall()

        if not tables:
            print("Table does not exist")
        else:
            print("Table list:")
            for table in tables:
                print(table[0])

    def close(self):
        self.con.close()

    # Blogtable blog_id 전체 출력
    def get_all_blogs(self):
        self.c.execute("PRAGMA table_info(BlogTable)")
        columns = [column[1] for column in self.c.fetchall()]

        self.c.execute("SELECT * FROM BlogTable")
        blogs = self.c.fetchall()

        if not blogs:
            print("BlogTable이 비었습니다.")
        else:
            result = [dict(zip(columns, blog)) for blog in blogs]
            return result

    # BlogPosttable blog_id 전체 출력
    def get_all_blog_posts(self):
        self.c.execute("PRAGMA table_info(BlogPostTable)")
        columns = [column[1] for column in self.c.fetchall()]

        self.c.execute("SELECT * FROM BlogPostTable")
        posts = self.c.fetchall()

        if not posts:
            print("BlogPostTable이 비었습니다.")
        else:
            result = [dict(zip(columns, post)) for post in posts]
            return result
        
    def update_blog(self, blog):
        sql_query = """
            UPDATE BlogTable
            SET
                blog_id = ?,
                comment_count = ?,
                like_count = ?,
                today_list_update = ?,
                neighbor_request_date = ?,
                neighbor_request_current = ?,
                neighbor_request_rmv = ?,
                created_date = ?,
                updated_date = ?
            WHERE
                id = ?
        """

        self.c.execute(sql_query, (
            blog['blog_id'],
            blog['comment_count'],
            blog['like_count'],
            blog['today_list_update'],
            blog['neighbor_request_date'],
            blog['neighbor_request_current'],
            blog['neighbor_request_rmv'],
            blog['created_date'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            blog['id']
        ))
        self.con.commit()


    def update_post(self, post):

        sql_query = """
            UPDATE BlogPostTable
            SET
                blog_post_id = ?,
                post_id = ?,
                post_name = ?,
                post_body = ?,
                written_comment = ?,
                is_liked = ?,
                created_date = ?,
                updated_date = ?
            WHERE
                id = ?
        """

        self.c.execute(sql_query, (
            post['blog_post_id'],
            post['post_id'],
            post['post_name'],
            post['post_body'],
            post['written_comment'],
            post['is_liked'],
            post['created_date'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            post['id']
        ))
        self.con.commit()

# if __name__ == "__main__":
#     db_manager = DbManager()
#     db_manager.list_tables()
#     db_manager.insert_blog_record_with_id("test1")
#     db_manager.insert_blog_record_with_id("test2")
#     db_manager.insert_blog_record_with_id("test3")
#     blog = db_manager.get_all_blogs()[0]
#     blog["blog_id"] = "modified ha ha"
#     blog["comment_count"] = 20
#     blog["neighbor_request_date"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#     blog["neighbor_request_current"] = 99
#     db_manager.update_blog(blog)
#     for blog in db_manager.get_all_blogs():
#         print(blog)

if __name__ == "__main__":
    db_manager = DbManager()
    blogs = db_manager.get_all_blogs()
    for blog in blogs:
        print(blog)
    print(len(blogs))