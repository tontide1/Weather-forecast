# import csv
# import numpy as np
# import pandas as pd
# import xgboost as xgb
# from sklearn.preprocessing import LabelEncoder

import os
import requests
from datetime import date, datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator


# Định nghĩa các biến
# DATA_DIR = "/opt/airflow/weather_data"
# PREDICTION_DIR = "/opt/airflow/xgboost_predictions"
# PREDICTION_FILE = os.path.join(PREDICTION_DIR, "weather_forecast_7days.csv")



def start_task():
    print(datetime.now())
    print("Bắt đầu xây dựng mô hình dự báo thời tiết.")

def collect_weather_data():
    print("Bắt đầu thu thập dữ liệu thời tiết.")
    import psycopg2
    from dotenv import load_dotenv
    load_dotenv()
    DB_PARAMS = {
        'database': os.environ.get("DATABASE_NAME"),
        'user': os.environ.get("DATABASE_USER"),
        'password': os.environ.get("DATABASE_PASSWORD"),
        'host': os.environ.get("DATABASE_HOST"),
        'port': os.environ.get("DATABASE_PORT")
    }
    print(DB_PARAMS)
    print("Kết nối đến PostgreSQL")

    connection = psycopg2.connect(**DB_PARAMS)
    cursor = connection.cursor()

    # Tạo bảng nếu chưa tồn tại
    create_table_query = """
    CREATE TABLE IF NOT EXISTS t (
        id SERIAL PRIMARY KEY,
        wind_speed FLOAT NOT NULL
    );
    """
    cursor.execute(create_table_query)
    connection.commit()

    insert_query = """
    INSERT INTO t (wind_speed)
    VALUES (5000);
    """
    cursor.execute(insert_query)
    connection.commit()
    # Lấy dữ liệu thời tiết từ API

def end_task():
    print("Dữ liệu đã được thu thập thành công và lưu vào PostgreSQL.")



# Define default arguments for the DAG
default_args = {
    'owner': 'Collector',
    'start_date': datetime(2025, 5, 10),
    # 'retries': 3,
    # 'retry_delay': timedelta(minutes=3),
    'retries': 0,
    'retry_delay': timedelta(seconds=5),
}

# Define the DAG
dag = DAG(
    dag_id='test_dag',
    default_args=default_args,
    description="DAG thu thập dữ liệu thời tiết",
    schedule_interval="@daily",
    catchup=False,
)


# Define the tasks
start_task = PythonOperator(
    task_id='start',
    python_callable=start_task,
    dag=dag,
)

collect_weather_data_task = PythonOperator(
    task_id='collect_weather_data',
    python_callable=collect_weather_data,
    dag=dag,
)

end_task = PythonOperator(
    task_id='end',
    python_callable=end_task,
    dag=dag,
)

# Set task dependencies
start_task >> collect_weather_data_task >> end_task