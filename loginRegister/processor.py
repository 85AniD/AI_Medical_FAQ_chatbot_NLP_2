import json
import random
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
import numpy as np
import pickle
import nltk
from db.database import execute_query

nltk.download('punkt')
lemmatizer = WordNetLemmatizer()

# Load required files
intents = json.load(open('intents.json', encoding='utf-8'))
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_model.h5')

def clean_up_sentence(sentence):
    """Tokenizes and lemmatizes a sentence."""
    sentence_words = nltk.word_tokenize(sentence)
    return [lemmatizer.lemmatize(word.lower()) for word in sentence_words]

def bow(sentence, words, show_details=False):
    """Convert a sentence into a bag-of-words."""
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
    """Predict the class of a sentence."""
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return [{"intent": classes[r[0]], "probability": str(r[1])} for r in results]

def get_response(ints, intents_json):
    """Get a response for the predicted intent."""
    if not ints:
        return "Sorry, I don't understand that."
    tag = ints[0]['intent']
    for i in intents_json['intents']:
        if i['tag'] == tag:
            return random.choice(i['responses'])
    return "You must ask the right questions."

def chatbot_response(msg):
    """Generate a chatbot response."""
    ints = predict_class(msg, model)
    return get_response(ints, intents)

def register(userinfo):
    """Register a user in the database."""
    query = """
    INSERT INTO users (username, email, password)
    VALUES (%s, %s, %s)
    """
    execute_query(query, (userinfo['username'], userinfo['email'], userinfo['password']))
    return "User registered successfully."
