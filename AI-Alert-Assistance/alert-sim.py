# kafka_producer.py
from kafka import KafkaProducer
import json
import time

KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'k8s-alerts'

producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
)

alerts = [
    "link state down - switch cisco",
    "server ido-shob-1: service sssd not running",
    "Linux server tif-prd-app-1: high cpu usage",
    "Node not ready",
    "Deployment does not have all replicas",
    "API server latency is high",
    "Pod is stuck in CrashLoopBackOff",
    "Disk usage exceeds 90%",
]

for alert in alerts:
    print(f"Sending alert: {alert}")
    producer.send(KAFKA_TOPIC, alert)
    time.sleep(1)  # Simulate delay

