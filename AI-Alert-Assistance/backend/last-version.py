from flask import Flask, render_template, request, jsonify, Response
import os
from flask_cors import CORS
import json
import psycopg2
from kafka import KafkaConsumer
from threading import Thread
import requests

app = Flask(__name__)
CORS(app)

DB_PARAMS = {
    'dbname': 'querydb',
    'user': 'admin',
    'password': 'password123',
    'host': 'localhost',
    'port': '5432'
}

KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'k8s-alerts'

def get_db_connection():
    return psycopg2.connect(**DB_PARAMS)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            id SERIAL PRIMARY KEY,
            query_text TEXT NOT NULL,
            response TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cur.close()
    conn.close()

def chat_with_ollama(messages, model_name="custom-model"):
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": True,
        "max_tokens": 150,
        "temperature": 0.7,
        "top_p": 0.9
    }

    print(payload)
    
    def stream_generator():
        response = requests.post(
            "http://localhost:11435/v1/chat/completions",
            json=payload,
            stream=True
        )
        
        for line in response.iter_lines():
            if line and line.startswith(b"data: "):
                try:
                    chunk = json.loads(line[6:])
                    if "choices" in chunk and chunk["choices"]:
                        #print(chunk["choices"][0]["delta"].get("content", ""))
                        yield chunk["choices"][0]["delta"].get("content", "")
                        
                except json.JSONDecodeError:
                    continue

    return stream_generator()

def process_kafka_message(message):
    user_query = message.value.decode("utf-8").replace('"', '')
    user_query += ". Give me a 5-line answer."
    
    messages = [
        {
            "role": "system",
            "content": "You are a network admin and Linux servers and K8s expert helping solve SRE issues in air-gapped environments."
        },
        {"role": "user", "content": user_query},
    ]
    
    result = "".join(chat_with_ollama(messages))
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO queries (query_text, response) VALUES (%s, %s)", (user_query, result))
    conn.commit()
    cur.close()
    conn.close()

def kafka_listener():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id="k8s-group",
        auto_offset_reset="earliest"
    )
    for message in consumer:
        process_kafka_message(message)

@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT query_text, response, timestamp FROM queries ORDER BY timestamp DESC LIMIT 10")
    recent_queries = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", recent_queries=recent_queries)

@app.route("/chat")
def chat():
    return render_template("chat.html")

@app.route("/dor", methods=["POST"])
def dor_chat():
    data = request.get_json()
    query = data.get("query", "")
    chat_history = data.get("history", [])
    
    messages = chat_history + [
        {"role": "system", "content": "You are a network admin and Linux servers and K8s expert helping solve SRE issues in air-gapped environments."},
        {"role": "user", "content": query}
    ]
    
    def generate_response():
        try:
            for chunk in chat_with_ollama(messages):
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}"
    
    return Response(
        generate_response(),
        mimetype="text/plain"
    )

if __name__ == "__main__":
    init_db()
    kafka_thread = Thread(target=kafka_listener, daemon=True)
    kafka_thread.start()
    app.run(host="0.0.0.0", port=5000)
