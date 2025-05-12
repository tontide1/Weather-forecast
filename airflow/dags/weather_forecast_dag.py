import os
import csv
import json
import logging
import requests
import psycopg2
from datetime import datetime, date, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from dotenv import load_dotenv

load_dotenv()

# Cấu hình logging
logger = logging.getLogger(__name__)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,  # Tăng số lần retry
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

def process_province_data(province, today_iso, end_date_iso):
    """
    Xử lý dữ liệu thời tiết cho một tỉnh.
    Được thiết kế để chạy song song với ThreadPoolExecutor.
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": province["lat"],
        "longitude": province["lon"],
        "hourly": "temperature_2m,precipitation,windspeed_10m,uv_index,weathercode,sunshine_duration,relativehumidity_2m,apparent_temperature",
        "timezone": "Asia/Bangkok",
        "start_date": today_iso,
        "end_date": end_date_iso
    }

    province_results = []
    
    try:
        response = requests.get(url, params=params, timeout=10)  # Thêm timeout để tránh treo
        if response.status_code == 200:
            data = response.json().get("hourly", {})
            times = data.get("time", [])
            
            # Kiểm tra nếu không có dữ liệu time thì bỏ qua tỉnh này
            if not times:
                logger.warning(f"⚠️ {province['name']}: không có dữ liệu 'time' từ API, bỏ qua.")
                return province_results

            # Lấy các dữ liệu thời tiết
            temps = data.get("temperature_2m", [])
            precs = data.get("precipitation", [])
            winds = data.get("windspeed_10m", [])
            uvs = data.get("uv_index", [])
            weathercodes = data.get("weathercode", [])
            sunshines = data.get("sunshine_duration", [0]*len(times))
            humidity = data.get("relativehumidity_2m", [])
            feel_like = data.get("apparent_temperature", [])

            # Xây dựng chỉ mục theo ngày
            day_indices = {}
            for idx, t in enumerate(times):
                day = t.split("T")[0]
                if day not in day_indices:
                    day_indices[day] = []
                day_indices[day].append(idx)

            # Xử lý dữ liệu mỗi 3 giờ
            for i, t in enumerate(times):
                hour = int(t.split("T")[1][:2])
                if hour % 3 != 0:
                    continue
                
                day = t.split("T")[0]
                indices = day_indices.get(day, [])
                if not indices:
                    continue
                
                # Tính toán các giá trị thống kê theo ngày
                valid_temp_indices = [j for j in indices if j < len(temps)]
                valid_wind_indices = [j for j in indices if j < len(winds)]
                valid_uv_indices = [j for j in indices if j < len(uvs)]
                
                temp_max = max([temps[j] for j in valid_temp_indices]) if valid_temp_indices else None
                temp_min = min([temps[j] for j in valid_temp_indices]) if valid_temp_indices else None
                wind_max = max([winds[j] for j in valid_wind_indices]) if valid_wind_indices else None
                uv_max = max([uvs[j] for j in valid_uv_indices]) if valid_uv_indices else None
                
                # Tính số giờ nắng và đêm
                valid_sunshine_indices = [j for j in indices if j < len(sunshines) and 6 <= int(times[j].split("T")[1][:2]) < 18]
                sunshine_hours = sum([sunshines[j] for j in valid_sunshine_indices]) / 3600 if valid_sunshine_indices else 0
                
                valid_time_indices = [j for j in indices if j < len(times)]
                sundown_hours = len([j for j in valid_time_indices if int(times[j].split("T")[1][:2]) < 6 or int(times[j].split("T")[1][:2]) >= 18])
                
                # Đảm bảo index i không vượt quá độ dài của các list
                current_temp = temps[i] if i < len(temps) else None
                current_prec = precs[i] if i < len(precs) else None
                current_weathercode = weathercodes[i] if i < len(weathercodes) else None
                current_humidity = humidity[i] if i < len(humidity) else None
                current_feel_like = feel_like[i] if i < len(feel_like) else None

                # Thêm vào danh sách kết quả
                province_results.append([
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
                ])
            
            logger.info(f"✅ {province['name']}: xong - {len(province_results)} bản ghi")
            return province_results
        else:
            logger.error(f"❌ {province['name']}: lỗi API - Status {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"❌ {province['name']}: lỗi xử lý - {str(e)}")
        return []

def fetch_weather_data(**context):
    today = date.today()
    today_iso = today.isoformat()
    end_date = today + timedelta(days=2)
    end_date_iso = end_date.isoformat()
    
    # Tạo thư mục nếu chưa tồn tại
    data_dir = "/opt/airflow/weather_data"
    os.makedirs(data_dir, exist_ok=True)
    
    csv_file = f"{data_dir}/{today_iso}_{end_date_iso}.csv"
    header = [
        "Province", "Time", "Temperature", "Temp_Max", "Temp_Min", 
        "Precipitation", "Windspeed_Max", "UV_Index_Max", "Sunshine_Hours", 
        "Sundown_Hours", "Weather_Code", "Humidity", "Feel_Like"
    ]
    
    logger.info(f"🔄 Bắt đầu thu thập dữ liệu thời tiết cho {len(provinces)} tỉnh/thành từ {today_iso} đến {end_date_iso}")
    
    # Sử dụng ThreadPoolExecutor để thu thập dữ liệu song song
    all_results = []
    max_workers = min(10, len(provinces))  # Tối đa 10 threads để tránh quá tải
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Tạo các future tasks
        future_to_province = {
            executor.submit(process_province_data, province, today_iso, end_date_iso): province["name"]
            for province in provinces
        }
        
        # Lấy kết quả khi các task hoàn thành
        for future in as_completed(future_to_province):
            province_name = future_to_province[future]
            try:
                province_results = future.result()
                all_results.extend(province_results)
            except Exception as e:
                logger.error(f"❌ Lỗi khi xử lý dữ liệu của {province_name}: {str(e)}")
    
    # Ghi dữ liệu vào file CSV
    with open(csv_file, mode="w", newline='', encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(all_results)
    
    # Thống kê kết quả
    province_counts = {}
    for row in all_results:
        province_name = row[0]
        if province_name in province_counts:
            province_counts[province_name] += 1
        else:
            province_counts[province_name] = 1
    
    # Hiển thị thống kê
    logger.info(f"\n📊 THỐNG KÊ KẾT QUẢ:")
    logger.info(f"✅ Tổng số bản ghi: {len(all_results)}")
    logger.info(f"✅ Số tỉnh/thành có dữ liệu: {len(province_counts)}")
    logger.info(f"📄 Đã lưu vào file: {csv_file}")
    
    return csv_file

def import_to_database(**context):
    ti = context['ti']
    csv_file_path = ti.xcom_pull(task_ids='fetch_weather_data')
    
    if not csv_file_path or not os.path.exists(csv_file_path):
        logger.error(f"❌ Không tìm thấy file CSV: {csv_file_path}. Bỏ qua import.")
        return False

    # Xác định khoảng thời gian dữ liệu
    start_date_for_delete = date.today()
    end_date_for_delete = start_date_for_delete + timedelta(days=2)
    
    connection = None
    try:
        # Kết nối đến database
        db_host = os.environ.get("DATABASE_HOST", "host.docker.internal")
        db_config = {
            "dbname": os.environ.get("DATABASE_NAME"),
            "user": os.environ.get("DATABASE_USER"),
            "password": os.environ.get("DATABASE_PASSWORD"),
            "host": db_host,
            "port": os.environ.get("DATABASE_PORT")
        }
        
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        table_name = os.environ.get("WEATHER_DATA_TABLE_NAME", "weather_data")

        logger.info(f"🔄 Bắt đầu nhập dữ liệu từ {csv_file_path} vào bảng {table_name}...")
        
        # Xóa dữ liệu cũ trong khoảng thời gian
        delete_start_timestamp = datetime.combine(start_date_for_delete, datetime.min.time())
        delete_end_timestamp = datetime.combine(end_date_for_delete, datetime.max.time())

        logger.info(f"🗑️ Xóa dữ liệu cũ trong khoảng: {delete_start_timestamp} đến {delete_end_timestamp}")
        cursor.execute(
            f"DELETE FROM {table_name} WHERE time >= %s AND time <= %s",
            (delete_start_timestamp, delete_end_timestamp)
        )
        
        # Đếm số bản ghi trước khi import
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        records_before = cursor.fetchone()[0]
        
        # Import dữ liệu mới bằng COPY
        with open(csv_file_path, mode="r", encoding="utf-8-sig") as file_obj:
            next(file_obj)  # Bỏ qua header
            copy_sql = f"""
                COPY {table_name} (
                    province, time, temperature, temp_max, temp_min, precipitation,
                    windspeed_max, uv_index_max, sunshine_hours, sundown_hours,
                    weather_code, humidity, feel_like
                )
                FROM STDIN
                WITH (FORMAT CSV, HEADER FALSE);
            """
            cursor.copy_expert(sql=copy_sql, file=file_obj)
        
        # Đếm số bản ghi sau khi import
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        records_after = cursor.fetchone()[0]
        records_added = records_after - records_before
        
        connection.commit()
        logger.info(f"✅ Import thành công! Đã thêm {records_added} bản ghi vào database.")
        
        # Lưu thông tin để task kiểm tra có thể sử dụng
        context['ti'].xcom_push(key='import_success', value=True)
        context['ti'].xcom_push(key='date_range', value={
            'start_date': delete_start_timestamp.isoformat(),
            'end_date': delete_end_timestamp.isoformat(),
            'table_name': table_name,
            'records_added': records_added
        })
        
        return True

    except Exception as e:
        logger.error(f"❌ Lỗi khi nhập dữ liệu vào database: {str(e)}")
        if connection:
            connection.rollback()
        context['ti'].xcom_push(key='import_success', value=False)
        context['ti'].xcom_push(key='import_error', value=str(e))
        return False
        
    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.info("ℹ️ Đã đóng kết nối tới PostgreSQL.")

def verify_import(**context):
    ti = context['ti']
    import_success = ti.xcom_pull(key='import_success', task_ids='import_to_database')
    date_range = ti.xcom_pull(key='date_range', task_ids='import_to_database')
    
    if not import_success:
        error_msg = ti.xcom_pull(key='import_error', task_ids='import_to_database') or "Lỗi không xác định"
        logger.error(f"❌ Import dữ liệu thất bại: {error_msg}")
        return False
    
    connection = None
    try:
        # Kết nối database để kiểm tra
        db_host = os.environ.get("DATABASE_HOST", "host.docker.internal")
        db_config = {
            "dbname": os.environ.get("DATABASE_NAME"),
            "user": os.environ.get("DATABASE_USER"),
            "password": os.environ.get("DATABASE_PASSWORD"),
            "host": db_host,
            "port": os.environ.get("DATABASE_PORT")
        }
        
        connection = psycopg2.connect(**db_config)
        cursor = connection.cursor()
        
        table_name = date_range['table_name']
        start_date = date_range['start_date']
        end_date = date_range['end_date']
        
        # Kiểm tra tổng số bản ghi và số tỉnh/thành
        cursor.execute(
            f"""
            SELECT COUNT(*), COUNT(DISTINCT province)
            FROM {table_name}
            WHERE time >= %s AND time <= %s
            """,
            (start_date, end_date)
        )
        total_records, province_count = cursor.fetchone()
        
        # Kiểm tra phạm vi thời gian
        cursor.execute(
            f"""
            SELECT MIN(time), MAX(time)
            FROM {table_name}
            WHERE time >= %s AND time <= %s
            """,
            (start_date, end_date)
        )
        earliest, latest = cursor.fetchone()
        
        # Thống kê theo tỉnh/thành
        cursor.execute(
            f"""
            SELECT province, COUNT(*)
            FROM {table_name}
            WHERE time >= %s AND time <= %s
            GROUP BY province
            ORDER BY COUNT(*) DESC
            """,
            (start_date, end_date)
        )
        province_stats = cursor.fetchall()
        
        # Hiển thị kết quả kiểm tra
        logger.info("\n====== 📊 KẾT QUẢ KIỂM TRA DỮ LIỆU ======")
        logger.info(f"✅ Tổng số bản ghi: {total_records}")
        logger.info(f"✅ Số tỉnh/thành: {province_count}")
        
        if earliest and latest:
            logger.info(f"✅ Thời gian bản ghi đầu tiên: {earliest}")
            logger.info(f"✅ Thời gian bản ghi cuối cùng: {latest}")
            logger.info(f"✅ Tổng thời gian dữ liệu: {(latest - earliest).days} ngày, {(latest - earliest).seconds // 3600} giờ")
        
        # Hiển thị thống kê theo tỉnh
        logger.info("\n------ Chi tiết theo tỉnh/thành ------")
        for i, (province, count) in enumerate(province_stats[:10]):
            logger.info(f"{i+1}. {province}: {count} bản ghi")
        
        if len(province_stats) > 10:
            logger.info(f"... và {len(province_stats) - 10} tỉnh/thành khác")
        
        # Lưu báo cáo chi tiết
        report = {
            'total_records': total_records,
            'province_count': province_count,
            'earliest': earliest.isoformat() if earliest else None,
            'latest': latest.isoformat() if latest else None,
            'provinces': [{'name': p, 'record_count': c} for p, c in province_stats],
            'import_time': datetime.now().isoformat(),
            'date_range': {
                'start': start_date,
                'end': end_date
            }
        }
        
        # Lưu báo cáo vào file
        report_file = os.path.join(
            os.path.dirname(context['ti'].xcom_pull(task_ids='fetch_weather_data')),
            f"import_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n📄 Đã lưu báo cáo chi tiết vào file: {report_file}")
        
        # Xác nhận thành công
        expected_provinces = len(provinces)
        if total_records > 0 and province_count >= expected_provinces * 0.9:  # Nếu có ít nhất 90% tỉnh có dữ liệu
            logger.info("\n✅ THÀNH CÔNG: Dữ liệu đã được import đầy đủ vào database!")
            return True
        elif total_records > 0:
            logger.warning(f"\n⚠️ CHÚ Ý: Dữ liệu đã được import nhưng chỉ có {province_count}/{expected_provinces} tỉnh/thành!")
            return True
        else:
            logger.error("\n❌ THẤT BẠI: Không có bản ghi nào được import vào database!")
            return False
            
    except Exception as e:
        logger.error(f"❌ Lỗi khi kiểm tra dữ liệu: {str(e)}")
        return False
    finally:
        if connection:
            cursor.close()
            connection.close()
            logger.info("ℹ️ Đã đóng kết nối tới PostgreSQL.")

with DAG(
    dag_id='weather_forecast_dag', 
    default_args=default_args,
    description='Thu thập và lưu trữ dữ liệu dự báo thời tiết cho 63 tỉnh thành Việt Nam',
    schedule_interval=timedelta(days=1),  # Cập nhật hàng ngày thay vì 3 ngày
    start_date=days_ago(1),
    catchup=False,
    tags=['weather', 'forecast', 'vietnam'],
) as dag:

    fetch_task = PythonOperator(
        task_id='fetch_weather_data',
        python_callable=fetch_weather_data,
    )

    import_task = PythonOperator(
        task_id='import_to_database',
        python_callable=import_to_database,
    )
    
    verify_task = PythonOperator(
        task_id='verify_import',
        python_callable=verify_import,
    )

    # Thiết lập phụ thuộc giữa các task
    fetch_task >> import_task >> verify_task