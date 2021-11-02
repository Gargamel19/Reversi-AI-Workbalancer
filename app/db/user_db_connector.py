from datetime import datetime, timedelta
import os
import re
import sqlite3

import bcrypt

from app.db.database import DataBase


class user_db_connector:

    code_spoil_time = timedelta(minutes=30)
    path = DataBase.base_path + '/dbs/database.db'

    @staticmethod
    def Has_Illegal_Chars(string):
        search_result = re.search(r"[^a-zA-Z0-9_-]", string)
        if search_result:
            return True
        return False

    @staticmethod
    def create_db():
        try:
            sql = "CREATE TABLE user(" \
                  "USER_ID INTEGER PRIMARY KEY AUTOINCREMENT," \
                  "USERNAME TEXT UNIQUE, " \
                  "PASSWORD TEXT, " \
                  "HASH TEXT," \
                  "ROLLE TEXT," \
                  "VALID_TO DATE)"
            DataBase.make_no_response_query(sql, user_db_connector.path)
        except sqlite3.OperationalError:
            print("Table Exists")

    @staticmethod
    def get_user_hash_from_user_id(user_id):
        query = "SELECT HASH FROM user WHERE USER_ID = " + str(user_id)
        return DataBase.make_single_response_query(query, user_db_connector.path)

    @staticmethod
    def get_password(user_id):
        query = "SELECT PASSWORD FROM user WHERE USER_ID = " + str(user_id) + ""
        return DataBase.make_single_response_query(query, user_db_connector.path)

    @staticmethod
    def get_user_id_by_hash(user_hash):
        query = "SELECT USER_ID FROM user WHERE HASH = '{}'".format(user_hash)
        return DataBase.make_single_response_query(query, user_db_connector.path)

    @staticmethod
    def get_hash_from_user_id(user_id):
        query = "SELECT HASH FROM user WHERE user_id = " + str(user_id)
        return DataBase.make_single_response_query(query, user_db_connector.path)

    @staticmethod
    def get_user_id_from_user_name(user_name):
        query = "SELECT user_id FROM user WHERE username = '" + user_name + "'"
        return DataBase.make_single_response_query(query, user_db_connector.path)

    @staticmethod
    def get_user_name_from_user_id(user_id):
        query = "SELECT username FROM user WHERE user_id = " + str(user_id)
        return DataBase.make_single_response_query(query, user_db_connector.path)

    @staticmethod
    def insert_user(username, password, user_hash, rolle="noob"):
        if user_db_connector.Has_Illegal_Chars(username):
            raise Exception("Error: Can't create Account with illegal Characters.")
        encoded_password = password.encode('UTF-8')
        hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
        decoded_password = hashed_password.decode("UTF-8")
        connection = sqlite3.connect(user_db_connector.path)
        cursor = connection.cursor()
        sql = "INSERT INTO user(USERNAME, PASSWORD, HASH, VALID_TO, ROLLE) VALUES('{}','{}','{}','{}','{}')"\
            .format(username, decoded_password, user_hash, str(datetime.now() + user_db_connector.code_spoil_time), rolle)
        cursor.execute(sql)
        user_id = cursor.lastrowid
        connection.commit()
        connection.close()
        return user_id

    @staticmethod
    def edit_user(user_id, password):

        encoded_password = password.encode('UTF-8')
        hashed_password = bcrypt.hashpw(encoded_password, bcrypt.gensalt())
        decoded_password = hashed_password.decode("UTF-8")
        sql = "UPDATE user SET password = '" + decoded_password + "' WHERE user_id = " + str(user_id)
        DataBase.make_no_response_query(sql, user_db_connector.path)

    @staticmethod
    def update_user_hash(user_id, user_hash):
        sql = "UPDATE user SET hash = '" + user_hash + "', valid_to = '" + str(datetime.now() + user_db_connector.code_spoil_time) + \
              "' WHERE user_id = " + str(user_id)
        DataBase.make_no_response_query(sql, user_db_connector.path)

    @staticmethod
    def has_user(user_id):
        sql = "SELECT * FROM user WHERE user_id = " + str(user_id)
        response = DataBase.make_single_response_query(sql, user_db_connector.path)
        if response is None:
            return False
        return True

    @staticmethod
    def login_user(username, password):
        if user_db_connector.Has_Illegal_Chars(username):
            return False
        encoded_password = password.encode('UTF-8')
        user_id = user_db_connector.get_user_id_from_user_name(username)
        if user_id is None:
            return False
        db_password = user_db_connector.get_password(user_id)
        if db_password is None:
            return False
        db_password = db_password.encode('UTF-8')
        pass_correct = bcrypt.checkpw(encoded_password, db_password)
        if pass_correct:
            return True
        return False

    @staticmethod
    def is_user_admin(user_id):
        sql = "SELECT ROLLE FROM user WHERE user_id = " + str(user_id)
        role = DataBase.make_single_response_query(sql, user_db_connector.path)
        if role == "admin":
            return True
        return False

    @staticmethod
    def get_hash_is_verify_from_user_id(user_id):
        connection = sqlite3.connect(user_db_connector.path)

        cursor = connection.cursor()

        sql = "SELECT VALID_TO FROM user WHERE user_id = " + str(user_id)
        try:
            cursor.execute(sql)
            msg = cursor.fetchone()
            if msg is not None:
                date = datetime.strptime(msg[0], '%Y-%m-%d %H:%M:%S.%f')
                connection.close()
                return date > datetime.now()
        except sqlite3.OperationalError:
            print("Invalid username: " + user_id)
            return None
        return None
