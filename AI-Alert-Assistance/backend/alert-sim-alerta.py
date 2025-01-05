import requests
import json
from kafka import KafkaProducer
import time
from datetime import datetime, timedelta

# Alerta and Kafka configurations
ALERTA_URL = "http://localhost:8081/api/alerts"  # Replace with your Alerta server URL
ALERTA_API_KEY = "CwhfNd_09NRlBFVtS1S5RCOgGvFG-H4aV8Q6L0jP"  # Replace with your Alerta API key
KAFKA_BROKER = "localhost:9092"  # Kafka broker address
KAFKA_TOPIC = "k8s-alerts"  # Kafka topic

# Initialize Kafka producer
producer = KafkaProducer(bootstrap_servers=KAFKA_BROKER, value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# Fetch alerts from Alerta API
def fetch_alerts():
    response = requests.get(ALERTA_URL, headers={"Authorization": f"Key {ALERTA_API_KEY}"})
    if response.status_code == 200:
        return response.json().get('alerts', [])
    else:
        print(f"Failed to fetch alerts: {response.status_code}")
        return []

# Filter alerts created in the last minute
def filter_alerts_last_minute(alerts):
    now = datetime.utcnow()
    one_minute_ago = now - timedelta(minutes=1)

    filtered_alerts = []
    for alert in alerts:
        create_time_str = alert.get('createTime')
        if create_time_str:
            create_time = datetime.strptime(create_time_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            if create_time >= one_minute_ago:
                filtered_alerts.append(alert)

    return filtered_alerts

# Send alerts to Kafka
def send_alerts_to_kafka(alerts):
    for alert in alerts:
        print(alert.get('text'))
        time.sleep(2)
        alert_text = alert.get('text')
        producer.send(KAFKA_TOPIC, value=alert_text)
        print(f"Alert sent to Kafka: {alert['id']}")

# Main execution
def main():
    while True:
        alerts = fetch_alerts()
        if alerts:
            filtered_alerts = filter_alerts_last_minute(alerts)
            if filtered_alerts:
                send_alerts_to_kafka(filtered_alerts)
            else:
                print("No alerts in the last minute.")
        else:
            print("No alerts found.")
        
        time.sleep(60)  # Wait for 1 minute before checking again

if __name__ == "__main__":
    main()
