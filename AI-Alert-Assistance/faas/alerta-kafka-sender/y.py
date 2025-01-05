import requests
import json

def fetch_alerts():
    ALERTA_URL = "http://localhost:8081/api/alerts"
    ALERTA_API_KEY = "CwhfNd_09NRlBFVtS1S5RCOgGvFG-H4aV8Q6L0jP"
    response = requests.get(ALERTA_URL, headers={"Authorization": f"Key {ALERTA_API_KEY}"})
    return response.json().get('alerts', [])

if __name__ == "__main__":
    alerts = fetch_alerts()
    print(alerts)

