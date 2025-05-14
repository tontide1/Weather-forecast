import os
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta
from sklearn.preprocessing import LabelEncoder
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
    # Đọc dữ liệu
    print("Đang đọc dữ liệu...")
    csv_filename = 'historical_weather_data.csv'
    data_file = os.path.join(DATA_DIR, csv_filename)
    if not data_file:
        raise FileNotFoundError("Không tìm thấy file dữ liệu!")
    df = pd.read_csv(data_file)

    # Kiểm tra và làm sạch dữ liệu
    print("Đang xử lý dữ liệu...")
    df['Time'] = pd.to_datetime(df['Time']).dt.normalize()
    df = df.dropna(subset=['Temp_Max', 'Temp_Min', 'Weather_Code'])
    df['Weather_Code'] = df['Weather_Code'].astype(int)

    # Định nghĩa các mã thời tiết hợp lệ và mô tả
    weather_code_descriptions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Drizzle: Light intensity",
        53: "Drizzle: Moderate intensity",
        55: "Drizzle: Dense intensity",
        56: "Freezing drizzle: Light",
        57: "Freezing drizzle: Dense",
        61: "Rain: Slight",
        63: "Rain: Moderate",
        65: "Rain: Heavy",
        66: "Freezing rain: Light",
        67: "Freezing rain: Heavy",
        71: "Snow fall: Slight",
        73: "Snow fall: Moderate",
        75: "Snow fall: Heavy",
        77: "Snow grains",
        80: "Rain showers: Slight",
        81: "Rain showers: Moderate",
        82: "Rain showers: Violent",
        85: "Snow showers: Slight",
        86: "Snow showers: Heavy",
        95: "Thunderstorm: Slight or moderate",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }

    # Thêm các đặc trưng thời gian
    df['Month'] = df['Time'].dt.month
    df['Day'] = df['Time'].dt.day
    df['DayOfYear'] = df['Time'].dt.dayofyear
    df['DayOfWeek'] = df['Time'].dt.dayofweek

    # Mã hóa tỉnh thành
    le_province = LabelEncoder()
    df['Province_Code'] = le_province.fit_transform(df['Province'])

    # Dự đoán 7 ngày tiếp theo
    last_date = df['Time'].max()
    future_dates = [last_date + timedelta(days=i+1) for i in range(7)]

    # Tạo DataFrame để lưu kết quả dự đoán
    prediction_results = pd.DataFrame()

    # Lấy danh sách các tỉnh thành
    provinces = df['Province'].unique()

    print(f"Dự báo thời tiết cho {len(provinces)} tỉnh thành...")

    for province_name in provinces:
        print(f"Đang xử lý cho tỉnh: {province_name}")
        
        # Lọc dữ liệu theo tỉnh
        province_data = df[df['Province'] == province_name].sort_values('Time')[-240:]
        
        # Kiểm tra xem có đủ dữ liệu không
        if len(province_data) < 14:  # Cần ít nhất 14 ngày để có đủ dữ liệu huấn luyện
            print(f"  Bỏ qua tỉnh {province_name}: không đủ dữ liệu")
            continue
        
        # Tạo các đặc trưng với độ trễ (lag features)
        # Tạo lag features cho nhiệt độ cao, thấp và mã thời tiết
        for lag in range(1, 8):  # Tạo lag từ 1 đến 7 ngày
            province_data[f'Temp_Max_Lag{lag}'] = province_data['Temp_Max'].shift(lag)
            province_data[f'Temp_Min_Lag{lag}'] = province_data['Temp_Min'].shift(lag)
            province_data[f'Weather_Code_Lag{lag}'] = province_data['Weather_Code'].shift(lag)
        
        # Tạo đặc trưng trung bình động (rolling mean)
        for window in [3, 5, 7]:
            province_data[f'Temp_Max_Roll{window}'] = province_data['Temp_Max'].rolling(window=window).mean()
            province_data[f'Temp_Min_Roll{window}'] = province_data['Temp_Min'].rolling(window=window).mean()
            province_data[f'Weather_Code_Roll{window}'] = province_data['Weather_Code'].rolling(window=window).mean()
        
        # Loại bỏ các hàng có giá trị NaN sau khi tạo đặc trưng
        province_data = province_data.dropna()
        
        if len(province_data) < 10:  # Kiểm tra lại sau khi đã tạo đặc trưng
            print(f"  Bỏ qua tỉnh {province_name}: không đủ dữ liệu sau khi tạo đặc trưng")
            continue
        
        # Chia tập dữ liệu
        train_data = province_data.copy()
        
        # Tạo các đặc trưng cho dự đoán
        feature_cols = [col for col in train_data.columns if col.startswith(('Temp_Max_Lag', 'Temp_Min_Lag', 
                                                                            'Weather_Code_Lag', 'Temp_Max_Roll', 
                                                                            'Temp_Min_Roll', 'Weather_Code_Roll'))]
        feature_cols += ['Month', 'Day', 'DayOfYear', 'DayOfWeek']
        
        X_train = train_data[feature_cols]
        y_temp_max = train_data['Temp_Max']
        y_temp_min = train_data['Temp_Min']
        y_weather_code = train_data['Weather_Code']
        
        # Kiểm tra mã thời tiết có trong dữ liệu của tỉnh này
        unique_weather_codes = y_weather_code.unique()
        print(f"  Mã thời tiết trong dữ liệu của {province_name}: {unique_weather_codes}")
        
        # Huấn luyện mô hình Random Forest cho nhiệt độ cao
        model_temp_max = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        model_temp_max.fit(X_train, y_temp_max)
        
        # Huấn luyện mô hình Random Forest cho nhiệt độ thấp
        model_temp_min = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        model_temp_min.fit(X_train, y_temp_min)
        
        # Huấn luyện mô hình Random Forest cho mã thời tiết
        model_weather_code = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        model_weather_code.fit(X_train, y_weather_code)
        
        # Tìm mã thời tiết gần nhất cho các dự đoán
        def find_nearest_weather_code(pred_code, valid_codes=None):
            if valid_codes is None:
                valid_codes = list(weather_code_descriptions.keys())
            
            valid_codes = np.array(valid_codes)
            idx = (np.abs(valid_codes - pred_code)).argmin()
            return valid_codes[idx]
        
        # Dự đoán cho 7 ngày tiếp theo
        future_predictions = []
        
        # Lấy dữ liệu gần nhất để dự đoán ngày đầu tiên
        last_row = province_data.iloc[-1].copy()
        
        for i in range(7):
            # Chuẩn bị dữ liệu cho ngày dự đoán
            future_date = future_dates[i]
            predict_row = pd.Series(dtype='float64')
            
            # Thêm đặc trưng thời gian
            predict_row['Month'] = future_date.month
            predict_row['Day'] = future_date.day
            predict_row['DayOfYear'] = future_date.dayofyear
            predict_row['DayOfWeek'] = future_date.dayofweek
            
            # Cập nhật lag features dựa trên dự đoán trước đó
            if i == 0:
                # Ngày đầu tiên: sử dụng dữ liệu thực tế
                for lag in range(1, 8):
                    if lag <= len(province_data):
                        predict_row[f'Temp_Max_Lag{lag}'] = province_data['Temp_Max'].iloc[-lag]
                        predict_row[f'Temp_Min_Lag{lag}'] = province_data['Temp_Min'].iloc[-lag]
                        predict_row[f'Weather_Code_Lag{lag}'] = province_data['Weather_Code'].iloc[-lag]
                    else:
                        # Nếu không đủ dữ liệu, sử dụng giá trị trung bình
                        predict_row[f'Temp_Max_Lag{lag}'] = province_data['Temp_Max'].mean()
                        predict_row[f'Temp_Min_Lag{lag}'] = province_data['Temp_Min'].mean()
                        predict_row[f'Weather_Code_Lag{lag}'] = province_data['Weather_Code'].mean()
                
                # Tính rolling mean dựa trên dữ liệu thực tế
                for window in [3, 5, 7]:
                    if window <= len(province_data):
                        predict_row[f'Temp_Max_Roll{window}'] = province_data['Temp_Max'].iloc[-window:].mean()
                        predict_row[f'Temp_Min_Roll{window}'] = province_data['Temp_Min'].iloc[-window:].mean()
                        predict_row[f'Weather_Code_Roll{window}'] = province_data['Weather_Code'].iloc[-window:].mean()
                    else:
                        predict_row[f'Temp_Max_Roll{window}'] = province_data['Temp_Max'].mean()
                        predict_row[f'Temp_Min_Roll{window}'] = province_data['Temp_Min'].mean()
                        predict_row[f'Weather_Code_Roll{window}'] = province_data['Weather_Code'].mean()
            else:
                # Từ ngày thứ 2 trở đi: cập nhật lag từ dự đoán trước đó
                for lag in range(1, 8):
                    if lag <= i:
                        # Lấy từ dự đoán trước đó
                        predict_row[f'Temp_Max_Lag{lag}'] = future_predictions[i-lag]['Temp_Max']
                        predict_row[f'Temp_Min_Lag{lag}'] = future_predictions[i-lag]['Temp_Min']
                        predict_row[f'Weather_Code_Lag{lag}'] = future_predictions[i-lag]['Weather_Code']
                    else:
                        # Lấy từ dữ liệu thực tế
                        idx = lag - i - 1
                        if idx < len(province_data):
                            predict_row[f'Temp_Max_Lag{lag}'] = province_data['Temp_Max'].iloc[-(lag-i)]
                            predict_row[f'Temp_Min_Lag{lag}'] = province_data['Temp_Min'].iloc[-(lag-i)]
                            predict_row[f'Weather_Code_Lag{lag}'] = province_data['Weather_Code'].iloc[-(lag-i)]
                        else:
                            predict_row[f'Temp_Max_Lag{lag}'] = province_data['Temp_Max'].mean()
                            predict_row[f'Temp_Min_Lag{lag}'] = province_data['Temp_Min'].mean()
                            predict_row[f'Weather_Code_Lag{lag}'] = province_data['Weather_Code'].mean()
                
                # Cập nhật rolling mean từ dự đoán trước đó
                for window in [3, 5, 7]:
                    if window <= i + 1:
                        # Có đủ dự đoán trước đó + dữ liệu thực tế
                        temp_max_vals = []
                        temp_min_vals = []
                        weather_code_vals = []
                        
                        for w in range(window):
                            if w < i:
                                temp_max_vals.append(future_predictions[i-w-1]['Temp_Max'])
                                temp_min_vals.append(future_predictions[i-w-1]['Temp_Min'])
                                weather_code_vals.append(future_predictions[i-w-1]['Weather_Code'])
                            else:
                                idx = w - i
                                if idx < len(province_data):
                                    temp_max_vals.append(province_data['Temp_Max'].iloc[-idx-1])
                                    temp_min_vals.append(province_data['Temp_Min'].iloc[-idx-1])
                                    weather_code_vals.append(province_data['Weather_Code'].iloc[-idx-1])
                                else:
                                    temp_max_vals.append(province_data['Temp_Max'].mean())
                                    temp_min_vals.append(province_data['Temp_Min'].mean())
                                    weather_code_vals.append(province_data['Weather_Code'].mean())
                        
                        predict_row[f'Temp_Max_Roll{window}'] = np.mean(temp_max_vals)
                        predict_row[f'Temp_Min_Roll{window}'] = np.mean(temp_min_vals)
                        predict_row[f'Weather_Code_Roll{window}'] = np.mean(weather_code_vals)
                    else:
                        # Không đủ dữ liệu, sử dụng trung bình
                        predict_row[f'Temp_Max_Roll{window}'] = province_data['Temp_Max'].mean()
                        predict_row[f'Temp_Min_Roll{window}'] = province_data['Temp_Min'].mean()
                        predict_row[f'Weather_Code_Roll{window}'] = province_data['Weather_Code'].mean()
            
            # Chuyển đổi Series thành DataFrame cho dự đoán
            predict_df = pd.DataFrame([predict_row])
            
            # Đảm bảo tất cả các đặc trưng đều có
            for col in feature_cols:
                if col not in predict_df.columns:
                    predict_df[col] = 0
            
            # Chỉ giữ lại các đặc trưng trong mô hình
            predict_df = predict_df[feature_cols]
            
            # Dự đoán
            temp_max_pred = model_temp_max.predict(predict_df)[0]
            temp_min_pred = model_temp_min.predict(predict_df)[0]
            weather_code_pred_raw = model_weather_code.predict(predict_df)[0]
            
            # Chuyển đổi dự đoán mã thời tiết về mã thực tế gần nhất
            weather_code_pred = find_nearest_weather_code(weather_code_pred_raw, unique_weather_codes)
            
            # Lấy mô tả thời tiết dựa trên mã
            weather_description = weather_code_descriptions.get(weather_code_pred, "Unknown")
            
            # Thêm vào danh sách dự đoán
            future_predictions.append({
                'Time': future_date,
                'Temp_Max': temp_max_pred,
                'Temp_Min': temp_min_pred,
                'Weather_Code': weather_code_pred,
                'Weather_Description': weather_description
            })
        
        # Chuyển danh sách dự đoán thành DataFrame
        province_predictions = pd.DataFrame(future_predictions)
        province_predictions['Province'] = province_name
        
        # Thêm vào kết quả tổng thể
        prediction_results = pd.concat([prediction_results, province_predictions])
        
        print(f"  ✓ Đã dự báo cho tỉnh {province_name}")

    prediction_results = prediction_results[['Province', 'Time', 'Temp_Max', 'Temp_Min', 'Weather_Code', 'Weather_Description']]
    print(prediction_results.head())
    prediction_results_tuples = list(prediction_results.itertuples(index=False, name=None))
    
    import psycopg2
    try:
        # Kết nối đến PostgreSQL
        connection = psycopg2.connect(
            database=os.environ.get("DATABASE_NAME"),
            user=os.environ.get("DATABASE_USER"),
            password=os.environ.get("DATABASE_PASSWORD"),
            host=os.environ.get("DATABASE_HOST"),
            port=os.environ.get("DATABASE_PORT"),
        )
        cursor = connection.cursor()
        
        # Tạo bảng chứa dữ liệu dự đoán
        table_name = os.environ.get("PREDICT_WEATHER_DATA_TABLE_NAME", default="predict_weather")
        cursor.execute(
            f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id SERIAL PRIMARY KEY,
                    Province VARCHAR(100) NOT NULL,
                    Time DATE NOT NULL,
                    Temp_Max DECIMAL(5,2),
                    Temp_Min DECIMAL(5,2),
                    Weather_Code INTEGER,
                    Weather_Description VARCHAR(100),
                    CONSTRAINT unique_province_time UNIQUE (Province, Time)
                );
            """
        )
        connection.commit()

        # Tạo bảng tạm để chứa dữ liệu từ CSV
        temp_table_name = table_name+"_temp"
        cursor.execute(
            f"""
            CREATE TEMPORARY TABLE {temp_table_name} (
                Province VARCHAR(100),
                Time TIMESTAMP,
                Temp_Max DECIMAL(5,2),
                Temp_Min DECIMAL(5,2),
                Weather_Code INTEGER,
                Weather_Description VARCHAR(100)
            );
            """
        )
        connection.commit()

        # Chèn dữ liệu từ CSV vào bảng tạm
        query = f"""
            INSERT INTO {temp_table_name} (
                Province, Time, Temp_Max, Temp_Min, Weather_Code, Weather_Description
            )
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(query, prediction_results_tuples)
        connection.commit()

        # Ghi dữ liệu từ bảng tạm vào bảng chính
        cursor.execute(
            f"""
            INSERT INTO {table_name} (
                Province, Time, Temp_Max, Temp_Min, Weather_Code, Weather_Description
            )
            SELECT
                Province, Time, Temp_Max, Temp_Min, Weather_Code, Weather_Description
            FROM {temp_table_name}
            ON CONFLICT ON CONSTRAINT unique_province_time
            DO UPDATE SET
                Temp_Max = EXCLUDED.Temp_Max,
                Temp_Min = EXCLUDED.Temp_Min,
                Weather_Code = EXCLUDED.Weather_Code,
                Weather_Description = EXCLUDED.Weather_Description;
            """
        )
        connection.commit()
        print("Dữ liệu dự đoán đã được thêm vào cơ sở dữ liệu thành công!")
    except Exception as e:
        connection.rollback()
        print(f"Lỗi khi ghi vào PostgreSQL: {str(e)}")
        raise
    finally:
        cursor.close()
        connection.close()

    # Tạo thư mục lưu kết quả dự đoán
    # os.makedirs(PREDICTION_DIR, exist_ok=True)

    # Xếp lại và lưu kết quả dự đoán (chỉ lưu file này)
    # prediction_results.to_csv(PREDICTION_FILE, index=False)

    print(f"\nĐã hoàn thành dự báo thời tiết cho {len(provinces)} tỉnh thành!")
    # print(f"File dự báo: {PREDICTION_FILE}")


def insert_predict_data_to_postgresql():
    pass

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
    dag_id='Build_XGBoost_Model',
    default_args=default_args,
    description="DAG dự báo thời tiết bằng XGBoost",
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