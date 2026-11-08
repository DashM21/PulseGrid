import mysql.connector
import config


def get_connection():
    """Establishes a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME,
            connection_timeout=5,
            use_pure=True
        )
        return conn

    except mysql.connector.Error as err:
        print(f"Database Error: {err}", flush=True)
        return None


        
        return conn
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return None

def execute_query(query, params=None):
    """Executes a modification query (INSERT, UPDATE, DELETE)."""
    conn = get_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except mysql.connector.Error as err:
        print(f"Execution Error: {err}")
        return False

def fetch_data(query, params=None):
    """Fetches records from the database (SELECT)."""
    conn = get_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result
    except mysql.connector.Error as err:
        print(f"Fetch Error: {err}")
        return []