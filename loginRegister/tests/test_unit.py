#unit testing
import pytest
import numpy as np
from loginRegister.processor import clean_up_sentence, bow, predict_class, get_response, model, intents
from loginRegister.utils import hash_password, verify_password, encrypt_data, decrypt_data

# Test clean_up_sentence function
def test_clean_up_sentence():
    # Test normal sentence
    sentence = "Hello! How are you?"
    cleaned = clean_up_sentence(sentence)
    assert cleaned == ["hello", "how", "are", "you"], "Sentence cleaning failed"

    # Test empty sentence
    sentence = ""
    cleaned = clean_up_sentence(sentence)
    assert cleaned == [], "Empty sentence cleaning failed"

    # Test sentence with special characters
    sentence = "Hello! How are you? #$%^&*()"
    cleaned = clean_up_sentence(sentence)
    assert cleaned == ["hello", "how", "are", "you"], "Special characters not handled correctly"

# Test bow function
def test_bow():
    # Test normal sentence
    sentence = "hello how are you"
    words = ["hello", "how", "are", "you"]
    bag = bow(sentence, words)
    assert np.array_equal(bag, np.array([1, 1, 1, 1])), "Bag of words generation failed"

    # Test sentence with unknown words
    sentence = "hello how are you today"
    words = ["hello", "how", "are", "you"]
    bag = bow(sentence, words)
    assert np.array_equal(bag, np.array([1, 1, 1, 1])), "Unknown words not handled correctly"

# Test predict_class function
def test_predict_class():
    # Test valid sentence
    sentence = "What are the symptoms of COVID-19?"
    intents_pred = predict_class(sentence, model)
    assert isinstance(intents_pred, list), "Intent prediction should return a list"
    assert len(intents_pred) > 0, "No intents predicted for valid sentence"

    # Test invalid sentence
    sentence = "asdfghjkl"
    intents_pred = predict_class(sentence, model)
    assert isinstance(intents_pred, list), "Intent prediction should return a list"
    assert len(intents_pred) == 0, "Intents predicted for invalid sentence"

# Test get_response function
def test_get_response():
    # Test valid intent
    ints = [{"intent": "symptoms", "probability": "0.9"}]
    response = get_response(ints, intents)
    assert isinstance(response, str), "Response should be a string"
    assert len(response) > 0, "Response should not be empty"

    # Test unknown intent
    ints = [{"intent": "unknown", "probability": "0.9"}]
    response = get_response(ints, intents)
    assert response == "You must ask the right questions.", "Unknown intent not handled correctly"

# Test password hashing and verification
def test_password_hashing():
    password = "Qaz_123"
    hashed = hash_password(password)
    assert verify_password(password, hashed), "Password verification failed"

    # Test incorrect password
    assert not verify_password("wrong_password", hashed), "Incorrect password verification failed"

# Test data encryption and decryption
def test_encryption_decryption():
    data = "sensitive data"
    encrypted = encrypt_data(data)
    decrypted = decrypt_data(encrypted)
    assert decrypted == data, "Decrypted data does not match original data"

    # Test empty data
    data = ""
    encrypted = encrypt_data(data)
    decrypted = decrypt_data(encrypted)
    assert decrypted == data, "Empty data encryption/decryption failed"