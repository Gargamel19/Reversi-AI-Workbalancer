from datetime import datetime, timedelta
import sqlite3

from app.db.database import DataBase


class database_started_attempts:

    path = DataBase.base_path + '/dbs/database.db'
    spoil_time = timedelta(minutes=10)

    @staticmethod
    def create_db():
        try:
            sql = "CREATE TABLE attempts_started(" \
                    "ATTEMPT_ID INTEGER PRIMARY KEY AUTOINCREMENT," \
                    "USER_ID INTEGER NOT NULL," \
                    "DEPTH INTEGER, " \
                    "CURRENT_GAME INTEGER, " \
                    "WINRATE REAL, " \
                    "GAMES_AMOUNT INTEGER, " \
                    "EXPIRE_DATE DATE, " \
                    "MATRIX BLOB)"
            DataBase.make_no_response_query(sql, database_started_attempts.path)
        except sqlite3.OperationalError:
            print("Table Exists")

    @staticmethod
    def get_attempts_of_user(user_id):
        query = "SELECT attempts_started.ATTEMPT_ID, user.USERNAME, attempts_started.DEPTH, attempts_started.GAMES_AMOUNT, attempts_started.CURRENT_GAME, attempts_started.WINRATE, attempts_started.EXPIRE_DATE FROM attempts_started JOIN User ON attempts_started.USER_ID=user.USER_ID WHERE attempts_started.User_ID = {}".format(
            user_id)
        return DataBase.make_multi_response_query(query, database_started_attempts.path)

    @staticmethod
    def get_attempts_with_username_from_querry(depth_int, games_amount, username):
        query = "SELECT attempts_started.ATTEMPT_ID, user.USERNAME, attempts_started.DEPTH, attempts_started.GAMES_AMOUNT, attempts_started.CURRENT_GAME, attempts_started.WINRATE, attempts_started.EXPIRE_DATE FROM attempts_started JOIN User ON attempts_started.USER_ID=user.USER_ID"
        added = 0
        if depth_int:
            if not added == 0:
                query += " AND"
            query += " WHERE attempts_started.DEPTH = " + depth_int
            added += 1
        if games_amount:
            if not added == 0:
                query += " AND"
            query += " WHERE attempts_started.GAMES_AMOUNT = " + games_amount
            added += 1
        if games_amount:
            if not added == 0:
                query += " AND"
            query += " WHERE user.USERNAME = " + username
            added += 1
        return DataBase.make_multi_response_query(query, database_started_attempts.path)

    @staticmethod
    def is_users_started_attempt(started_attempt_id, user_id):
        query = "SELECT USER_ID FROM attempts_started WHERE ATTEMPT_ID = {}" \
            .format(started_attempt_id)
        return user_id == DataBase.make_multi_response_query(query, database_started_attempts.path)[0][0]

    @staticmethod
    def get_attemps_with_matrix_depth_gameAmount(matrix, depth, game_amount):
        query = "SELECT * FROM attempts_started WHERE DEPTH = {} AND MATRIX= '{}' AND GAMES_AMOUNT= {}"\
            .format(depth, matrix, game_amount)
        return DataBase.make_multi_response_query(query, database_started_attempts.path)

    @staticmethod
    def update_expire_date_cg_winrate(started_attempt_id, current_game, winrate):
        query = "UPDATE attempts_started SET EXPIRE_DATE = '{}', CURRENT_GAME = {}, WINRATE = {} WHERE ATTEMPT_ID= {}" \
            .format(datetime.now() + database_started_attempts.spoil_time, current_game, winrate, started_attempt_id)
        return DataBase.make_no_response_query(query, database_started_attempts.path)


    @staticmethod
    def delete_attempt(user_id, depth, games, matrix):
        query = "DELETE FROM attempts_started WHERE USER_ID = {} AND DEPTH = {} AND GAMES_AMOUNT = {} MATRIX = {};"\
            .format(user_id, depth, games, matrix)
        return DataBase.make_single_response_query(query, database_started_attempts.path)

    @staticmethod
    def get_attempt_by_id(attempt_id):
        query = "SELECT * FROM attempts_started WHERE ATTEMPT_ID = {};" \
            .format(attempt_id)
        return DataBase.make_multi_response_query(query, database_started_attempts.path)

    @staticmethod
    def get_expired():
        query = "SELECT ATTEMPT_ID FROM attempts_started WHERE EXPIRE_DATE < '{}';" \
            .format(datetime.now())
        return DataBase.make_multi_response_query(query, database_started_attempts.path)

    @staticmethod
    def delete_attempt_by_id(attempt_id):
        query = "DELETE FROM attempts_started WHERE ATTEMPT_ID = {};" \
            .format(attempt_id)
        return DataBase.make_no_response_query(query, database_started_attempts.path)

    @staticmethod
    def insert_attempt(user_id, depth, games, matrix):
        connection = sqlite3.connect(database_started_attempts.path)
        cursor = connection.cursor()

        sql = "INSERT INTO attempts_started(USER_ID, DEPTH, GAMES_AMOUNT, CURRENT_GAME, WINRATE, EXPIRE_DATE, MATRIX) VALUES('{}', '{}', '{}', '{}', '{}', '{}', '{}')"\
            .format(user_id, depth, games, 0, 0.0, datetime.now() + database_started_attempts.spoil_time, matrix)
        cursor.execute(sql)
        attempt_id = cursor.lastrowid
        connection.commit()
        connection.close()
        return attempt_id
