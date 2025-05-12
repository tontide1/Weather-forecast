import os
import csv
import requests
import psycopg2
from datetime import datetime, date, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago # Được sử dụng cho start_date
from dotenv import load_dotenv

load_dotenv()

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

provinces = [
    {"name": "An Giang", "lat": 10.521, "lon": 105.125},
    {"name": "Bà Rịa - Vũng Tàu", "lat": 10.541, "lon": 107.242},
    {"name": "Bạc Liêu", "lat": 9.294, "lon": 105.724},
    {"name": "Bắc Giang", "lat": 21.273, "lon": 106.194},
    {"name": "Bắc Kạn", "lat": 22.147, "lon": 105.834},
    {"name": "Bắc Ninh", "lat": 21.186, "lon": 106.076},
    {"name": "Bến Tre", "lat": 10.243, "lon": 106.375},
    {"name": "Bình Dương", "lat": 11.325, "lon": 106.477},
    {"name": "Bình Định", "lat": 14.166, "lon": 108.902},
    {"name": "Bình Phước", "lat": 11.751, "lon": 106.723},
    {"name": "Bình Thuận", "lat": 11.090, "lon": 108.072},
    {"name": "Cà Mau", "lat": 9.176, "lon": 105.152},
    {"name": "Cao Bằng", "lat": 22.665, "lon": 106.257},
    {"name": "Cần Thơ", "lat": 10.045, "lon": 105.746},
    {"name": "Đà Nẵng", "lat": 16.047, "lon": 108.206},
    {"name": "Đắk Lắk", "lat": 12.710, "lon": 108.237},
    {"name": "Đắk Nông", "lat": 12.264, "lon": 107.609},
    {"name": "Điện Biên", "lat": 21.383, "lon": 103.016},
    {"name": "Đồng Nai", "lat": 10.948, "lon": 106.824},
    {"name": "Đồng Tháp", "lat": 10.535, "lon": 105.636},
    {"name": "Gia Lai", "lat": 13.807, "lon": 108.109},
    {"name": "Hà Giang", "lat": 22.750, "lon": 104.983},
    {"name": "Hà Nam", "lat": 20.583, "lon": 105.922},
    {"name": "Hà Nội", "lat": 21.028, "lon": 105.854},
    {"name": "Hà Tĩnh", "lat": 18.342, "lon": 105.905},
    {"name": "Hải Dương", "lat": 20.938, "lon": 106.330},
    {"name": "Hải Phòng", "lat": 20.844, "lon": 106.688},
    {"name": "Hậu Giang", "lat": 9.757, "lon": 105.641},
    {"name": "Hòa Bình", "lat": 20.817, "lon": 105.337},
    {"name": "Hưng Yên", "lat": 20.646, "lon": 106.051},
    {"name": "Khánh Hòa", "lat": 12.259, "lon": 109.196},
    {"name": "Kiên Giang", "lat": 10.012, "lon": 105.080},
    {"name": "Kon Tum", "lat": 14.349, "lon": 108.000},
    {"name": "Lai Châu", "lat": 22.396, "lon": 103.458},
    {"name": "Lâm Đồng", "lat": 11.575, "lon": 108.142},
    {"name": "Lạng Sơn", "lat": 21.853, "lon": 106.761},
    {"name": "Lào Cai", "lat": 22.485, "lon": 103.970},
    {"name": "Long An", "lat": 10.543, "lon": 106.411},
    {"name": "Nam Định", "lat": 20.438, "lon": 106.162},
    {"name": "Nghệ An", "lat": 19.234, "lon": 104.920},
    {"name": "Ninh Bình", "lat": 20.250, "lon": 105.974},
    {"name": "Ninh Thuận", "lat": 11.564, "lon": 108.988},
    {"name": "Phú Thọ", "lat": 21.345, "lon": 105.254},
    {"name": "Phú Yên", "lat": 13.088, "lon": 109.092},
    {"name": "Quảng Bình", "lat": 17.468, "lon": 106.622},
    {"name": "Quảng Nam", "lat": 15.539, "lon": 108.019},
    {"name": "Quảng Ngãi", "lat": 15.120, "lon": 108.800},
    {"name": "Quảng Ninh", "lat": 21.006, "lon": 107.292},
    {"name": "Quảng Trị", "lat": 16.744, "lon": 107.189},
    {"name": "Sóc Trăng", "lat": 9.602, "lon": 105.973},
    {"name": "Sơn La", "lat": 21.325, "lon": 103.918},
    {"name": "Tây Ninh", "lat": 11.365, "lon": 106.098},
    {"name": "Thái Bình", "lat": 20.446, "lon": 106.342},
    {"name": "Thái Nguyên", "lat": 21.594, "lon": 105.848},
    {"name": "Thanh Hóa", "lat": 19.807, "lon": 105.776},
    {"name": "Thừa Thiên Huế", "lat": 16.463, "lon": 107.590},
    {"name": "Tiền Giang", "lat": 10.449, "lon": 106.342},
    {"name": "TP Hồ Chí Minh", "lat": 10.776, "lon": 106.700},
    {"name": "Trà Vinh", "lat": 9.812, "lon": 106.299},
    {"name": "Tuyên Quang", "lat": 21.823, "lon": 105.218},
    {"name": "Vĩnh Long", "lat": 10.253, "lon": 105.973},
    {"name": "Vĩnh Phúc", "lat": 21.308, "lon": 105.604},
    {"name": "Yên Bái", "lat": 21.705, "lon": 104.870}
]

