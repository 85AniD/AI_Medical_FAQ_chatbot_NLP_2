import sys
import os

# Add the path to the loginRegister folder explicitly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from loginRegister.processor import chatbot_response
from db.database import execute_query

from flask_session import Session
from loginRegister.utils import hash_password
from functools import wraps
import mysql.connector
from flask_cors import CORS
import bcrypt
import logging

# Set up logging for Flask
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'enter-a-very-secretive-key-3479373'

CORS(app)

# Configure session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['TEMPLATES_AUTO_RELOAD'] = True

Session(app)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Qaz_123",
        database="medical_faq_chatbot"
    )

# Decorator for checking login
def loggedin(func):
    @wraps(func)
    def secure_function(*args, **kwargs):
        logger.debug(f"Session data: {session}")
        if not session.get("email"):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return secure_function

# Route: Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Email and password are required!", "danger")
            return redirect(url_for('login'))

        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                session['email'] = email
                session['role'] = user['role']  # This should match the role column in your database
                flash("Login successful!", "success")
                logger.debug(f"Session after login: {session}")
                if user['role'].lower() == 'admin':  # Ensure case consistency
                    return redirect(url_for('admin_dashboard'))
                return redirect(url_for('index'))


            flash("Invalid email or password!", "danger")

        except mysql.connector.Error as e:
            logger.error(f"Database error during login: {e}")
            flash("An error occurred. Please try again.", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template('login.html')

# Route: Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

# Route: Index
@app.route('/', methods=['GET', 'POST'])
@loggedin
def index():
    return render_template('index.html')

# Route: Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')

        if not name or not email or not password:
            flash("All fields are required!", "danger")
            return redirect(url_for('register'))

        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            conn = get_db_connection()
            cursor = conn.cursor()

            if role.lower() == 'admin':
                query = "INSERT INTO admins (username, email, password) VALUES (%s, %s, %s)"
            else:
                query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"

            cursor.execute(query, (name, email, hashed_password))
            conn.commit()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for('login'))

        except mysql.connector.Error as e:
            logger.error(f"Database error during registration: {e}")
            flash("An error occurred. Please try again.", "danger")

        finally:
            cursor.close()
            conn.close()

    return render_template('register.html')

# Route: Admin Dashboard
@app.route('/admin_dashboard', methods=['GET'])
@loggedin
def admin_dashboard():
    session['email'] = 'admin@example.com'  # Simulate a logged-in admin
    session['role'] = 'admin'  # Simulate admin role
    logger.debug(f"Session during admin_dashboard: {session}")

    if session.get('role', '').lower() != 'admin':
        flash("Access denied. Admins only.", "danger")
        return redirect(url_for('index'))

    # Fetch user data
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, username, email FROM users"
        cursor.execute(query)
        users = cursor.fetchall()
        logger.debug(f"Fetched users: {users}")
    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        flash("An error occurred while fetching user data.", "danger")
        users = []
    finally:
        cursor.close()
        conn.close()

    return render_template('admin_dashboard.html', users=users)

# Route: Chatbot Endpoint
@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Message is required"}), 400

    response = chatbot_response(message)
    return jsonify({"response": response})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
