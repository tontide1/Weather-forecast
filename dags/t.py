import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta
import os
import pandas as pd
import numpy as np
from airflow import DAG
from airflow.operators.python import PythonOperator

# Định nghĩa các biến
DATA_DIR = "/opt/airflow/weather_data"
PREDICTION_DIR = "/opt/airflow/RandomForest_predictions"
# PREDICTION_DIR = "/opt/airflow/weather_data"
PREDICTION_FILE = os.path.join(PREDICTION_DIR, "weather_forecast_7days.csv")



def start_task():
    print("Bắt đầu xây dựng mô hình dự báo thời tiết.")

def build_randomforest_model():
    # import psycopg2
    # try:
    #     # Kết nối đến PostgreSQL
    #     connection = psycopg2.connect(
    #         database=os.environ.get("DATABASE_NAME"),
    #         user=os.environ.get("DATABASE_USER"),
    #         password=os.environ.get("DATABASE_PASSWORD"),
    #         host=os.environ.get("DATABASE_HOST"),
    #         port=os.environ.get("DATABASE_PORT"),
    #     )
    #     cursor = connection.cursor()
        
    #     # Tạo bảng chứa dữ liệu dự đoán
    #     table_name = os.environ.get("PREDICT_WEATHER_DATA_TABLE_NAME", default="predict_weather")
    #     cursor.execute(
    #         f"""
    #             CREATE TABLE IF NOT EXISTS {table_name} (
    #                 id SERIAL PRIMARY KEY,
    #                 Province VARCHAR(100) NOT NULL,
    #                 Time DATE NOT NULL,
    #                 Temp_Max DECIMAL(5,2),
    #                 Temp_Min DECIMAL(5,2),
    #                 Weather_Code INTEGER,
    #                 Weather_Description VARCHAR(100),
    #                 CONSTRAINT unique_province_time UNIQUE (Province, Time)
    #             );
    #         """
    #     )
    #     connection.commit()

    #     # Tạo bảng tạm để chứa dữ liệu từ CSV
    #     temp_table_name = table_name+"_temp"
    #     cursor.execute(
    #         f"""
    #         CREATE TEMPORARY TABLE {temp_table_name} (
    #             Province VARCHAR(100),
    #             Time TIMESTAMP,
    #             Temp_Max DECIMAL(5,2),
    #             Temp_Min DECIMAL(5,2),
    #             Weather_Code INTEGER,
    #             Weather_Description VARCHAR(100)
    #         );
    #         """
    #     )
    #     connection.commit()

    #     # Chèn dữ liệu từ CSV vào bảng tạm
    #     query = f"""
    #         INSERT INTO {temp_table_name} (
    #             Province, Time, Temp_Max, Temp_Min, Weather_Code, Weather_Description
    #         )
    #         VALUES (%s, %s, %s, %s, %s, %s)
    #     """
    #     cursor.executemany(query, prediction_results_tuples)
    #     connection.commit()

    #     # Ghi dữ liệu từ bảng tạm vào bảng chính
    #     cursor.execute(
    #         f"""
    #         INSERT INTO {table_name} (
    #             Province, Time, Temp_Max, Temp_Min, Weather_Code, Weather_Description
    #         )
    #         SELECT
    #             Province, Time, Temp_Max, Temp_Min, Weather_Code, Weather_Description
    #         FROM {temp_table_name}
    #         ON CONFLICT ON CONSTRAINT unique_province_time
    #         DO UPDATE SET
    #             Temp_Max = EXCLUDED.Temp_Max,
    #             Temp_Min = EXCLUDED.Temp_Min,
    #             Weather_Code = EXCLUDED.Weather_Code,
    #             Weather_Description = EXCLUDED.Weather_Description;
    #         """
    #     )
    #     connection.commit()
    #     print("Dữ liệu dự đoán đã được thêm vào cơ sở dữ liệu thành công!")
    # except Exception as e:
    #     connection.rollback()
    #     print(f"Lỗi khi ghi vào PostgreSQL: {str(e)}")
    #     raise
    # finally:
    #     cursor.close()
    #     connection.close()

    # Tạo thư mục lưu kết quả dự đoán
    # os.makedirs(PREDICTION_DIR, exist_ok=True)

    # Xếp lại và lưu kết quả dự đoán (chỉ lưu file này)
    # prediction_results.to_csv(PREDICTION_FILE, index=False)

    print(f"\nĐã hoàn thành dự báo thời tiết cho tỉnh thành!")
    # print(f"File dự báo: {PREDICTION_FILE}")



def end_task():
    print("Hoàn thành xây dựng mô hình dự báo thời tiết.")



# Define default arguments for the DAG
default_args = {
    'owner': 'Predictor',
    'start_date': datetime(2025, 5, 10),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'retry_delay': timedelta(seconds=5),
}

# Define the DAG
dag = DAG(
    dag_id='Build_RandomForest_Model',
    default_args=default_args,
    description="DAG dự báo thời tiết bằng RandomForest",
    schedule_interval='@daily',
    catchup=False,
)


# Define the tasks
start_task = PythonOperator(
    task_id='start',
    python_callable=start_task,
    dag=dag,
)

build_model_randomforest_task = PythonOperator(
    task_id='build_randomforest_model',
    python_callable=build_randomforest_model,
    dag=dag,
)

end_task = PythonOperator(
    task_id='end',
    python_callable=end_task,
    dag=dag,
)

# Set task dependencies
start_task >> build_model_randomforest_task >> end_task