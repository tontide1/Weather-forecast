## Danh sách thành viên

- Phan Tấn Tài - 22684181
- Hoa Xuân Hoàn - 22689381
- Nguyễn Gia Lâm - 22685611
- Trương Công Đạt - 22685561

# Hệ Thống Dự Báo Thời Tiết Việt Nam

![Logo](./src/static/web_app/images/logo.png)

Hệ thống dự báo thời tiết là ứng dụng web cung cấp thông tin thời tiết chi tiết và dự báo trong 7 ngày tới cho tất cả các tỉnh thành tại Việt Nam. Dự án sử dụng dữ liệu lịch sử và mô hình Random Forest để thực hiện dự đoán.

## Tính năng

- **Thu thập dữ liệu thời tiết tự động**: Thu thập dữ liệu thời tiết hàng ngày cho 63 tỉnh thành Việt Nam
- **Dự báo thời tiết 7 ngày**: Dự báo nhiệt độ cao nhất, thấp nhất và mã thời tiết cho 7 ngày tiếp theo
- **Giao diện trực quan**: Hiển thị thông tin thời tiết dễ đọc với biểu đồ và hình ảnh
- **Tìm kiếm theo tỉnh thành**: Cho phép người dùng tìm kiếm thời tiết theo tỉnh thành
- **Thông tin chi tiết**: Hiển thị nhiệt độ, độ ẩm, lượng mưa, tốc độ gió...
- **Hỗ trợ đăng ký nhận thông báo**: Người dùng có thể đăng ký nhận thông báo về thời tiết qua email

## Kiến trúc hệ thống

Hệ thống được xây dựng với các thành phần chính:

1. **Django Backend**: Cung cấp API và xử lý logic ứng dụng
2. **Giao diện người dùng**: Frontend được xây dựng với HTML, CSS và JavaScript
3. **PostgreSQL**: Cơ sở dữ liệu lưu trữ thông tin thời tiết
4. **Apache Airflow**: Quản lý các tác vụ định kỳ (lấy dữ liệu thời tiết, xây dựng mô hình dự báo)
5. **Docker**: Đóng gói và triển khai các thành phần

## Yêu cầu hệ thống

- Docker và Docker Compose
- Git

## Cài đặt và chạy hệ thống

### 1. Clone dự án

```bash
git clone <repository-url>
cd Weather-forecast
```

### 2. Cấu hình môi trường

Tạo file `.env` trong thư mục gốc bằng cách sao chép từ file `env_example.txt` có sẵn:

Sau đó chỉnh sửa file `.env` để cập nhật các thông số cấu hình phù hợp với môi trường của bạn. Đặc biệt là cần tạo `FERNET_KEY` và `SECRET_KEY` mới.

Bạn có thể tạo Fernet key bằng cách chạy:

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 3. Khởi động hệ thống với Docker Compose

```bash
docker-compose up -d
```

Docker Compose sẽ tạo và khởi động các container:
- **web**: Ứng dụng Django chính chạy trên cổng 8000
- **db**: PostgreSQL database
- **airflow-webserver**: Airflow webserver UI chạy trên cổng 8080
- **airflow-scheduler**: Airflow scheduler
- **airflow-init**: Khởi tạo Airflow (tạo admin và database)

### 4. Truy cập ứng dụng

- **Ứng dụng dự báo thời tiết**: http://localhost:8000
- **Giao diện Airflow**: http://localhost:8080 (đăng nhập bằng tài khoản admin đã cấu hình)

## Quy trình hoạt động

1. **Thu thập dữ liệu**: Airflow DAG `Collector` thu thập dữ liệu thời tiết hiện tại và lịch sử từ API
2. **Xây dựng mô hình dự báo**: Airflow DAG `Build_XGBoost_Model` xây dựng và cập nhật mô hình dự báo
3. **Hiển thị dữ liệu**: Ứng dụng Django phục vụ API và giao diện người dùng

## Cấu trúc dự án

```
Weather-forecast/
├── airflow/              # Cấu hình và DAGs của Airflow
│   ├── dags/             # Các file định nghĩa DAG
│   │   ├── collect_weather_data_dag.py
│   │   └── RandomForest_predict_dag.py
│   ├── Dockerfile        # Docker image cho Airflow
│   └── requirements.txt  # Thư viện Python cho Airflow
├── src/                  # Mã nguồn Django
│   ├── api_app/          # API endpoint
│   ├── static/           # Tài nguyên tĩnh (CSS, JS, hình ảnh)
│   ├── templates/        # Template HTML
│   └── web_app/          # Ứng dụng web
├── src_data/             # Script thu thập dữ liệu
│   └── fetch_old_weather.py
├── test_model/           # Mô hình dự báo
│   └── randomforest_model.py
├── docker-compose.yml    # Cấu hình Docker Compose
├── Dockerfile            # Docker image cho ứng dụng Django
├── entrypoint.sh         # Script khởi động cho container Django
└── requirements.txt      # Thư viện Python cho Django
```

## API Endpoints

- `GET /api/get-weather-data/?province={province}`: Lấy dữ liệu thời tiết hiện tại cho tỉnh thành
- `GET /api/get-predict-weather-data/?province={province}`: Lấy dữ liệu dự báo cho tỉnh thành
- `GET /api/get-unique-province/`: Lấy danh sách tất cả các tỉnh thành
- `POST /api/subscribe/`: Đăng ký nhận thông báo thời tiết qua email

## Công nghệ sử dụng

- **Backend**: Django, Django REST framework
- **Frontend**: HTML, CSS, JavaScript
- **Database**: PostgreSQL
- **Task Scheduling**: Apache Airflow
- **Containerization**: Docker, Docker Compose
- **Machine Learning**: Scikit-learn (Random Forest)

## Nguồn dữ liệu

Dữ liệu thời tiết được lấy từ [Open-Meteo API](https://api.open-meteo.com/v1/forecast) và được lưu trữ trong cơ sở dữ liệu PostgreSQL.

## Tác giả

Dự án được phát triển như một công cụ giúp người dùng dễ dàng tiếp cận thông tin thời tiết chính xác cho các tỉnh thành Việt Nam, sử dụng mô hình dự báo hiện đại.
