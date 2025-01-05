from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import os
import json
import psycopg2
from kafka import KafkaConsumer
from threading import Thread
import time
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

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
        "stream": True,
        "max_tokens": 150,
        "temperature": 0.7,
        "top_p": 0.9
    }
    
    def stream_generator():
        response = requests.post(
            "http://localhost:11435/v1/chat/completions",
            json=payload,
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    json_str = line[6:]
                    try:
                        chunk = json.loads(json_str)
                        if 'choices' in chunk and len(chunk['choices']) > 0:
                            delta = chunk['choices'][0].get('delta', {})
                            if 'content' in delta:
                                content = delta['content']
                                yield content  # Yield each piece of content
                    except json.JSONDecodeError:
                        continue

    return stream_generator()


def process_kafka_message(message):
    user_query = message.value.decode('utf-8').replace('"', '')
    print(f"Processing query: {user_query}")
    
    messages = [
        {
            "role": "system",
            "content": "You are a network admin and linux servers and K8s expert helping solve SRE issues in air-gapped env."
        },
        {"role": "user", "content": user_query},
    ]
    
    result = chat_with_ollama(messages)
    
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

@app.route('/message_stream', methods=['GET'])
def message_stream():
    print("/messageeeee")
    try:
        # Extract chatMessages from query parameters or elsewhere if needed
        chat_messages = request.args.get('chatMessages', '[]')
        chat_messages = json.loads(chat_messages)

        print("Received chat messages:")
        for message in chat_messages:
            print(f"Role: {message['role']}, Content: {message['content']}")

        def generate_stream():
            try:
                messages = [{"role": m["role"], "content": m["content"]} for m in chat_messages]
                for chunk in chat_with_ollama(messages):
                    yield f"data: {chunk}\n\n"  # Send each chunk as an SSE
            except Exception as e:
                yield f"data: Error streaming response: {e}\n\n"

        return Response(stream_with_context(generate_stream()), content_type='text/event-stream')

    except Exception as e:
        print(f"Error processing request: {e}")
        return jsonify({"error": "Something went wrong"}), 500

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
    # kafka_thread = Thread(target=kafka_listener, daemon=True)
    # kafka_thread.start()
    app.run(debug=True)
