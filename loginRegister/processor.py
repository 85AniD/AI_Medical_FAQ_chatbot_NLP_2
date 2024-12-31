import os
import json
import random
import pickle
import logging
import nltk
from keras.models import load_model
import numpy as np
from nltk.stem import WordNetLemmatizer

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ensure NLTK data is downloaded
nltk.download('punkt')

# Set up paths to your data folder dynamically
project_root = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(project_root, 'data')

# Ensure the data folder exists
if not os.path.exists(data_folder):
    os.makedirs(data_folder)
    logging.error(f"Data folder not found. Created an empty folder: {data_folder}")
    raise FileNotFoundError(f"Please add the required files to the data folder: {data_folder}")

# File paths
intents_file = os.path.join(data_folder, 'intents.json')
words_file = os.path.join(data_folder, 'words.pkl')
classes_file = os.path.join(data_folder, 'classes.pkl')
model_file = os.path.join(data_folder, 'chatbot_model.h5')

# Validate required files
missing_files = [f for f in [intents_file, words_file, classes_file, model_file] if not os.path.exists(f)]
if missing_files:
    logging.error(f"Missing files: {', '.join(missing_files)}")
    raise FileNotFoundError(f"The following required files are missing in the data folder: {', '.join(missing_files)}")

# Load data files
try:
    with open(intents_file, encoding='utf-8') as f:
        intents = json.load(f)
    words = pickle.load(open(words_file, 'rb'))
    classes = pickle.load(open(classes_file, 'rb'))
    model = load_model(model_file)
    logging.info("All files loaded successfully.")
except Exception as e:
    logging.error(f"Error loading files: {e}")
    raise

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

# Clean and tokenize a sentence
def clean_up_sentence(sentence):
    try:
        sentence_words = nltk.word_tokenize(sentence)
        return [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    except Exception as e:
        logging.error(f"Error in sentence cleaning: {e}")
        raise

# Convert sentence to bag of words
def bow(sentence, words, show_details=False):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
                if show_details:
                    logging.info(f"Found in bag: {w}")
    return np.array(bag)

# Predict the class of a sentence
def predict_class(sentence, model):
    try:
        p = bow(sentence, words)
        res = model.predict(np.array([p]))[0]
        ERROR_THRESHOLD = 0.25
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
        results.sort(key=lambda x: x[1], reverse=True)
        return [{"intent": classes[r[0]], "probability": str(r[1])} for r in results]
    except Exception as e:
        logging.error(f"Error during prediction: {e}")
        return []

# Get response based on intent
def get_response(ints, intents_json):
    if not ints:
        return "Sorry, I don't understand that."
    tag = ints[0]['intent']
    for intent in intents_json['intents']:
        if intent['tag'] == tag:
            return random.choice(intent['responses'])
    return "You must ask the right questions."

# Generate chatbot response
def chatbot_response(msg):
    ints = predict_class(msg, model)
    return get_response(ints, intents)

# Register a user in the database
def register(userinfo):
    try:
        query = """
        INSERT INTO users (username, email, password)
        VALUES (%s, %s, %s)
        """
        execute_query(query, (userinfo['username'], userinfo['email'], userinfo['password']))
        return "User registered successfully."
    except Exception as e:
        logging.error(f"Error registering user: {e}")
        return "Failed to register user."
