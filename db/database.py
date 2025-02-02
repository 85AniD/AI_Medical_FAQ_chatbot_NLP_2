import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_config import create_connection

def execute_query(query, params=None):
    """Execute a query on the MySQL database."""
    connection = create_connection()
    if not connection:
        return None
    try:
        cursor = connection.cursor()
        cursor.execute(query, params)
        connection.commit()
        print("Query executed successfully")
    except Exception as e:
        print(f"Error: '{e}'")
    finally:
        cursor.close()
        connection.close()

def fetch_query(query, params=None):
    """Fetch results from a query."""
    connection = create_connection()
    if not connection:
        return None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Error: '{e}'")
        return None
    finally:
        cursor.close()
        connection.close()
