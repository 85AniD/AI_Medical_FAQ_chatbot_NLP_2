import sys
import os

# Add the 'loginRegister' and 'db' folders to sys.path for module imports
sys.path.append(os.path.join(os.getcwd(), 'loginRegister'))
sys.path.append(os.path.join(os.getcwd(), 'db'))

from flask import Flask, request, jsonify
from processor import chatbot_response, register
from db.database import fetch_query, execute_query

# Initialize Flask app
app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return "Welcome to the AI Medical FAQ Chatbot API!"

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
@app.route('/register', methods=['POST'])
def user_register():
    """Registers a new user."""
    userinfo = request.get_json()
    required_fields = ["username", "email", "password"]
    missing_fields = [field for field in required_fields if field not in userinfo]
    if missing_fields:
        return jsonify({"error": f"Missing fields: {', '.join(missing_fields)}"}), 400
    response = register(userinfo)
    return jsonify({"message": response})

# Fetch users endpoint
@app.route('/users', methods=['GET'])
def get_users():
    """Fetch all registered users."""
    try:
        query = "SELECT id, username, email, created_at FROM users"
        users = fetch_query(query)
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Fetch FAQs endpoint
@app.route('/faqs', methods=['GET'])
def get_faqs():
    """Fetch all FAQs."""
    try:
        query = "SELECT id, question, answer, created_at FROM faqs"
        faqs = fetch_query(query)
        return jsonify(faqs)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add a new FAQ endpoint
@app.route('/faqs', methods=['POST'])
def add_faq():
    """Add a new FAQ."""
    faq = request.get_json()
    question = faq.get("question")
    answer = faq.get("answer")
    if not question or not answer:
        return jsonify({"error": "Question and answer are required"}), 400
    try:
        query = "INSERT INTO faqs (question, answer) VALUES (%s, %s)"
        execute_query(query, (question, answer))
        return jsonify({"message": "FAQ added successfully!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
