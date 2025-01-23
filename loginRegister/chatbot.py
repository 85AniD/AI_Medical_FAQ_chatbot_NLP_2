import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from loginRegister.processor import chatbot_response

def get_response(user_input):
    try:
        return chatbot_response(user_input)  # Main response generator
    except Exception as e:
        return f"Error in processing response: {e}"

def start_chatbot():
    print("AI Medical FAQ Chatbot is ready. Type 'quit' to exit.")
    while True:
        message = input("You: ")
        if message.lower() == 'quit':
            print("Goodbye!")
            break
        response = get_response(message)
        print(f"Chatbot: {response}")

if __name__ == "__main__":
    start_chatbot()