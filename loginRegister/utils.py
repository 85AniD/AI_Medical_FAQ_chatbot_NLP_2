import bcrypt
from Crypto.Cipher import AES
import base64
import os
import mysql.connector
from mysql.connector import Error


SECRET_KEY = os.getenv('SECRET_KEY', b'some_16_byte_key')
if len(SECRET_KEY) not in [16, 24, 32]:
    raise ValueError("SECRET_KEY must be 16, 24, or 32 bytes long.")

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def encrypt_data(data: str) -> str:
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
    return base64.b64encode(nonce + tag + ciphertext).decode('utf-8')

def decrypt_data(encrypted_data: str) -> str:
    encrypted_bytes = base64.b64decode(encrypted_data)
    nonce, tag, ciphertext = encrypted_bytes[:16], encrypted_bytes[16:32], encrypted_bytes[32:]
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')


def execute_query(query, params=None):
    """Executes a given SQL query with optional parameters."""
    try:
        # Connect to the database (ensure db_config.py has the correct credentials)
        from db.db_config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

        connection = mysql.connector.connect(
            host='localhost',  # Replace with your host
            user='root',  # Replace with your MySQL username
            password='Qaz_123',  # Replace with your MySQL password
            database='medical_faq_chatbot'  # Replace with your database name
        )
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute(query, params)
            connection.commit()
            cursor.close()
            connection.close()
            return "Query executed successfully."

    except Error as e:
        return f"Error executing query: {e}"
