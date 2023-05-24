from collections import namedtuple
import psycopg2
from psycopg2 import Error
from psycopg2.extras import RealDictCursor

try:

    connection = psycopg2.connect(
        user='postgres',
        password='VqhDHXgGPL8avdUHqCWP',
        host='containers-us-west-72.railway.app',
        databases='railway',
        port='7729',
    )

    # Create a cursor to perform database operations
    connection.autocommit = True
    cursor = connection.cursor()

        # Print PostgreSQL details
    print("PostgreSQL server information")
    print(connection.get_dsn_parameters(), "\n")

    # Executing a SQL query
    cursor.execute("SELECT version();")

    # Fetch result
    record = cursor.fetchone()
    print("You are connected to - ", record, "\n")

    cursor.execute("SET search_path TO PUBLIC;")

except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)


def map_cursor(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple("Result", [col[0] for col in desc])
    return [dict(row) for row in cursor.fetchall()]


def query(query_str: str):
    hasil = []
    with connection.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SET SEARCH_PATH TO PUBLIC;")
        try:
            cursor.execute(query_str)

            if query_str.strip().upper().startswith("SELECT"):
                # Kalau ga error, return hasil SELECT
                hasil = map_cursor(cursor)
            else:
                # Kalau ga error, return jumlah row yang termodifikasi oleh INSERT, UPDATE, DELETE
                hasil = cursor.rowcount
                connection.commit()
        except Exception as e:
            # Ga tau error apa
            hasil = e

    return hasil

def exec(query):
    query = query.strip()
    if not (query.endswith(";")):
        query += ";"
    cursor.execute(query)
    if (query.upper().startswith("SELECT")):
        return cursor.fetchall()
    elif (query.upper().startswith("INSERT")) or (query.upper().startswith("UPDATE")) or (query.upper().startswith("CREATE")):
        connection.commit()

def try_exec(query):
    try:
        return False, exec(query)
    except (Exception, Error) as error:
        connection.rollback()
        cursor.execute("SET SEARCH_PATH TO PUBLIC;")
        return True, error
	