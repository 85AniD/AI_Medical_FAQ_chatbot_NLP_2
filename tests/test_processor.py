import sys
import os
import unittest

# Add the root directory to sys.path to allow imports from 'loginRegister'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loginRegister.processor import predict_class, get_response


class TestProcessor(unittest.TestCase):
    def test_predict_class(self):
        message = "What are the symptoms of flu?"
        result = predict_class(message, None)
        self.assertIsInstance(result, list)

    def test_get_response(self):
        intents = [{"tag": "flu", "responses": ["Flu symptoms include fever and cough."]}]
        ints = [{"intent": "flu", "probability": "0.95"}]
        response = get_response(ints, {"intents": intents})
        self.assertIn("Flu symptoms", response)

if __name__ == "__main__":
    unittest.main()
