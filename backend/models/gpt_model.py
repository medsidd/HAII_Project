import openai
import json
import sqlite3
from datetime import datetime, timedelta
import os
from nltk.tokenize import sent_tokenize
import re

# Load OpenAI API key from config file
config_path = "/Users/medsidd/mental_health_app/backend/config/openai_config.json"
with open(config_path, "r") as config_file:
    config = json.load(config_file)
openai.api_key = config["api_key"]

# Constants
MODEL_NAME = "gpt-3.5-turbo"
MAX_TOKENS = 1500
CONTEXT_LIMIT = 3000
CHECKIN_INTERVAL = timedelta(hours=6)  # Example interval for periodic check-ins

# Load prompts.json
prompts_path = "/Users/medsidd/mental_health_app/backend/static/prompts.json"
with open(prompts_path, "r") as prompts_file:
    prompts = json.load(prompts_file)


class GPTModel:
    def __init__(self, db_path="/Users/medsidd/mental_health_app/backend/database/mental_health_app.db"):
        self.db_path = db_path
        self.initialize_database()
        self.persona_context = "\n".join(prompts["persona"])
        self.action_prompts = prompts["action_prompts"]

    def initialize_database(self):
        """Initialize SQLite database for storing chat history and periodic checks."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY,
                user_message TEXT NOT NULL,
                gpt_response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkins (
                id INTEGER PRIMARY KEY,
                checkin_message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def fetch_chat_history(self, limit=10):
        """Fetch the most recent chat history from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT user_message, gpt_response FROM chats ORDER BY id DESC LIMIT ?", (limit,))
        history = cursor.fetchall()
        conn.close()

        formatted_history = []
        for user_message, gpt_response in reversed(history):
            formatted_history.append(f"User: {user_message}")
            formatted_history.append(f"AI: {gpt_response}")
        return "\n".join(formatted_history)

    def truncate_context(self, context, limit=CONTEXT_LIMIT):
        """Truncate context to fit within token limits."""
        sentences = sent_tokenize(context)
        truncated_context = ""
        token_count = 0

        for sentence in sentences:
            token_count += len(sentence.split())  # Approximate token count
            if token_count > limit:
                break
            truncated_context += f"{sentence} "
        
        return truncated_context.strip()

    def generate_response(self, user_message):
        """Generate a response using GPT-3.5-turbo."""
        chat_history = self.fetch_chat_history()
        full_context = f"{self.persona_context}\n\n{chat_history}\nUser: {user_message}"
        truncated_context = self.truncate_context(full_context)

        try:
            response = openai.ChatCompletion.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": self.persona_context},
                    {"role": "user", "content": truncated_context}
                ],
                max_tokens=MAX_TOKENS,
                temperature=0.7,
                top_p=0.9,
                frequency_penalty=0.5,
                presence_penalty=0.6
            )
            gpt_response = response['choices'][0]['message']['content']
        except Exception as e:
            gpt_response = "Sorry, I'm having trouble generating a response right now."

        self.save_to_database(user_message, gpt_response)

        return gpt_response

    def save_to_database(self, user_message, gpt_response):
        """Save the conversation to the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chats (user_message, gpt_response) VALUES (?, ?)", (user_message, gpt_response))
        conn.commit()
        conn.close()

    def periodic_checkin(self):
        """Generate periodic check-ins based on action prompts."""
        last_checkin = self.get_last_checkin_time()
        if not last_checkin or datetime.now() - last_checkin > CHECKIN_INTERVAL:
            checkin_message = self.action_prompts["mood_checkins"][0]  # Example check-in prompt
            self.save_checkin_to_database(checkin_message)
            return checkin_message
        return None

    def get_last_checkin_time(self):
        """Fetch the last check-in time."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT timestamp FROM checkins ORDER BY id DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        return datetime.strptime(result[0], "%Y-%m-%d %H:%M:%S") if result else None

    def save_checkin_to_database(self, checkin_message):
        """Save the periodic check-in to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO checkins (checkin_message) VALUES (?)", (checkin_message,))
        conn.commit()
        conn.close()

    def keyword_trigger(self, user_message):
        """Trigger action prompts based on keywords in user input."""
        for category, prompts in self.action_prompts.items():
            for prompt in prompts:
                keywords = re.findall(r'\b\w+\b', prompt.lower())
                if any(keyword in user_message.lower() for keyword in keywords):
                    return prompt
        return None


# Example Usage
if __name__ == "__main__":
    gpt = GPTModel()
    print("AI Ready. Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input.lower() == "quit":
            break
        ai_response = gpt.generate_response(user_input)
        print(f"AI: {ai_response}")
