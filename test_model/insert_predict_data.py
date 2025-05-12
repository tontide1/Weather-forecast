import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
from decouple import config

load_dotenv()



connection = None
try:
    connection = psycopg2.connect(
        dbname=config("DATABASE_NAME"),
        user=config("DATABASE_USER"),
        password=config("DATABASE_PASSWORD"),
        host=config("DATABASE_HOST"),
        port=config("DATABASE_PORT")
    )
except Exception as e:
    print("Lỗi khi kết nối tới PostgreSQL:", e)


if connection is not None:
    cursor = connection.cursor()
    table_name = config("PREDICT_WEATHER_DATA_TABLE_NAME", default="predict_weather")
    try:
        # cursor.execute(f"""
        #     DROP TABLE IF EXISTS {table_name};
        # """)
        # connection.commit()
        # print(f"Xóa bảng bảng dữ liệu dự đoán thành công.")
        # Tạo một bảng
        cursor.execute(
            f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    Province VARCHAR(100) NOT NULL,
                    Date TIMESTAMP NOT NULL,
                    Temp_Max DECIMAL(5,2),
                    Temp_Min DECIMAL(5,2),
                    Weather_Code INTEGER,
                    Weather_Description VARCHAR(100)
                );
            """
        )
        connection.commit()
        print(f"Tạo bảng dữ liệu dự đoán thành công")

        # cursor.execute(
        #     f"""
        #     SELECT column_name
        #     FROM information_schema.columns
        #     WHERE table_name = %s
        #     ORDER BY ordinal_position;
        #     """,
        #     (table_name,)  # Truyền tên bảng vào truy vấn
        # )
        # # Lấy kết quả
        # columns = cursor.fetchall()
        # print(f"Các cột trong bảng '{table_name}':")
        # for column in columns:
        #     print(column[0])
        
        # Đọc file CSV và chèn dữ liệu vào bảng
        data_file = "test_model/xgboost_predictions/weather_forecast_7days.csv"
        with open(data_file, mode="r", encoding="utf-8") as csv_file:
            cursor.copy_expert(
                f"""
                COPY {table_name} (
                    Province,Date,Temp_Max,Temp_Min,Weather_Code,Weather_Description
                )
                FROM STDIN
                WITH (FORMAT CSV, HEADER TRUE);
                """,
                csv_file
            )
        connection.commit()
        print("Dữ liệu dự đoán đã được thêm vào cơ sở dữ liệu thành công!")

        # # Lấy dữ liệu
        # cursor.execute(f"SELECT * FROM {table_name};")
        # rows = cursor.fetchall()
        # print(f"Dữ liệu trong bảng {table_name}:")
        # for row in rows:
        #     print(row)

    except Exception as e:
        print("Lỗi khi thêm dữ liệu:", e)
        connection.rollback()
    finally:
        # Đóng kết nối
        cursor.close()
        connection.close()
        print("Đã đóng kết nối tới PostgreSQL.")