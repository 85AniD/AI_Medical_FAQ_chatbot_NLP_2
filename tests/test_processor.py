import sys
import os
import unittest
import numpy as np
from unittest.mock import MagicMock
from keras.models import Sequential
from keras.layers import Dense

# Add the root directory to sys.path to allow imports from 'loginRegister'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from loginRegister.processor import predict_class, get_response

class TestProcessor(unittest.TestCase):
    def setUp(self):
        # Mock model setup for testing
        self.mock_model = Sequential()
        self.mock_model.add(Dense(10, input_shape=(5,), activation='relu'))  # Dummy structure
        self.mock_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
        self.mock_model.predict = MagicMock(return_value=np.array([[0.1, 0.7, 0.2]]))  # Mock prediction output

    def test_predict_class(self):
        message = "What are the symptoms of flu?"
        result = predict_class(message, self.mock_model)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0, "The prediction result should not be empty.")
        self.assertIn("intent", result[0], "The prediction result should include an 'intent' key.")

    def test_get_response(self):
        intents = [{"tag": "flu", "responses": ["Flu symptoms include fever and cough."]}]
        ints = [{"intent": "flu", "probability": "0.95"}]
        response = get_response(ints, {"intents": intents})
        self.assertIn("Flu symptoms", response, "The response should contain a flu-related message.")

if __name__ == "__main__":
    unittest.main(argv=[''], exit=False)
