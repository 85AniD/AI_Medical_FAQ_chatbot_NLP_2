import os
import sys
# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
print(sys.path)

import secrets
import bcrypt
import logging
import mysql.connector
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_session import Session
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_talisman import Talisman
from functools import wraps
from loginRegister.processor import chatbot_response
from loginRegister.utils import hash_password, encrypt_data, decrypt_data
from dotenv import load_dotenv
load_dotenv()


# Logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Flask application initialization
app = Flask(__name__)

# Secret key and session configuration
app.secret_key = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))
if not os.getenv("FLASK_SECRET_KEY"):
    logger.warning("Using a fallback FLASK_SECRET_KEY. Set a secure key in your environment!")

app.session_cookie_name = "medical_faq_session"  # Unique session cookie name
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

# JWT Configuration
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
if not os.getenv("JWT_SECRET_KEY"):
    logger.warning("Using a fallback JWT_SECRET_KEY. Set a secure key in your environment!")

# Security and session configuration
Talisman(app)
CORS(app)
Session(app)
jwt = JWTManager(app)

# Database connection function
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "Qaz_123"),
            database=os.getenv("DB_NAME", "medical_faq_chatbot"),
        )
    except mysql.connector.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

# Login decorator
def loggedin(func):
    @wraps(func)
    def secure_function(*args, **kwargs):
        if not session.get("email"):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return secure_function


# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        logger.debug(f"Login attempt for email: {email}")

        if not email or not password:
            logger.debug("Email or password missing.")
            flash("Email and password are required!", "danger")
            return render_template("login.html")

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 'user' AS role, username, email, password FROM users WHERE email = %s
                UNION
                SELECT 'admin' AS role, username, email, password FROM admins WHERE email = %s
            """
            cursor.execute(query, (email, email))
            user = cursor.fetchone()
            logger.debug(f"User fetched: {user}")

            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                session.clear()
                session.update({
                    "email": user["email"],
                    "role": user["role"],
                    "username": user["username"],
                })
                flash("Login successful!", "success")
                return redirect(url_for("admin_dashboard" if user["role"] == "admin" else "index"))

            logger.debug("Invalid credentials.")
            flash("Invalid email or password!", "danger")
        except mysql.connector.Error as e:
            logger.error(f"Database error: {e}")
            flash("An error occurred. Please try again.", "danger")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("login.html")


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()  # Clear all session data
    flash("Logged out successfully!", "success")
    return redirect(url_for("login"))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        role = request.form.get('role', 'user')  # Default role is 'user'

        # Validate input
        if not name or not email or not password or not confirm_password:
            flash("All fields are required!", "danger")
            return render_template("register.html")

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return render_template("register.html")

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            # Database connection
            conn = get_db_connection()
            cursor = conn.cursor()

            # Choose the table based on role
            table_name = 'admins' if role.lower() == 'admin' else 'users'

            # Prepare and execute the query
            query = f"INSERT INTO {table_name} (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(query, (name, email, hashed_password))
            conn.commit()

            flash("Registration successful!", "success")
            return redirect(url_for("login"))

        except mysql.connector.Error as e:
            logger.error(f"Database error during registration: {e}")
            flash("Internal server error!", "danger")

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    return render_template("register.html")


@app.route('/admin/dashboard')
@loggedin
def admin_dashboard():
    logger.debug(f"Accessing admin_dashboard. Session: {dict(session)}")
    if session.get('role') != 'admin':
        flash("Access denied! Only admins can access this page.", "danger")
        return redirect(url_for("login"))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email FROM users")
        users = cursor.fetchall()
        logger.debug(f"Fetched users: {users}")
    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        users = []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    return render_template("admin_dashboard.html", users=users)


@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    message = data.get("message", "")
    logger.debug(f"Received message: {message}")

    if not message:
        return jsonify({"error": "Message is required"}), 400

    try:
        response = chatbot_response(message)
        logger.debug(f"Chatbot response: {response}")
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"Error generating chatbot response: {e}")
        return jsonify({"error": "Failed to process the message."}), 500


@app.route('/')
@loggedin
def index():
    logger.debug(f"Accessing index. Session: {dict(session)}")
    if session.get('role') != 'user':
        flash("Access denied! Admins cannot access the user dashboard.", "danger")
        return redirect(url_for("login"))
    return render_template("index.html")


@app.route('/debug_session')
def debug_session():
    return jsonify(dict(session))


# Run the application
if __name__ == '__main__':
    try:
        app.run(debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Error running the Flask app: {e}")
