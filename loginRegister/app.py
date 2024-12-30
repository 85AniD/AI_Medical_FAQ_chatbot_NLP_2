import sys
import os

# Add the path to the loginRegister folder explicitly
sys.path.append(os.path.join(os.getcwd(), 'loginRegister'))
sys.path.append(os.path.join(os.getcwd(), 'db'))  # Ensure 'db' is in the path

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from processor import chatbot_response  # assuming processor.py is in the same folder
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
app.secret_key = 'enter-a-very-secretive-key-3479373'  # Required for session management and flash messages

CORS(app)  # Allow cross-origin requests for frontend integration

# Configure session to use filesystem
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# Database connection function
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # Update with your DB host
        user="root",       # Update with your DB user
        password="Qaz_123",  # Update with your DB password
        database="medical_faq_chatbot"
    )

# Decorator for checking login
# Updated loggedin decorator
def loggedin(func):
    @wraps(func)  # This preserves the original function name and avoids conflicts
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
                session['role'] = user['role']
                flash("Login successful!", "success")
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
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

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
            query = "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, email, hashed_password, role))
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

# Route: Chatbot Endpoint
@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Message is required"}), 400

    response = chatbot_response(message)  # Ensure chatbot_response() works as expected
    return jsonify({"response": response})


# Route: Admin Dashboard
@app.route('/admin/dashboard')
@loggedin
def admin_dashboard():
    if session.get('role') != 'admin':
        flash("Access denied.", "danger")
        return redirect(url_for('index'))
    return render_template('admin_dashboard.html')

'''
# Fetch users endpoint
@app.route('/users', methods=['GET'])
def get_users():
    """Fetch all registered users."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT id, username, email, created_at FROM users"
        cursor.execute(query)
        users = cursor.fetchall()  # Make sure to fetch all results
    finally:
        cursor.close()
        conn.close()
    return jsonify(users)


# Fetch FAQs endpoint
@app.route('/faqs', methods=['GET'])
def get_faqs():
    """Fetch all FAQs."""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = "SELECT id, question, answer, created_at FROM faqs"
        cursor.execute(query)
        faqs = cursor.fetchall()  # Make sure to fetch all results
    finally:
        cursor.close()
        conn.close()
    return jsonify(faqs)


# Add a new FAQ endpoint
@app.route('/faqs', methods=['POST'])
def add_faq():
    """Add a new FAQ."""
    faq = request.get_json()
    question = faq.get("question")
    answer = faq.get("answer")
    if not question or not answer:
        return jsonify({"error": "Question and answer are required"}), 400
    query = "INSERT INTO faqs (question, answer) VALUES (%s, %s)"
    execute_query(query, (question, answer))
    return jsonify({"message": "FAQ added successfully!"})
'''
# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
