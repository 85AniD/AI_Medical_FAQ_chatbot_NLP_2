import json
import numpy as np
import nltk
import random
from nltk.stem import WordNetLemmatizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.optimizers import SGD
import pickle

lemmatizer = WordNetLemmatizer()

# Load intents
with open('loginRegister/data/intents.json', 'r', encoding='utf-8') as file:
    intents = json.load(file)

words = []
classes = []
documents = []
ignore_letters = ['!', '?', ',', '.']

# Data preprocessing
for intent in intents['intents']:
    for pattern in intent['patterns']:
        word_list = nltk.word_tokenize(pattern)
        words.extend(word_list)
        documents.append((word_list, intent['tag']))
        if intent['tag'] not in classes:
            classes.append(intent['tag'])

words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_letters]
words = sorted(set(words))
classes = sorted(set(classes))

# Save words and classes
with open('loginRegister/data/words.pkl', 'wb') as file:
    pickle.dump(words, file)
with open('loginRegister/data/classes.pkl', 'wb') as file:
    pickle.dump(classes, file)

# Create training data
training = []
output_empty = [0] * len(classes)

for doc in documents:
    bag = []
    pattern_words = doc[0]
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]

    for word in words:
        bag.append(1 if word in pattern_words else 0)

    output_row = list(output_empty)
    output_row[classes.index(doc[1])] = 1

    training.append([bag, output_row])

# Shuffle and convert training data
random.shuffle(training)
training = np.array(training, dtype=object)

# Split the data
train_x = np.array([entry[0] for entry in training])
train_y = np.array([entry[1] for entry in training])

print(f"train_x shape: {train_x.shape}")
print(f"train_y shape: {train_y.shape}")

# Build the model
model = Sequential()
model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(classes), activation='softmax'))

# Compile the model
sgd = SGD(learning_rate=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])

# Train the model
model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)

# Save the model
model.save('loginRegister/data/chatbot_model.h5')
