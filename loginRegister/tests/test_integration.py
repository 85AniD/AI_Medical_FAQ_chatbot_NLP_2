#test_integration
import pytest
from ..app import app
from ..processor import chatbot_response
from ..utils import execute_query
from db.db_config import create_connection

# Test chatbot response generation
def test_chatbot_response():
    response = chatbot_response("What are the symptoms of COVID-19?")
    assert isinstance(response, str)
    assert len(response) > 0

# Test database connection and query execution
def test_database_connection():
    connection = create_connection()
    assert connection.is_connected()
    connection.close()

# Test execute_query function
def test_execute_query():
    query = "SELECT 1"
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'password',
        'database': 'test_db'
    }
    result = execute_query(query, db_config=DB_CONFIG)
    assert result == "Query executed successfully."

# Test Flask app endpoints
def test_flask_app():
    client = app.test_client()
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {"status": "ok"}