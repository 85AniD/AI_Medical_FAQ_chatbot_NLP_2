import sys
import os

# Add the path to the loginRegister folder explicitly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from loginRegister.processor import chatbot_response  # Adjusted import
from db.database import execute_query  # Adjusted import

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
app.secret_key = 'enter-a-very-secretive-key-3479373'  # Required for session management and flash messages

CORS(app)  # Allow cross-origin requests for frontend integration

# Configure session to use filesystem
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
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

        # Check if both email and password are provided
        if not email or not password:
            flash("Email and password are required!", "danger")
            return redirect(url_for('login'))

        try:
            # Establish database connection
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # Query to fetch user or admin based on email
            query = """
                SELECT * FROM users WHERE role = 'user' AND email = %s
                UNION
                SELECT * FROM admins WHERE role = 'admin' AND email = %s
            """
            cursor.execute(query, (email, email))

            # Fetch the user record
            user = cursor.fetchone()

            # Check if user exists and validate password
            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                session['email'] = email
                session['role'] = user['role']  # Set the role from the database

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

# Route: Logout
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()  # Clear session data
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))  # Redirect to login page


# Route: Index (Home Page After Login)
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
@app.route('/admin/dashboard', methods=['GET'])
@loggedin
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('index'))

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, username, email FROM users"
        cursor.execute(query)
        users = cursor.fetchall()
        print(users)  # Debug: Check if user data is fetched
    except mysql.connector.Error as e:
        logger.error(f"Database error while fetching users: {e}")
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

    response = chatbot_response(message)  # Ensure chatbot_response() works as expected
    return jsonify({"response": response})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)