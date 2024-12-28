import nltk
from nltk.stem import WordNetLemmatizer
import pickle
import numpy as np
from tensorflow.keras.models import load_model
from database import execute_query
import json
import random
import os

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, '../data/intents.json')
WORDS_PATH = os.path.join(BASE_DIR, '../data/words.pkl')
CLASSES_PATH = os.path.join(BASE_DIR, '../data/classes.pkl')
MODEL_PATH = os.path.join(BASE_DIR, '../data/chatbot_model.h5')


# Load required files
with open(DATA_PATH, encoding='utf-8') as file:
    intents = json.load(file)

words = pickle.load(open(WORDS_PATH, 'rb'))
classes = pickle.load(open(CLASSES_PATH, 'rb'))
model = load_model(MODEL_PATH)


def clean_up_sentence(sentence):
    """
    Tokenizes and lemmatizes the input sentence, removing non-alphanumeric characters.
    """
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words if word.isalnum()]
    return sentence_words


def bow(sentence, words, show_details=True):
    """
    Converts a sentence into a bag-of-words representation using the provided word list.
    """
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print(f"Found in bag: {w}")
    return np.array(bag)


def predict_class(sentence, model):
    """
    Predicts the intent of the given sentence using the trained model.
    """
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    if not results:
        return []
    results.sort(key=lambda x: x[1], reverse=True)
    return [{"intent": classes[r[0]], "probability": str(r[1])} for r in results]


def get_response(ints, intents_json):
    """
    Fetches the response corresponding to the predicted intent.
    """
    if not ints:
        return "Sorry, I don't understand that."
    tag = ints[0]['intent']
    for i in intents_json['intents']:
        if i['tag'] == tag:
            return random.choice(i['responses'])
    return "You must ask the right questions."


def chatbot_response(msg):
    """
    Generates a chatbot response for the given message.
    """
    ints = predict_class(msg, model)
    res = get_response(ints, intents)
    return res


def register(userinfo):
    query = """
    INSERT INTO users (username, email, password)
    VALUES (%s, %s, %s)
    """
    params = (userinfo['username'], userinfo['email'], userinfo['password'])
    execute_query(query, params)
    return "User registered successfully."
