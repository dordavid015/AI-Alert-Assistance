from flask import Flask, render_template, request, jsonify, Response, stream_with_context
import os
from flask_cors import CORS
import json
import psycopg2
from kafka import KafkaConsumer
from threading import Thread
import time
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
        
        collected_response = ""
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
                                collected_response += content
                                print(content, end='', flush=True)
                    except json.JSONDecodeError:
                        continue
        return collected_response

    return stream_generator()

def process_kafka_message(message):
    user_query = message.value.decode('utf-8').replace('"', '')
    user_query = user_query +'.give me 5 lines answer'
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

@app.route('/dor', methods=['POST'])
def dor_chat():
    data = request.get_json()
    query = data.get('query', '')
    chat_history = data.get('history', [])
    
    # Add user message to history
    messages = chat_history + [
        {
            "role": "system",
            "content": "You are a network admin and linux servers and K8s expert helping solve SRE issues in air-gapped env."
        },
        {"role": "user", "content": query + ". please answer fast"}
    ]
    
    def generate_response():
        try:
            for chunk in chat_with_ollama(messages):
                yield chunk
        except Exception as e:
            yield f"Error: {str(e)}"
    
    return Response(
        generate_response(),
        mimetype='text/plain',
        headers={
            'Cache-Control': 'no-cache',
            'Transfer-Encoding': 'chunked'
        }
    )

@app.route('/dor_chat')
def dor_chat_page():
    return render_template('chat-answer.html')

if __name__ == '__main__':
    init_db()
    kafka_thread = Thread(target=kafka_listener, daemon=True)
    kafka_thread.start()
    app.run(debug=True)
