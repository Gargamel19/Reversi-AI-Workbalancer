import sqlite3


class DataBase:
    base_path = "."

    @staticmethod
    def make_no_response_query(sql, database_url):
        connection = sqlite3.connect(database_url)
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()
        connection.close()

    @staticmethod
    def make_single_response_query(query, database_url):

        connection = sqlite3.connect(database_url)
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            msg = cursor.fetchone()
            if msg is not None:
                user_hash = msg[0]
                connection.close()
                return user_hash
        except sqlite3.OperationalError:
            print("Invalid query: " + query)
            return None
        return None

    @staticmethod
    def make_multi_response_query(query, database_url):

        connection = sqlite3.connect(database_url)
        cursor = connection.cursor()
        try:
            cursor.execute(query)
            msg = cursor.fetchall()
            connection.close()
            return msg
        except sqlite3.OperationalError:
            print("Invalid query: " + query)
            return None
        return None
