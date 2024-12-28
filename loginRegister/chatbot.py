from loginRegister.processor import chatbot_response

def start_chatbot():
    """Starts a CLI-based chatbot."""
    print("AI Medical FAQ Chatbot is ready. Type 'quit' to exit.")
    while True:
        message = input("You: ")
        if message.lower() == 'quit':
            print("Goodbye!")
            break
        response = chatbot_response(message)
        print(f"Chatbot: {response}")

if __name__ == "__main__":
    start_chatbot()
