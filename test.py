import sqlite3

db_path = "/Users/medsidd/mental_health_app/backend/database/mental_health_app.db"  # Update with your actual database path
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Add the ai_response column if it doesn't already exist
cursor.execute("PRAGMA table_info(chats)")
columns = [column[1] for column in cursor.fetchall()]
if "ai_response" not in columns:
    cursor.execute("ALTER TABLE chats ADD COLUMN ai_response TEXT")

conn.commit()
conn.close()
print("Database updated successfully!")
