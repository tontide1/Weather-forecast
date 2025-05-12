FROM apache/airflow:2.7.3-python3.11

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the AIRFLOW_HOME environment variable
ENV AIRFLOW_HOME=/opt/airflow

# Initialize directories
RUN mkdir -p ${AIRFLOW_HOME}/weather_data
