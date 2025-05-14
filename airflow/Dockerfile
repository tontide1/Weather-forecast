FROM apache/airflow:2.7.3-python3.11

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    postgresql-client \
    build-essential \
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

# Copy DAGs if you have them
COPY --chown=airflow:root dags/ ${AIRFLOW_HOME}/dags/

# Copy any other necessary files (plugins, configs, etc.)
# COPY --chown=airflow:root plugins/ ${AIRFLOW_HOME}/plugins/
# COPY --chown=airflow:root config/ ${AIRFLOW_HOME}/config/