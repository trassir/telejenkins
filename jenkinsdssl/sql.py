import psycopg2

class sql:
    _db_connection = None
    _db_cursor = None
    @staticmethod
    def init(**kwargs):
        sql._db_connection = psycopg2.connect(**kwargs)
        sql._db_cursor = sql._db_connection.cursor()
    @staticmethod
    def set(*args, **kwargs):
        sql._db_cursor.execute(*args, **kwargs)
        sql._db_connection.commit()
    @staticmethod
    def get(*args, **kwargs):
        sql._db_cursor.execute(*args, **kwargs)
        return sql._db_cursor.fetchall()
