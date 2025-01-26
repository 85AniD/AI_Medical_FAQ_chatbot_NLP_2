import os
import sys
# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import secrets
import bcrypt
import logging
import nltk
import mysql.connector
from mysql.connector import pooling

from flask import Flask, session, request, g, jsonify, render_template, redirect, url_for, flash
from flask_session import Session
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from flask_cors import CORS
from flask_talisman import Talisman
from functools import wraps
from dotenv import load_dotenv
from datetime import datetime, timedelta

from loginRegister.processor import chatbot_response
from loginRegister.utils import hash_password

# Load environment variables
load_dotenv()
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
nltk.download('punkt')

# Logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Flask configuration
class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", secrets.token_hex(32))  # Fallback to a random key if not set
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))  # Fallback to a random key if not set
    SESSION_PERMANENT = False
    SESSION_TYPE = "filesystem"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    SESSION_COOKIE_NAME = 'medical_faq_session'  # Ensure this is set
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "Qaz_123")
    DB_NAME = os.getenv("DB_NAME", "medical_faq_chatbot")

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Debugging: Log session configuration
logger.debug(f"Session Cookie Name: {app.config['SESSION_COOKIE_NAME']}")
logger.debug(f"Session Type: {app.config['SESSION_TYPE']}")
logger.debug(f"Session Permanent: {app.config['SESSION_PERMANENT']}")

# Initialize Flask-Session
Session(app)

# Initialize Talisman and CORS
Talisman(app)
CORS(app)

# Initialize JWTManager
jwt_manager = JWTManager(app)

# Database connection pool
db_pool = pooling.MySQLConnectionPool(
    pool_name="db_pool",
    pool_size=5,
    host=app.config["DB_HOST"],
    user=app.config["DB_USER"],
    password=app.config["DB_PASSWORD"],
    database=app.config["DB_NAME"],
)

def get_db_connection():
    """Get a connection from the database pool."""
    return db_pool.get_connection()

# Decorator for logged-in user
def loggedin(func):
    @wraps(func)
    def secure_function(*args, **kwargs):
        if not session.get("email"):
            flash("Please log in to access this page.", "warning")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return secure_function

@app.before_request
def generate_nonce():
    """Generate a nonce for Content Security Policy (CSP)."""
    g.nonce = secrets.token_hex(16)
    logger.debug(f"Generated nonce: {g.nonce}")

