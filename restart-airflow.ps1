# Script để khởi động lại Airflow và xóa volume cũ trên Windows
Write-Host "Stopping and removing old containers..." -ForegroundColor Cyan
docker-compose -f docker-compose-airflow.yml down

Write-Host "Removing PostgreSQL volume..." -ForegroundColor Red
docker volume rm weather-forecast_postgres-db-volume

Write-Host "Starting Airflow with new volumes..." -ForegroundColor Green
docker-compose --env-file .env.airflow -f docker-compose-airflow.yml up -d

Write-Host "Airflow is running at http://localhost:8080" -ForegroundColor Yellow
Write-Host "Username: airflow" -ForegroundColor Yellow
Write-Host "Password: airflow" -ForegroundColor Yellow