def fetch_weather_data(**context):
    today = date.today()
    today_iso = today.isoformat()
    end_date = today + timedelta(days=2)
    
    os.makedirs("/opt/airflow/weather_data", exist_ok=True)
    
    csv_file = f"/opt/airflow/weather_data/{today_iso}_{end_date.isoformat()}.csv"
    header = ["Province", "Time", "Temperature", "Temp_Max", "Temp_Min", "Precipitation", "Windspeed_Max", "UV_Index_Max", "Sunshine_Hours", "Sundown_Hours", "Weather_Code", "Humidity", "Feel_Like"]
    
    with open(csv_file, mode="w", newline='', encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for province in provinces:
            url = "https://api.open-meteo.com/v1/forecast"
            params = {
                "latitude": province["lat"],
                "longitude": province["lon"],
                "hourly": "temperature_2m,precipitation,windspeed_10m,uv_index,weathercode,sunshine_duration,relativehumidity_2m,apparent_temperature",
                "timezone": "Asia/Bangkok",
                "start_date": today_iso,
                "end_date": end_date.isoformat()
            }

            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json().get("hourly", {})
                times = data.get("time", []) # Thêm .get để tránh lỗi nếu key không tồn tại
                temps = data.get("temperature_2m", [])
                precs = data.get("precipitation", [])
                winds = data.get("windspeed_10m", [])
                uvs = data.get("uv_index", [])
                weathercodes = data.get("weathercode", [])
                sunshines = data.get("sunshine_duration", [0]*len(times))
                humidity = data.get("relativehumidity_2m", [])
                feel_like = data.get("apparent_temperature", [])

                # Kiểm tra nếu không có dữ liệu time thì bỏ qua tỉnh này
                if not times:
                    print(f"⚠️ {province['name']}: không có dữ liệu 'time' từ API, bỏ qua.")
                    continue

                day_indices = {}
                for idx, t in enumerate(times):
                    day = t.split("T")[0]
                    if day not in day_indices:
                        day_indices[day] = []
                    day_indices[day].append(idx)

                for i, t in enumerate(times):
                    hour = int(t.split("T")[1][:2])
                    if hour % 3 != 0:
                        continue
                    day = t.split("T")[0]
                    indices = day_indices.get(day, []) # Thêm .get để tránh lỗi nếu key không tồn tại
                    if not indices: # Nếu không có indices cho ngày đó thì bỏ qua
                        continue
                        
                    temp_max = max([temps[j] for j in indices if j < len(temps)])
                    temp_min = min([temps[j] for j in indices if j < len(temps)])
                    wind_max = max([winds[j] for j in indices if j < len(winds)])
                    uv_max = max([uvs[j] for j in indices if j < len(uvs)])
                    sunshine_hours = sum([sunshines[j] for j in indices if j < len(sunshines) and 6 <= int(times[j].split("T")[1][:2]) < 18]) / 3600
                    sundown_hours = len([j for j in indices if j < len(times) and (int(times[j].split("T")[1][:2]) < 6 or int(times[j].split("T")[1][:2]) >= 18)])
                    
                    # Đảm bảo index i không vượt quá độ dài của các list
                    current_temp = temps[i] if i < len(temps) else None
                    current_prec = precs[i] if i < len(precs) else None
                    current_weathercode = weathercodes[i] if i < len(weathercodes) else None
                    current_humidity = humidity[i] if i < len(humidity) else None
                    current_feel_like = feel_like[i] if i < len(feel_like) else None

                    row = [
                        province["name"],
                        t,
                        current_temp,
                        temp_max,
                        temp_min,
                        current_prec,
                        wind_max,
                        uv_max,
                        round(sunshine_hours, 2),
                        sundown_hours,
                        current_weathercode,
                        current_humidity,
                        current_feel_like
                    ]
                    writer.writerow(row)
                print(f"✅ {province['name']}: xong")
            else:
                print(f"❌ {province['name']}: lỗi API - Status {response.status_code}")

    print(f"\n📄 Đã lưu vào file: {csv_file}")
    return csv_file

def import_to_database(**context):
    ti = context['ti']
    csv_file_path = ti.xcom_pull(task_ids='fetch_weather_data')
    
    if not csv_file_path or not os.path.exists(csv_file_path):
        print(f"❌ Không tìm thấy file CSV: {csv_file_path}. Bỏ qua import.")
        return

    today = date.today() # Dùng ngày hiện tại khi task chạy để xác định khoảng dữ liệu
    start_of_data_period_iso = os.path.basename(csv_file_path).split('_')[0]
    end_of_data_period_iso = os.path.basename(csv_file_path).split('_')[1].replace(".csv", "")
    
    # Chuyển đổi ngày từ tên file về datetime.date để dùng trong query
    try:
        # start_date_for_delete = datetime.strptime(start_of_data_period_iso, '%Y-%m-%d').date()
        # end_date_for_delete = datetime.strptime(end_of_data_period_iso, '%Y-%m-%d').date()
        
        # Dùng ngày hôm nay và 2 ngày tới, tương ứng với logic cào dữ liệu
        start_date_for_delete = date.today()
        end_date_for_delete = start_date_for_delete + timedelta(days=2)


    except ValueError as e:
        print(f"❌ Lỗi chuyển đổi ngày từ tên file: {e}. Sử dụng ngày mặc định.")
        start_date_for_delete = date.today()
        end_date_for_delete = start_date_for_delete + timedelta(days=2)


    connection = None
    try:
        connection = psycopg2.connect(
            dbname=os.environ.get("DATABASE_NAME"),
            user=os.environ.get("DATABASE_USER"),
            password=os.environ.get("DATABASE_PASSWORD"),
            host=os.environ.get("DATABASE_HOST"),
            port=os.environ.get("DATABASE_PORT")
        )
        
        cursor = connection.cursor()
        table_name = os.environ.get("WEATHER_DATA_TABLE_NAME", "weather_data")

        print(f"Bắt đầu nhập dữ liệu từ {csv_file_path} vào bảng {table_name}...")
        
        with open(csv_file_path, mode="r", encoding="utf-8-sig") as file_obj:
            next(file_obj)
            
            # Xóa dữ liệu cũ trong khoảng thời gian mới để tránh trùng lặp
            # Dữ liệu 'Time' trong DB là timestamp, cần đảm bảo so sánh đúng kiểu
            # Ví dụ: Time >= '2023-01-01 00:00:00' AND Time <= '2023-01-03 23:59:59'
            delete_start_timestamp = datetime.combine(start_date_for_delete, datetime.min.time())
            delete_end_timestamp = datetime.combine(end_date_for_delete, datetime.max.time())

            print(f"Xóa dữ liệu cũ trong khoảng: {delete_start_timestamp} đến {delete_end_timestamp}")
            
            cursor.execute(
                f"""
                DELETE FROM {table_name}
                WHERE "Time" >= %s AND "Time" <= %s
                """,
                (delete_start_timestamp, delete_end_timestamp)
            )
            
            # COPY dữ liệu mới
            copy_sql = f"""
                COPY {table_name} (
                    "Province", "Time", "Temperature", "Temp_Max", "Temp_Min", "Precipitation", 
                    "Windspeed_Max", "UV_Index_Max", "Sunshine_Hours", "Sundown_Hours", 
                    "Weather_Code", "Humidity", "Feel_Like"
                )
                FROM STDIN
                WITH (FORMAT CSV, HEADER FALSE);
            """
            cursor.copy_expert(sql=copy_sql, file=file_obj)
            
        connection.commit()
        print("✅ Dữ liệu từ file CSV đã được nhập vào cơ sở dữ liệu thành công!")

    except Exception as e:
        print(f"❌ Lỗi khi nhập dữ liệu vào database: {e}")
        if connection:
            connection.rollback()
    finally:
        if connection:
            cursor.close()
            connection.close()
            print("ℹ️ Đã đóng kết nối tới PostgreSQL.")

with DAG(
    dag_id='weather_forecast_dag', 
    default_args=default_args,
    description='Cào dữ liệu thời tiết từ API mỗi 3 ngày và lưu vào database',
    schedule_interval=timedelta(days=3),
    start_date=days_ago(1), # Bắt đầu tính từ ngày hôm qua lúc 00:00
    catchup=False,
    tags=['weather'],
) as dag:

    fetch_task = PythonOperator(
        task_id='fetch_weather_data',
        python_callable=fetch_weather_data,
        # provide_context=True,
    )

    import_task = PythonOperator(
        task_id='import_to_database',
        python_callable=import_to_database,
        # provide_context=True, 
    )

    fetch_task >> import_task