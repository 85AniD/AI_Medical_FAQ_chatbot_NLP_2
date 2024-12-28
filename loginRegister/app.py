import sys
import os

# Add the path to the loginRegister folder explicitly
sys.path.append(os.path.join(os.getcwd(), 'loginRegister'))
sys.path.append(os.path.join(os.getcwd(), 'db'))

from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from processor import chatbot_response, register  # assuming processor.py is in the same folder as app.py
from db.database import fetch_query, execute_query

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management and flash messages

# Home route
@app.route('/')
def home():
    return render_template('login.html')

# Chatbot endpoint
@app.route('/chatbot', methods=['POST'])
def chatbot():
    """Handles chatbot messages."""
    data = request.get_json()
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Message is required"}), 400
    response = chatbot_response(message)
    return jsonify({"response": response})

# User registration endpoint
@app.route('/register', methods=['GET', 'POST'])
def user_register():
    """Registers a new user."""
    if request.method == 'POST':
        userinfo = request.form
        required_fields = ["username", "email", "password"]
        missing_fields = [field for field in required_fields if field not in userinfo]
        if missing_fields:
            flash(f"Missing fields: {', '.join(missing_fields)}", 'error')
            return redirect(url_for('user_register'))
        response = register(userinfo)
        flash(response, 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login for users."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Here you should add authentication logic
        if username == "admin" and password == "admin":  # Replace with actual authentication
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials, please try again.', 'error')
            return redirect(url_for('login'))
    
    return render_template('login.html')

# Admin dashboard
@app.route('/admin/dashboard')
def admin_dashboard():
    """Admin dashboard route."""
    return render_template('admin_dashboard.html')

# Fetch users endpoint
@app.route('/users', methods=['GET'])
def get_users():
    """Fetch all registered users."""
    query = "SELECT id, username, email, created_at FROM users"
    users = fetch_query(query)
    return jsonify(users)

# Fetch FAQs endpoint
@app.route('/faqs', methods=['GET'])
def get_faqs():
    """Fetch all FAQs."""
    query = "SELECT id, question, answer, created_at FROM faqs"
    faqs = fetch_query(query)
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

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
