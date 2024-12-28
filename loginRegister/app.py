from flask import Flask, request, jsonify
from loginRegister.processor import chatbot_response, register
from db.database import fetch_query, execute_query

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the AI Medical FAQ Chatbot API!"

@app.route('/chatbot', methods=['POST'])
def chatbot():
    """Handles chatbot messages."""
    data = request.get_json()
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Message is required"}), 400
    response = chatbot_response(message)
    return jsonify({"response": response})

@app.route('/register', methods=['POST'])
def user_register():
    """Registers a new user."""
    userinfo = request.get_json()
    required_fields = ["username", "email", "password"]
    for field in required_fields:
        if field not in userinfo:
            return jsonify({"error": f"{field} is required"}), 400
    response = register(userinfo)
    return jsonify({"message": response})

@app.route('/users', methods=['GET'])
def get_users():
    """Fetch all registered users."""
    query = "SELECT id, username, email, created_at FROM users"
    users = fetch_query(query)
    return jsonify(users)

@app.route('/faqs', methods=['GET'])
def get_faqs():
    """Fetch all FAQs."""
    query = "SELECT id, question, answer, created_at FROM faqs"
    faqs = fetch_query(query)
    return jsonify(faqs)

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

if __name__ == '__main__':
    app.run(debug=True)
