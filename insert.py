import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv
from decouple import config

load_dotenv()


connection = None
try:
    # Kết nối tới PostgreSQL
    connection = psycopg2.connect(
        dbname=config("DATABASE_NAME"),
        user=config("DATABASE_USER"),
        password=config("DATABASE_PASSWORD"),
        host=config("DATABASE_HOST"),
        port=config("DATABASE_PORT")
    )
except Exception as e:
    print("Lỗi khi kết nối tới PostgreSQL:", e)


if connection:
    cursor = connection.cursor()
    try:
        # Tạo một bảng
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS weather_data (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                location VARCHAR(100) NOT NULL,

                temp DECIMAL(5,2),
                dwpt DECIMAL(5,2),
                rhum DECIMAL(5,2),
                wpgt DECIMAL(5,2),
                tsun INTEGER,
                wdir INTEGER,
                coco DECIMAL(5,2),
                weather VARCHAR(100)
            );
            """
        )
        connection.commit()
        
        cursor.executemany(
            """
            INSERT INTO weather_data (date, location, temp, dwpt, rhum, wpgt, tsun, wdir, coco, weather)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            [
                ('2025-04-16', 'Hanoi', 10.5, 25.3, 70.0, 35.6, 320, 180, 40.0, 'Sunny'),
                ('2025-04-15', 'Ho Chi Minh City', 20, 27.8, 75.0, 28.4, 280, 200, 30.0, 'Partly Cloudy')
            ]
        )
        connection.commit()
        print("Thêm dữ liệu thành công.")

        # Lấy dữ liệu
        cursor.execute("SELECT * FROM weather_data")
        rows = cursor.fetchall()
        df = pd.DataFrame(rows).drop([0], axis=1)
        # df = df.drop([0], axis=1)
        columns = ("date", "location", "temp", "dwpt", "rhum", "wpgt", "tsun", "wdir", "coco", "weather")
        df.columns = columns
        print(df)
        print("Dữ liệu trong bảng weather_data:")
        for row in rows:
            print(row)

        # cursor.execute("""
        #     DROP TABLE IF EXISTS weather_data;
        # """)
        # cursor.commit()
    except Exception as e:
        print("Lỗi khi thêm dữ liệu:", e)
    finally:
        # Đóng kết nối
        cursor.close()
        connection.close()
        print("Đã đóng kết nối tới PostgreSQL.")