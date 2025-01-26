import os
import sys
# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from sklearn.metrics import precision_score, recall_score, f1_score
from loginRegister.processor import predict_class, model, intents

# Test intent classification accuracy
def test_intent_classification_accuracy():
    test_cases = [
        ("What are the symptoms of COVID-19?", "symptoms"),
        ("How is COVID-19 treated?", "treatment"),
        ("What is the incubation period for COVID-19?", "incubation"),
        ("Is there a vaccine for COVID-19?", "vaccine"),
        ("How can I prevent COVID-19?", "prevention"),
    ]
    y_true = []
    y_pred = []

    for sentence, expected_intent in test_cases:
        intents_pred = predict_class(sentence, model)
        predicted_intent = intents_pred[0]['intent'] if intents_pred else "unknown"
        y_true.append(expected_intent)
        y_pred.append(predicted_intent)

    # Calculate precision, recall, and F1-score
    precision = precision_score(y_true, y_pred, average='weighted')
    recall = recall_score(y_true, y_pred, average='weighted')
    f1 = f1_score(y_true, y_pred, average='weighted')

    # Assertions
    assert precision > 0.8, f"Precision is too low: {precision}"
    assert recall > 0.8, f"Recall is too low: {recall}"
    assert f1 > 0.8, f"F1-score is too low: {f1}"

    # Print metrics for debugging
    print(f"Precision: {precision}")
    print(f"Recall: {recall}")
    print(f"F1-score: {f1}")