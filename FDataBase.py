# -*-coding: utf-8 -*-
import datetime
import sqlite3

class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("Ошибка чтения из БД")
        return []

    def get_all_posts(self):
        try:
            self.__cur.execute(
                f"SELECT * FROM posts")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения из БД" + str(e))
        return False

    def get_all_authors(self):
        try:
            self.__cur.execute(
                f"SELECT * FROM authors")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения из БД" + str(e))
        return False

    def get_all_topics(self):
        try:
            self.__cur.execute(
                f"SELECT * FROM topics")
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения из БД" + str(e))
        return False

    def get_posts_by_author(self, id):
        try:
            self.__cur.execute(
                f"SELECT * FROM posts where id_user == :id", (id,))
            res = self.__cur.fetchall()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения из БД" + str(e))
        return False

    def get_posts_by_topic(self, id_topics):
        try:
            self.__cur.execute(
                f"SELECT * FROM posts where id_topics == :id_topics", (id_topics,))
            res = self.__cur.fetchall()
            if res:
                # print("posts_t")
                # for r in res:
                #     print(r[0])
                return res
        except sqlite3.Error as e:
            print("Ошибка получения из БД" + str(e))
        return False

    def get_post_by_id(self, id):
        try:
            self.__cur.execute(
                f"SELECT * FROM posts where id == :id", (id,))
            res = self.__cur.fetchone()
            if res:
                # print("posts_t")
                # for r in res:
                #     print(r[0])
                return res
        except sqlite3.Error as e:
            print("Ошибка получения из БД" + str(e))
        return False

    def get_id_author(self, login):
        try:
            self.__cur.execute(
                f"SELECT * FROM authors where login == :login", (login,))
            res = self.__cur.fetchone()
            if res:
                return res[0]
        except sqlite3.Error as e:
            print("Ошибка получения из БД" + str(e))
        return False

    def get_author_by_id(self, idd):

        try:
            self.__cur.execute(
                f"SELECT * FROM authors where id == :id", (idd,))
            res = self.__cur.fetchone()
            if res:
                print(type(idd))
                return res
        except sqlite3.Error as e:
            print("Ошибка получения из БД" + str(e))
        return False

    def get_id_topic(self, title):
        try:
            self.__cur.execute(
                f"SELECT * FROM topics where title == :title", (title,))
            res = self.__cur.fetchone()
            if res:
                return res[0]
        except sqlite3.Error as e:
            print("Ошибка получения из БД" + str(e))
        return False

    def add_post(self, title, text, id_user, id_topics):
        try:
            date_ = datetime.datetime.now()
            print(date_)
            sql = """INSERT INTO posts (title, text, url, time, id_user, id_topics)
                      values (:title, :text, :url, :time, :id_user, :id_topics)"""
            self.__cur.execute(sql, [title, text, "url", date_, id_user, id_topics])
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БДLL " + str(e))
            return False
        return True

    def delete_post(self, idd):
        try:
            sql1 = """DELETE FROM posts WHERE id == :idd"""
            self.__cur.execute(sql1, (idd,))
            self.__db.commit()
            res = self.__cur.fetchone()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка при удалении комментария из БД " + str(e))
        return False

    def delete_auth(self, idd):
        try:
            sql1 = """DELETE FROM authors WHERE id == :idd"""
            self.__cur.execute(sql1, (idd,))
            self.__db.commit()
            res = self.__cur.fetchone()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка при удалении комментария из БД " + str(e))
        return False

    def add_auth(self, login):
        try:
            date_ = datetime.datetime.now()
            print(date_)
            sql = """INSERT INTO authors (login)
                         values (:login)"""
            self.__cur.execute(sql, (login,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БДLL " + str(e))
            return False
        return True

    def add_topic(self, title):
        try:
            date_ = datetime.datetime.now()
            print(date_)
            sql = """INSERT INTO topics (title)
                         values (:title)"""
            self.__cur.execute(sql, (title,))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД " + str(e))
            return False
        return True

    def addTopic(self, title):
        print(title)
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM posts WHERE title LIKE '{title}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Статья с таким url уже существует")
                return False

            self.__cur.execute("INSERT INTO topics VALUES(?, ?)", (0, title))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД " + str(e))
            return False

        return True

    def getPostsAnonce1(self, id_user):
        try:
            self.__cur.execute(f"SELECT id, title, text, url FROM posts where id_user = '{id_user}' ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return []

    def getPostsAnonce(self):
        try:
            self.__cur.execute(f"SELECT id, title, text, url FROM posts ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД " + str(e))

        return []

    def update_post(self, id, title, text):
        print("update_post")
        print(text)
        try:
            sql = """UPDATE posts SET title=:title, text=:text where id=:id"""
            self.__cur.execute(sql, [title, text, id])
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БДLL " + str(e))
            return False
        self.__cur.execute(f"SELECT * FROM posts where id=:id", [id])
        res = self.__cur.fetchone()
        print(res[0])
        return True