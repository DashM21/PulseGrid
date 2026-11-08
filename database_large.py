
import mysql.connector
import config


def get_connection():
    """Connect to the PULSEGRID large database."""
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database="pulsegrid_large_db",
            connection_timeout=5,
            use_pure=True
        )
        return conn

    except mysql.connector.Error as err:
        print(f"Large Database Error: {err}", flush=True)
        return None


def execute_query(query, params=None):
    """Execute INSERT, UPDATE or DELETE queries."""
    conn = get_connection()

    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(query, params or ())
        conn.commit()
        return True

    except mysql.connector.Error as err:
        print(f"Execution Error: {err}")
        return False

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def fetch_data(query, params=None):
    """Fetch records from the large database."""
    conn = get_connection()

    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        return result

    except mysql.connector.Error as err:
        print(f"Fetch Error: {err}")
        return []

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
