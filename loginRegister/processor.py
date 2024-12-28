import os
import sys
import json
import random
import pickle
import nltk
from keras.models import load_model
import numpy as np
from nltk.stem import WordNetLemmatizer

# Ensure that NLTK punkt data is downloaded
nltk.download('punkt')

# Set up paths to your data folder
data_folder = os.path.join(os.getcwd(), 'loginRegister', 'data')

# Check if data folder exists
if not os.path.exists(data_folder):
    raise FileNotFoundError(f"Data folder not found: {data_folder}")

# File paths
intents_file = os.path.join(data_folder, 'intents.json')
words_file = os.path.join(data_folder, 'words.pkl')
classes_file = os.path.join(data_folder, 'classes.pkl')
model_file = os.path.join(data_folder, 'chatbot_model.h5')

# Load the files
try:
    with open(intents_file, encoding='utf-8') as f:
        intents = json.load(f)
except FileNotFoundError:
    print(f"Error loading intents file: {intents_file}")
    raise

try:
    words = pickle.load(open(words_file, 'rb'))
    classes = pickle.load(open(classes_file, 'rb'))
    model = load_model(model_file)
except FileNotFoundError as e:
    print(f"Error loading one or more files: {e}")
    raise

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Function to clean up the sentence (tokenize and lemmatize)
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    return [lemmatizer.lemmatize(word.lower()) for word in sentence_words]

# Convert sentence to bag of words
def bow(sentence, words, show_details=False):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    print(f"Found in bag: {w}")
    return np.array(bag)

# Predict the class of the sentence
def predict_class(sentence, model):
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return [{"intent": classes[r[0]], "probability": str(r[1])} for r in results]

# Get response based on predicted class
def get_response(ints, intents_json):
    if not ints:
        return "Sorry, I don't understand that."
    tag = ints[0]['intent']
    for i in intents_json['intents']:
        if i['tag'] == tag:
            return random.choice(i['responses'])
    return "You must ask the right questions."

# Main function to generate chatbot response
def chatbot_response(msg):
    ints = predict_class(msg, model)
    return get_response(ints, intents)

# Register a user in the database
def register(userinfo):
    query = """
    INSERT INTO users (username, email, password)
    VALUES (%s, %s, %s)
    """
    execute_query(query, (userinfo['username'], userinfo['email'], userinfo['password']))
    return "User registered successfully."
