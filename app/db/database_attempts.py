import os
import datetime
import sqlite3

from app.db.database import DataBase


class database_attempts:

    path = DataBase.base_path + '/dbs/database.db'

    @staticmethod
    def create_db():
        try:
            sql = "CREATE TABLE attempts(" \
                    "ATTEMPT_ID INTEGER PRIMARY KEY AUTOINCREMENT," \
                    "USER_ID INTEGER NOT NULL," \
                    "DEPTH INTEGER, " \
                    "GAMES_AMOUNT INTEGER, " \
                    "GENERATION INTEGER," \
                    "SCORE REAL," \
                    "ABORTED_IN_GAME INTEGER," \
                    "SUBMITTED_AT DATE, " \
                    "MATRIX BLOB," \
                    "GAMES_JSON TEXT)"
            DataBase.make_no_response_query(sql, database_attempts.path)
        except sqlite3.OperationalError:
            print("Table Exists")

    @staticmethod
    def get_attempts_with_username_from_querry(depth_int, games_amount, username):
        query = "SELECT attempts.ATTEMPT_ID, user.USERNAME, attempts.DEPTH, attempts.GAMES_AMOUNT, attempts.SCORE, attempts.ABORTED_IN_GAME, attempts.GENERATION FROM attempts JOIN User ON attempts.USER_ID=user.USER_ID"
        added = 0
        if depth_int:
            if not added == 0:
                query += " AND"
            query += " WHERE attempts.DEPTH = " + depth_int
            added += 1
        if games_amount:
            if not added == 0:
                query += " AND"
            query += " WHERE attempts.GAMES_AMOUNT = " + games_amount
            added += 1
        if games_amount:
            if not added == 0:
                query += " AND"
            query += " WHERE user.USERNAME = " + username
            added += 1
        return DataBase.make_multi_response_query(query + " ORDER BY attempts.SCORE DESC", database_attempts.path)

    @staticmethod
    def get_attemps_with_matrix_depth_gameAmount(matrix, depth, game_amount):

        query = "SELECT * FROM attempts WHERE DEPTH = {} AND MATRIX= '{}' AND GAMES_AMOUNT= {}"\
            .format(depth, matrix, game_amount)
        return DataBase.make_multi_response_query(query, database_attempts.path)

    @staticmethod
    def get_attemps_with_depth(depth):
        query = "SELECT * FROM attempts WHERE DEPTH = " + str(depth)
        return DataBase.make_multi_response_query(query, database_attempts.path)

    @staticmethod
    def get_attemps_with_depth_amount(depth, amount):
        query = "SELECT * FROM attempts WHERE DEPTH = {} AND GAMES_AMOUNT= {}".format(depth, amount)
        return DataBase.make_multi_response_query(query, database_attempts.path)

    @staticmethod
    def get_depths():
        query = "SELECT DEPTH, COUNT(*) FROM attempts GROUP BY DEPTH"
        return DataBase.make_multi_response_query(query, database_attempts.path)

    @staticmethod
    def get_attempts_of_user(user_id):
        query = "SELECT attempts.ATTEMPT_ID, user.USERNAME, attempts.DEPTH, attempts.GAMES_AMOUNT, attempts.SCORE, attempts.ABORTED_IN_GAME, attempts.GENERATION FROM attempts JOIN User ON attempts.USER_ID=user.USER_ID WHERE attempts.User_ID = {}".format(user_id)
        return DataBase.make_multi_response_query(query, database_attempts.path)

    @staticmethod
    def get_max_gen_from_ammount_and_depths(depth, games):
        query = "SELECT max(GENERATION) FROM attempts WHERE DEPTH={} AND GAMES_AMOUNT={}".format(depth, games)
        return DataBase.make_single_response_query(query, database_attempts.path)

    @staticmethod
    def insert_attempt(user_id, depth, games, score, aborded_in_games, matrix, games_json):
        matrix_exists = database_attempts.get_attemps_with_matrix_depth_gameAmount(matrix, depth, games)
        if not matrix_exists:
            connection = sqlite3.connect(database_attempts.path)
            cursor = connection.cursor()
            generation = database_attempts.get_max_gen_from_ammount_and_depths(depth, games)
            if generation:
                generation += 1
            else:
                generation = 1
            sql = "INSERT INTO attempts(USER_ID, DEPTH, GAMES_AMOUNT, GENERATION, SCORE, ABORTED_IN_GAME, SUBMITTED_AT, MATRIX, GAMES_JSON) " \
                  "VALUES('{}','{}','{}','{}','{}', '{}','{}', '{}','{}')"\
                .format(user_id, depth, games, generation, score, aborded_in_games, datetime.datetime.now(), matrix, games_json)
            cursor.execute(sql)
            attempt_id = cursor.lastrowid
            connection.commit()
            connection.close()
            return str(attempt_id)
        else:
            return "matrix already exist", 405

