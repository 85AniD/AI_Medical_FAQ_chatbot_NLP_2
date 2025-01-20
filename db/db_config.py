import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
load_dotenv()

def create_connection():
    """Create a database connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', 'Qaz_123'),
            database=os.getenv('DB_NAME', 'medical_faq_chatbot')
        )
        if connection.is_connected():
            print("Connection to MySQL database successful")
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise e  # Raise the exception for handling at higher levels

def close_connection(connection):
    """Close the database connection."""
    if connection.is_connected():
        connection.close()
        print("MySQL connection closed")