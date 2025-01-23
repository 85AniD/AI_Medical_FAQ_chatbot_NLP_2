import os
import mysql.connector
from mysql.connector import Error, pooling
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    "host": os.getenv('DB_HOST', 'localhost'),
    "user": os.getenv('DB_USER', 'root'),
    "password": os.getenv('DB_PASSWORD', 'Qaz_123'),
    "database": os.getenv('DB_NAME', 'medical_faq_chatbot')
}

# Connection pool
db_pool = pooling.MySQLConnectionPool(
    pool_name="db_pool",
    pool_size=5,  # Adjust based on your application's needs
    **DB_CONFIG
)

def create_connection():
    """Create a database connection to the MySQL database."""
    try:
        connection = db_pool.get_connection()
        if connection.is_connected():
            logger.info("Connection to MySQL database successful")
        return connection
    except Error as e:
        logger.error(f"Error connecting to MySQL: {e}")
        raise e  # Raise the exception for handling at higher levels

def close_connection(connection):
    """Close the database connection."""
    if connection.is_connected():
        connection.close()
        logger.info("MySQL connection closed")

def is_connection_active(connection):
    """Check if the database connection is still active."""
    try:
        if connection.is_connected():
            return True
        return False
    except Error as e:
        logger.error(f"Error checking connection status: {e}")
        return False