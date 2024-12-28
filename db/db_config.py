import mysql.connector
from mysql.connector import Error

def create_connection():
    """Create a database connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host='localhost',  # Replace with your host
            user='root',  # Replace with your MySQL username
            password='Qaz_123',  # Replace with your MySQL password
            database='medical_faq_chatbot'  # Replace with your database name
        )
        if connection.is_connected():
            print("Connection to MySQL database successful")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None
