import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import bcrypt
import logging
import mysql.connector
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_session import Session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from flask_talisman import Talisman
from functools import wraps
from loginRegister.processor import chatbot_response
from loginRegister.utils import hash_password, encrypt_data, decrypt_data


# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Replace with a secure key in production
app.session_cookie_name = 'session_cookie_name'

# Security and CORS settings
Talisman(app)
CORS(app)

# Session and JWT configurations
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "YourJWTSecretKey")  # Secure key for JWT
Session(app)
jwt = JWTManager(app)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD", "Qaz_123"),  # Use environment variables for sensitive info
        database="medical_faq_chatbot"
    )

# Decorator for login check
def loggedin(func):
    @wraps(func)
    def secure_function(*args, **kwargs):
        # Log session details
        logger.debug(f"Session email: {session.get('email')}, role: {session.get('role')}")

        if not session.get("email"):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return secure_function


# Routes

# Login page route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        logger.debug(f"Attempting login for email: {email}")

        if not email or not password:
            flash("Email and password are required!", "danger")
            return redirect(url_for('login'))

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT * FROM users WHERE role = 'user' AND email = %s
                UNION
                SELECT * FROM admins WHERE role = 'admin' AND email = %s
            """
            cursor.execute(query, (email, email))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                session['email'] = email
                session['role'] = user['role']  # Set the role from the database
                logger.debug(f"Session set: email={session.get('email')}, role={session.get('role')}")
                
                flash("Login successful!", "success")

                # Redirect based on user role
                if user['role'] == 'admin':
                    return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
                return redirect(url_for('index'))  # Redirect to user home page


            flash("Invalid email or password!", "danger")

        except mysql.connector.Error as e:
            logger.error(f"Database error during login: {e}")
            flash("An error occurred. Please try again.", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')


# Logout route
@app.route('/logout', methods=['GET'])
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(url_for('login'))

# Register page route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    data = request.form
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'user')

    if not name or not email or not password:
        flash("All fields are required!", "danger")
        return render_template('register.html')

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        if role.lower() == 'admin':
            query = "INSERT INTO admins (username, email, password) VALUES (%s, %s, %s)"
        cursor.execute(query, (name, email, hashed_password))
        conn.commit()
        flash("Registration successful!", "success")
        return redirect(url_for('login'))
    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        flash("Internal server error!", "danger")
        return render_template('register.html')
    finally:
        cursor.close()
        conn.close()

# Admin dashboard route (Requires Admin Role)
@app.route('/admin/dashboard', methods=['GET'])
@loggedin
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Access denied!", "danger")
        return redirect(url_for('index'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, username, email FROM users")
        users = cursor.fetchall()
    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        flash("An error occurred!", "danger")
        users = []
    finally:
        cursor.close()
        conn.close()

    return render_template('admin_dashboard.html', users=users)

# Chatbot route
@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Message is required"}), 400

    response = chatbot_response(message)  # Ensure chatbot_response() works as expected
    return jsonify({"response": response})

# Main page route
@app.route('/', methods=['GET', 'POST'])
@loggedin
def index():
    logger.debug(f"Accessing index: session email={session.get('email')}, role={session.get('role')}")
    return render_template('index.html')


# Run the Flask app
if __name__ == '__main__':
    try:
        app.run(debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Error running the Flask app: {e}")
