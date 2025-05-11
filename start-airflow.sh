#!/bin/bash

# Dừng và xóa các container cũ
echo "Stopping and removing old containers..."
docker-compose -f docker-compose-airflow.yml down

# Khởi động Airflow với biến môi trường từ .env.airflow
echo "Starting Airflow..."
docker-compose --env-file .env.airflow -f docker-compose-airflow.yml up -d

echo "Airflow is running at http://localhost:8080"
echo "Username: airflow"
echo "Password: airflow"
