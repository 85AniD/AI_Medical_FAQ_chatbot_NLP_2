from locust import HttpUser, task, between

class ChatbotUser(HttpUser):
    wait_time = between(1, 2.5)

    @task
    def interact_with_chatbot(self):
        self.client.post("/chatbot", json={"subject": "What are the symptoms of COVID-19?"})