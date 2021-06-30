import pymysql
from app import create_connection

def fetchall(sql, vals=None):
    connection = create_connection()

    with connection.cursor() as cursor:
        query_result = None

        if vals == None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, vals)

        query_result = list(cursor.fetchall())
        return query_result
    connection.close()

def fetchone(sql, vals=None):
    connection = create_connection()

    with connection.cursor() as cursor:
        query_result = None

        if vals == None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, vals)

        query_result = cursor.fetchone()
        return query_result
    connection.close()

# Used for SQL operations that don't return anything,
# e.g INSERT, DELETE...
def nonquery(sql, vals):
    connection = create_connection()

    with connection.cursor() as cursor:
        if vals == None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, vals)
    connection.commit()
    connection.close()