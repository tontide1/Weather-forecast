#!/bin/bash

# Exit on any error
set -e

echo "=== STARTING AIRFLOW ENTRYPOINT ==="

# Function to wait for database connection
wait_for_db() {
  echo "=== WAIT FOR DATABASE ==="
  local i=0
  while [ $i -lt 30 ]; do
    if pg_isready -h "${DATABASE_HOST}" -p "${DATABASE_PORT}" -U "${DATABASE_USER}"; then
      echo "=== DATABASE IS AVAILABLE ==="
      return 0
    fi
    i=$((i+1))
    echo "Database is not ready yet, waiting... (Attempt $i/30)"
    sleep 5
  done
  echo "ERROR: Database connection timed out!"
  return 1
}

# Create necessary directories if they don't exist
echo "=== PREPARING DIRECTORIES ==="
mkdir -p ${AIRFLOW_HOME}/weather_data

# Wait for database
wait_for_db

# If RAILWAY_ENVIRONMENT is present, we are on Railway
if [ -n "$RAILWAY_ENVIRONMENT" ]; then
  echo "Running on Railway deployment"
  
  # Initialize the database if needed
  echo "=== INITIALIZING AIRFLOW DATABASE ==="
  airflow db init
  
  # Create default admin user if not exists
  echo "=== CHECKING/CREATING ADMIN USER ==="
  if ! airflow users list | grep -q "$ADMIN_USERNAME"; then
    echo "Creating admin user: $ADMIN_USERNAME"
    airflow users create \
      --username "${ADMIN_USERNAME}" \
      --firstname Admin \
      --lastname User \
      --role Admin \
      --email "${ADMIN_EMAIL}" \
      --password "${ADMIN_PASSWORD}"
  else
    echo "Admin user already exists."
  fi
  
  # Start Airflow in standalone mode
  echo "=== STARTING AIRFLOW STANDALONE ==="
  exec airflow standalone
else
  # In Docker Compose environment, use the command provided
  echo "=== STARTING AIRFLOW WITH COMMAND: $@ ==="
  exec airflow "$@"
fi
