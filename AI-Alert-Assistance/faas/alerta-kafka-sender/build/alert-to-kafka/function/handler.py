# alert-to-kafka/handler.py
import requests
import json
from datetime import datetime, timedelta

def handle(req):
    """
    Handle both scheduled and manual invocations
    """
    try:
        # Your alert processing logic
        alerts = fetch_alerts()
        return alerts
        if alerts:
            filtered_alerts = filter_alerts_last_minute(alerts)
            if filtered_alerts:
                send_alerts_to_kafka(filtered_alerts)
                return {"status": "success", "message": f"Processed {len(filtered_alerts)} alerts"}
            else:
                return {"status": "success", "message": "No alerts in the last minute"}
        return {"status": "success", "message": "No alerts found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def fetch_alerts():
    ALERTA_URL = "http://alerta-web.default.svc.cluster.local:8080/api/alerts"
    ALERTA_API_KEY = "CwhfNd_09NRlBFVtS1S5RCOgGvFG-H4aV8Q6L0jP"
    print("xxxxxx")
    response = requests.get(ALERTA_URL, headers={"Authorization": f"Key {ALERTA_API_KEY}"})
    print(response)
    if response.status_code == 200:
        return response.json().get('alerts', [])
    else:
        print(f"Failed to fetch alerts: {response.status_code}")
        return []

def filter_alerts_last_minute(alerts):
    now = datetime.utcnow()
    one_minute_ago = now - timedelta(minutes=1)
    
    return [
        alert for alert in alerts
        if datetime.strptime(alert.get('createTime'), "%Y-%m-%dT%H:%M:%S.%fZ") >= one_minute_ago
    ]

def send_alerts_to_kafka(alerts):
    KAFKA_BROKER = "localhost:9092"
    KAFKA_TOPIC = "k8s-alerts"
    
    from kafka import KafkaProducer
    producer = KafkaProducer(
        bootstrap_servers=KAFKA_BROKER,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    
    for alert in alerts:
        producer.send(KAFKA_TOPIC, value=alert.get('text'))

