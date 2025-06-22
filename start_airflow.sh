#!/bin/bash

echo "🚀 Starting Airflow Scheduler..."
airflow scheduler &

echo "🌐 Starting Airflow Webserver on port 8080..."
airflow webserver --port 8080
