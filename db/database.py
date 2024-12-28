import mysql.connector
from mysql.connector import Error

class Database:
    def __init__(self, host='localhost', user='root', password='Qaz_123', database='medical_faq_chatbot'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print("Connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")

    def execute_script(self, script):
        try:
            if self.connection:
                cursor = self.connection.cursor()
                for statement in script.split(';'):
                    if statement.strip():
                        cursor.execute(statement)
                self.connection.commit()
                print("Executed script successfully.")
            else:
                print("Error: No active database connection.")
        except Error as e:
            print(f"Error executing script: {e}")

    def retrieve_data(self, table_name):
        try:
            if self.connection:
                cursor = self.connection.cursor()
                query = f"SELECT * FROM {table_name}"
                cursor.execute(query)
                rows = cursor.fetchall()
                return rows
            else:
                print("Error: No active database connection.")
        except Error as e:
            print(f"Error retrieving data: {e}")
        return None

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed.")
