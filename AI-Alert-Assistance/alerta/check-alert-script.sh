#!/bin/sh

# Fetch alerts from Prometheus
curl http://localhost:9090/api/v1/alerts
echo "\n"

# Wait for 3 seconds
sleep 3

# Fetch alerts from Prometheus Alertmanager
curl http://localhost:9093/api/v1/alerts
echo "\n"

# Wait for 3 seconds
sleep 3

# Fetch alerts from Alerta
curl -H "Authorization: Key NWGKPxkcEy1DYOWLVuvg_Zbr_Jx7gxXjD7CPGwk6" http://localhost:8080/api/alerts
echo "\n"