@app.after_request
def set_csp(response):
    """Set Content Security Policy (CSP) headers."""
    nonce = g.get('nonce', '')
    csp_policy = (
        f"default-src 'self'; "
        f"script-src 'self' 'nonce-{nonce}'; "  # Allow local scripts
        f"style-src 'self' 'nonce-{nonce}'; "
        f"connect-src 'self';"  # Allow AJAX requests to the same origin
    )
    response.headers['Content-Security-Policy'] = csp_policy
    logger.info(f"Generated CSP Policy: {csp_policy}")
    return response

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm-password')
        role = request.form.get('role', 'user').strip().lower()

        if not name or not email or not password or not confirm_password:
            flash("All fields are required!", "danger")
            return render_template("register.html", nonce=g.nonce)

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return render_template("register.html", nonce=g.nonce)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            table_name = 'admins' if role == 'admin' else 'users'
            query = f"INSERT INTO {table_name} (username, email, password) VALUES (%s, %s, %s)"

            cursor.execute(query, (name, email, hashed_password))
            conn.commit()
            flash("Registration successful!", "success")
            return redirect(url_for("login"))
        except mysql.connector.Error as e:
            logger.error(f"Database error during registration: {e}")
            flash("An error occurred during registration. Please try again.", "danger")
            return render_template("register.html", nonce=g.nonce)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    else:
        return render_template("register.html", nonce=g.nonce)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        if not data:
            return jsonify({"error": "Invalid request data"}), 400

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required!"}), 400

        logger.info(f"Login attempt for email: {email}")

        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({"error": "Database connection failed"}), 500
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT 'user' AS role, username, email, password FROM users WHERE email = %s
                UNION
                SELECT 'admin' AS role, username, email, password FROM admins WHERE email = %s
            """
            cursor.execute(query, (email, email))
            user = cursor.fetchone()

            if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
                session.clear()
                session.permanent = True
                session['email'] = user['email']
                session['role'] = user['role']
                session['username'] = user['username']

                logger.info(f"Login successful for user: {user['email']}, role: {user['role']}")

                access_token = create_access_token(
                    identity={"username": user["username"], "role": user["role"]},
                    expires_delta=timedelta(hours=1)
                )
                return jsonify({
                    "access_token": access_token,
                    "username": user["username"],
                    "role": user["role"]
                }), 200

            logger.warning(f"Invalid login attempt for email: {email}")
            return jsonify({"error": "Invalid email or password!"}), 401

        except mysql.connector.Error as e:
            logger.error(f"Database error during login: {e}")
            return jsonify({"error": "An error occurred. Please try again later."}), 500

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

    else:
        return render_template("login.html", nonce=g.nonce)

@app.route('/index', methods=["GET"])
@loggedin
def index():
    """Render the user dashboard."""
    if session.get('role') != 'user':
        flash("Access denied! Admins cannot access the user dashboard.", "danger")
        return redirect(url_for("login"))
    logger.info(f"User dashboard accessed by {session.get('email')}")
    return render_template("index.html", username=session.get("username"), nonce=g.nonce)

@app.route('/admin/dashboard', methods=["GET"])
@loggedin
def admin_dashboard():
    """Render the admin dashboard."""
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
    return render_template("admin_dashboard.html", users=users, nonce=g.nonce)

@app.route('/chatbot', methods=['POST'])
@jwt_required()  # Protect the endpoint with JWT authentication
def chatbot():
    logger.info(request.get_json())  # Log the incoming request data
    try:
        if not request.is_json:
            logger.error("Request must be in JSON format.")
            return jsonify({"error": "Request must be in JSON format."}), 400

        data = request.get_json()
        logger.info(f"Received data: {data}")  # Log the incoming data

        # Check if 'question' field exists and is a non-empty string
        user_query = data.get("question", "").strip()
        if not user_query:
            logger.error("Invalid or empty 'question' field.")
            return jsonify({"error": "The 'question' field must be a non-empty string."}), 422

        logger.info(f"Received valid question from user: {user_query}")

        # Generate a response using the chatbot model
        response = chatbot_response(user_query)

        logger.info(f"Chatbot response generated: {response}")

        return jsonify({"response": response}), 200

    except Exception as e:
        logger.error(f"Unexpected error in chatbot endpoint: {e}", exc_info=True)
        return jsonify({"error": "An internal server error occurred. Please try again later."}), 500
            
@app.route('/logout', methods=['POST'])  # Restrict to POST for security
def logout():
    """Handle user logout."""
    user_email = session.get('email')
    if user_email:
        logger.info(f"User logged out: {user_email}")
    else:
        logger.info("An anonymous user attempted to log out.")

    session.clear()  # Clear the session data
    flash("Logged out successfully!", "success")

    # If using JWT tokens, you might want to clear the token on the client side
    # This would require additional client-side logic (e.g., in JavaScript)

    return redirect(url_for("login"))  # Redirect to the login page

@app.route('/')
def root():
    """Redirect to the appropriate dashboard based on user role."""
    if session.get("role") == "user":
        return redirect(url_for("index"))
    elif session.get("role") == "admin":
        return redirect(url_for("admin_dashboard"))
    return redirect(url_for("login"))

@app.route('/admin/modify_user/<int:user_id>', methods=['POST'])
@loggedin
def modify_user(user_id):
    """Modify user details (admin only)."""
    if session.get('role') != 'admin':
        logger.warning(f"Unauthorized access attempt by user {session.get('username')}")
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        data = request.get_json()
        if not data:
            logger.error("No data provided in modify_user request")
            return jsonify({"error": "No data provided"}), 400

        new_username = data.get("username")
        new_email = data.get("email")

        if not new_username or not new_email:
            logger.error("Username or email missing in modify_user request")
            return jsonify({"error": "Username and email are required"}), 400

        logger.info(f"Modifying user {user_id} with username: {new_username}, email: {new_email}")

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    UPDATE users
                    SET username = %s, email = %s
                    WHERE id = %s
                """
                cursor.execute(query, (new_username, new_email, user_id))
                conn.commit()

        return jsonify({"message": "User updated successfully"}), 200
    except mysql.connector.Error as e:
        logger.error(f"Database error while modifying user {user_id}: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Unexpected error while modifying user {user_id}: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/admin/delete_user/<int:user_id>', methods=['DELETE'])
@loggedin
def delete_user(user_id):
    """Delete a user (admin only)."""
    if session.get('role') != 'admin':
        logger.warning(f"Unauthorized access attempt by user {session.get('username')}")
        return jsonify({"error": "Unauthorized access"}), 403

    try:
        logger.info(f"Deleting user {user_id}")

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                query = "DELETE FROM users WHERE id = %s"
                cursor.execute(query, (user_id,))
                conn.commit()

        return jsonify({"message": "User deleted successfully"}), 200
    except mysql.connector.Error as e:
        logger.error(f"Database error while deleting user {user_id}: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Unexpected error while deleting user {user_id}: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('404.html', nonce=g.nonce), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return render_template('500.html', nonce=g.nonce), 500

@app.route('/simulate-500')
def simulate_500():
    """Simulate a 500 error for testing."""
    raise Exception("This is a simulated 500 error.")

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)