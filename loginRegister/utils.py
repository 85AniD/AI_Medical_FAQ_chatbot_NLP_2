import bcrypt
from Crypto.Cipher import AES
import base64
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error
from typing import Optional, Dict, List, Union
import logging

# Load environment variables from .env file
load_dotenv()

# Debug statement
print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug statement
print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")

# SECRET_KEY validation
SECRET_KEY = os.getenv('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required.")

# Decode the SECRET_KEY from base64
try:
    SECRET_KEY = base64.urlsafe_b64decode(SECRET_KEY)
except Exception as e:
    raise ValueError("Invalid SECRET_KEY: Must be a valid base64-encoded string.") from e

# Validate the length of the decoded SECRET_KEY
if len(SECRET_KEY) not in [16, 24, 32]:
    raise ValueError("SECRET_KEY must be 16, 24, or 32 bytes long when decoded.")

def hash_password(password: str) -> str:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verifies a password against a hashed password."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def encrypt_data(data: str) -> str:
    """Encrypts data using AES in EAX mode."""
    cipher = AES.new(SECRET_KEY, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
    return base64.b64encode(nonce + tag + ciphertext).decode('utf-8')

def decrypt_data(encrypted_data: str) -> str:
    """Decrypts data encrypted with AES in EAX mode."""
    try:
        encrypted_bytes = base64.b64decode(encrypted_data)
        nonce, tag, ciphertext = encrypted_bytes[:16], encrypted_bytes[16:32], encrypted_bytes[32:]
        cipher = AES.new(SECRET_KEY, AES.MODE_EAX, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag).decode('utf-8')
    except (ValueError, KeyError) as e:
        logger.error(f"Decryption failed: {e}")
        raise ValueError("Decryption failed: Invalid or tampered data.") from e

def execute_query(query: str, params: Optional[tuple] = None, db_config: Optional[Dict] = None) -> Union[str, List[Dict]]:
    """Executes a given SQL query with optional parameters."""
    if not db_config:
        raise ValueError("Database configuration is required.")

    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)  # Return results as dictionaries
            cursor.execute(query, params)
            if query.strip().upper().startswith("SELECT"):
                result = cursor.fetchall()  # Fetch results for SELECT queries
            else:
                connection.commit()
                result = "Query executed successfully."
            cursor.close()
            connection.close()
            return result
    except Error as e:
        logger.error(f"Error executing query: {e}")
        return f"Error executing query: {e}"