# Base image
FROM python:3.11-slim-bullseye

# Set environment variables for Python optimization
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app

# Working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install system dependencies including PostgreSQL client
RUN apt-get update && \
    apt-get install -y postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create directories for weather data storage
RUN mkdir -p /app/weather_data

# Copy source code
COPY . .

# Make entrypoint script executable
RUN chmod +x ./entrypoint.sh

# Use entrypoint script
ENTRYPOINT ["./entrypoint.sh"]

# Run server
CMD ["gunicorn", "--chdir", "/app/src", "weather_forecast_management.wsgi:application", "--bind", "0.0.0.0:8000"]
