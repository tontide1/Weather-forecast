# filepath: c:\Users\tontide1\Desktop\weather\Weather-forecast_1\Dockerfile
FROM apache/airflow:2.7.3-python3.11

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y \
    build-essential \
    postgresql-client \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Copy requirements files
COPY requirements.txt .
COPY airflow/requirements.txt ./airflow-requirements.txt

# Install Python dependencies and setup directories
RUN mkdir -p /RandomForest_predictions && \
    mkdir -p ${AIRFLOW_HOME}/weather_data && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r airflow-requirements.txt

# Set the AIRFLOW_HOME environment variable
ENV AIRFLOW_HOME=/opt/airflow

# Copy DAGs, plugins, and data
COPY --chown=airflow:root airflow/dags/ ${AIRFLOW_HOME}/dags/
COPY --chown=airflow:root weather_data/ ${AIRFLOW_HOME}/weather_data/

# Copy entrypoint script
COPY airflow-entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Configure for Railway deployment
ENV PORT=8080
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__WEBSERVER__EXPOSE_CONFIG=True
ENV AIRFLOW__WEBSERVER__BASE_URL=https://${RAILWAY_PUBLIC_DOMAIN}
ENV AIRFLOW__WEBSERVER__ENABLE_PROXY_FIX=True
ENV AIRFLOW__WEBSERVER__PROXY_FIX_X_FOR=1
ENV AIRFLOW__WEBSERVER__PROXY_FIX_X_PROTO=1
ENV AIRFLOW__WEBSERVER__PROXY_FIX_X_HOST=1
ENV AIRFLOW__WEBSERVER__PROXY_FIX_X_PORT=1

# Health check
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=30s --retries=3 CMD curl -f http://localhost:8080/health || exit 1

ENTRYPOINT ["/entrypoint.sh"]