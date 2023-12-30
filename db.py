import sqlite3
import string
from random import random


# BlogTable
# id (autogeneration)
# blog_id (str)
# comment_count (int)
# like_count (int)
# neighbor_request_date (date) 일주일동안 안받으면 삭제하는 로직이 필요
# created_date
# updated_date

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
    def __init__(self, path):
        self.con = sqlite3.connect(path)
        self.c = self.con.cursor()

        # UserTable 생성
        sql_blog_table = """
                    CREATE TABLE IF NOT EXISTS BlogTable (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        blog_id TEXT NOT NULL,
                        comment_count INTEGER DEFAULT 0 NOT NULL,
                        like_count INTEGER DEFAULT 0 NOT NULL,
                        neighbor_request_date DATE,
                        created_date DATE DEFAULT CURRENT_DATE NOT NULL,
                        updated_date DATE DEFAULT CURRENT_DATE NOT NULL
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

    # BlogTable에 blog_id 저장하는 함수
    def insert_blog_record_with_id(self, blog_id):
        sql_insert_blog = """
            INSERT INTO BlogTable (blog_id)
            VALUES (?);
        """
        self.c.execute(sql_insert_blog, (blog_id))
        self.con.commit()

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

    # BlogTable의 like_counts 출력
    def get_blog_like_count(self, blog_id):
        sql_get_blog_like_count = "SELECT like_count FROM BlogTable WHERE blog_id = ?"
        self.c.execute(sql_get_blog_like_count, (blog_id,))
        like_count = self.c.fetchone()
        if like_count is None:
            print(f"No Likes found for Blog ID: {blog_id}.")
        else:
            print(f"Blog ID: {blog_id}, Like Count: {like_count[0]}")

    # BlogTable의 neighbor_request_date 출력
    def get_blog_neighbor_request_date(self, blog_id):
        sql_get_blog_neighbor_request_date = "SELECT neighbor_request_date FROM BlogTable WHERE blog_id = ?"
        self.c.execute(sql_get_blog_neighbor_request_date, (blog_id,))
        neighbor_request_date = self.c.fetchone()
        if neighbor_request_date is None:
            print(f"No Neighbor Request Date found for Blog ID: {blog_id}.")
        else:
            print(f"Blog ID: {blog_id}, Neighbor Request Date: {neighbor_request_date[0]}")

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

    ############################################################################################

    # BlogPostTable 관련 함수
    ############################################################################################

    # BlogPostTable의 post 정보 출력
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


db_manager = DbManager('./test.db')

# db_manager.create_user('Jae')

# 테이블 리스트 출력
db_manager.list_tables()
