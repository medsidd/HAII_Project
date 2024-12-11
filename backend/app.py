from flask import Flask, request, jsonify, send_file
from models.gpt_model import GPTModel
from models.train_distilbert import DistilBERTModel
import sqlite3
import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd
from datetime import datetime
from flask_cors import CORS 
import os
import matplotlib
import matplotlib.dates as mdates
matplotlib.use('Agg')  # Use a non-GUI backend


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)


# Initialize models
gpt_model = GPTModel()
distilbert_model = DistilBERTModel()  # Updated to use the refactored class

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response


# Example chat endpoint
@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        response = app.response_class()
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    try:
        data = request.json
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Fetch the last 3 user messages and AI responses from the database
        conn = sqlite3.connect(gpt_model.db_path, timeout=10)
        cursor = conn.cursor()

        # Fetch last 3 user messages
        cursor.execute(
            "SELECT user_message FROM chats WHERE user_message IS NOT NULL ORDER BY timestamp DESC LIMIT 3"
        )
        user_messages = [row[0] for row in cursor.fetchall()]

        # Fetch last 3 AI responses
        cursor.execute(
            "SELECT gpt_response FROM chats WHERE gpt_response IS NOT NULL ORDER BY timestamp DESC LIMIT 3"
        )
        ai_responses = [row[0] for row in cursor.fetchall()]

        conn.close()

        # Reverse the order to chronological
        user_messages = user_messages[::-1]
        ai_responses = ai_responses[::-1]

        # Construct the context with priority to recent messages
        context = ""
        weights = [1.0, 0.8, 0.6]  # Higher weight for more recent messages
        for i, (user, ai) in enumerate(zip(user_messages, ai_responses)):
            weight = weights[min(i, len(weights) - 1)]  # Use the weight or fallback
            context += f"Weight: {weight}\nUser: {user}\nAI: {ai}\n"

        # Add the current user message to the prompt
        prompt = f"{context}User: {user_message}\nAI:"
        print(prompt)

        # Generate GPT response
        gpt_response = gpt_model.generate_response(prompt) or "I'm here to listen."

        # Save the user message and GPT response to the database
        conn = sqlite3.connect(gpt_model.db_path, timeout=10)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chats (user_message, gpt_response, timestamp) VALUES (?, ?, datetime('now'))",
            (user_message, gpt_response),
        )
        conn.commit()
        conn.close()

        return jsonify({"response": gpt_response})

    except sqlite3.Error as e:
        print("Database error:", e)
        return jsonify({"error": "Database error occurred"}), 500

    except Exception as e:
        print("Error occurred:", e)
        return jsonify({"error": "Internal server error"}), 500



    
# Diagnosis Endpoint
@app.route("/diagnose", methods=["GET"])
def diagnose():
    if request.method == "OPTIONS":
        # Handle CORS preflight request
        response = app.response_class()
        response.headers["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    try:
        # Fetch chat history from the database
        conn = sqlite3.connect(gpt_model.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT user_message FROM chats ORDER BY timestamp ASC")
        chat_history = [row[0] for row in cursor.fetchall()]
        conn.close()

        if not chat_history:
            return jsonify({"error": "No chat history available for diagnosis."}), 400

        # Run diagnosis using DistilBERT
        diagnosis_results = distilbert_model.diagnose(chat_history)
        print("Diagnosis Results:", diagnosis_results)

        # Insert diagnosis results into the trends table
        timestamp = datetime.now()
        conn = sqlite3.connect(gpt_model.db_path)
        cursor = conn.cursor()
        for condition, confidence in diagnosis_results.items():
            cursor.execute(
                "INSERT INTO trends (condition, trend_score, timestamp) VALUES (?, ?, ?)",
                (condition, round(confidence * 100, 2), timestamp),
            )
        conn.commit()
        conn.close()

        # Prepare the response data
        response_data = [
            {"condition": condition, "confidence": round(confidence * 100, 2)}
            for condition, confidence in diagnosis_results.items()
        ]

        return jsonify({"diagnosis": response_data})

    except Exception as e:
        print("Error during diagnosis:", str(e))
        return jsonify({"error": "Internal server error"}), 500


def generate_trend_chart():
    try:
        conn = sqlite3.connect(gpt_model.db_path)
        trends_df = pd.read_sql_query("SELECT * FROM trends ORDER BY timestamp ASC", conn)
        conn.close()

        if trends_df.empty:
            print("No trend data available.")
            return None

        os.makedirs('./charts', exist_ok=True)
        charts = {}
        for condition in trends_df["condition"].unique():
            condition_data = trends_df[trends_df["condition"] == condition]

            # Parse timestamps into datetime objects for accurate plotting
            condition_data["timestamp"] = pd.to_datetime(condition_data["timestamp"])

            plt.figure(figsize=(10, 6))
            
            # Set background color
            plt.gca().set_facecolor("#f5fbfb")
            
            plt.plot(
                condition_data["timestamp"],
                condition_data["trend_score"],
                label=condition,
                marker="o",
                color="#4caf50",  # Green line for the chart
            )

            # Format X-axis to display time in seconds and minutes
            plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            plt.gca().xaxis.set_major_locator(mdates.SecondLocator(interval=5)) # Adjust interval as needed
            plt.gcf().autofmt_xdate()  # Rotate date labels for readability

            plt.title(f"{condition} Severity Trend Over Time", fontsize=14)
            plt.xlabel("Time (HH:MM:SS)", fontsize=12)
            plt.ylabel("Severity (%)", fontsize=12)
            plt.legend()
            plt.grid(color="#d3d3d3", linestyle="--", linewidth=0.5)

            chart_path = f"./charts/trend_chart_{condition}.png"
            plt.savefig(chart_path, bbox_inches="tight", facecolor="#f7f9fc")  
            plt.close()
            print(f"Chart saved at: {chart_path}")
            charts[condition] = chart_path

        return charts
    except Exception as e:
        print(f"Error in generate_trend_chart: {e}")
        return None



# Route to fetch trend chart as an image
@app.route("/trends", methods=["GET"])
def trends():
    try:
        charts = generate_trend_chart()
        if not charts:
            return jsonify({"error": "No trend data available."}), 400

        # Return absolute URLs for the charts to ensure accessibility
        base_url = request.host_url  # Get the base URL of the server
        charts_with_urls = {
            condition: f"{base_url}charts/{os.path.basename(path)}" for condition, path in charts.items()
        }

        return jsonify({"charts": charts_with_urls})
    except Exception as e:
        print(f"Error in /trends endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

# Static file serving for charts
@app.route("/charts/<filename>")
def serve_chart(filename):
    chart_path = os.path.join("charts", filename)
    if not os.path.exists(chart_path):
        return jsonify({"error": "Chart not found"}), 404
    return send_file(chart_path, mimetype="image/png")


@app.route("/reset", methods=["POST"])
def reset_chat():
    try:
        conn = sqlite3.connect(gpt_model.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chats")
        cursor.execute("DELETE FROM trends")
        conn.commit()
        conn.close()
        return jsonify({"message": "Chat history and trends reset successfully."})
    except sqlite3.Error as e:
        print("Database error:", e)
        return jsonify({"error": "Database error occurred"}), 500



if __name__ == "__main__":
    app.run(debug=True)
