from flask import Flask, render_template, request, jsonify
import os
import json
import psycopg2
from kafka import KafkaConsumer
from threading import Thread
import time

app = Flask(__name__)

# Database connection parameters
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
    cur.execute('''CREATE TABLE IF NOT EXISTS queries (
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
        "stream": False,
        "max_tokens": 150,
        "temperature": 0.7,
        "top_p": 0.9
    }
    json_payload = json.dumps(payload).replace('"', '\\"')
    curl_cmd = f'curl -s -X POST http://localhost:11435/v1/chat/completions -H "Content-Type: application/json" -d "{json_payload}" | jq -r \'.choices[0].message.content\''
    return os.popen(curl_cmd).read()

def process_kafka_message(message):
    user_query = message.value.decode('utf-8').replace('"', '')
    user_query = user_query + ". give me 5 lines answer"
    print(f"Processing query: {user_query}")
    
    # Create the JSON payload
    payload = {
        "model": "custom-model",
        "messages": [
            {
                "role": "system",
                "content": "You are a network admin and linux servers and K8s expert helping solve SRE issues in air-gapped env."
            },
            {"role": "user", "content": user_query},
        ],
        "stream": False,
    }
    
    json_payload = json.dumps(payload).replace('"', '\\"')
    curl_cmd = f'curl -s -X POST http://localhost:11435/v1/chat/completions -H "Content-Type: application/json" -d "{json_payload}" | jq -r \'.choices[0].message.content\''
    result = os.popen(curl_cmd).read()
    
    # Store query and response in the database
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO queries (query_text, response) VALUES (%s, %s)', (user_query, result))
    conn.commit()
    cur.close()
    conn.close()
    print(f"Query processed and stored: {result}")

def kafka_listener():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id='k8s-group',
        auto_offset_reset='earliest',
    )
    print(f"Listening to Kafka topic: {KAFKA_TOPIC}")
    for message in consumer:
        process_kafka_message(message)

@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT query_text, response, timestamp FROM queries ORDER BY timestamp DESC LIMIT 10')
    recent_queries = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', recent_queries=recent_queries)

@app.route('/chat')
def chat():
    return render_template('chat.html')

if __name__ == '__main__':
    init_db()
    # Start Kafka listener in a separate thread
    kafka_thread = Thread(target=kafka_listener, daemon=True)
    kafka_thread.start()
    app.run(debug=True)