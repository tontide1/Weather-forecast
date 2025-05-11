import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.db import connection
import requests
from datetime import datetime

MAIL_USERNAME = 'lieutien124@gmail.com'
MAIL_PASSWORD = 'tibkmaofxfcuuwbw'

# Hàm gửi email
def send_weather_email(to_email, province, weather_info):
    # Lấy ngày đầu tiên từ dữ liệu thời tiết (nếu có)
    if weather_info:
        try:
            dt = datetime.fromisoformat(weather_info[0]['time'].replace('Z', '+00:00'))
            date_str = dt.strftime('%d/%m/%Y')
        except Exception:
            date_str = 'hôm nay'
    else:
        date_str = 'hôm nay'
    subject = f"Dự báo thời tiết ngày {date_str} cho {province}"
    body = f"""
    <h3 style='color:#2563eb;'>Dự báo thời tiết cho <b>{province}</b> ngày <b>{date_str}</b>:</h3>
    <table border='1' cellpadding='8' cellspacing='0' style='border-collapse:collapse;font-size:15px;'>
        <thead style='background:#f1f5f9;'>
            <tr>
                <th>Thời gian</th>
                <th>Nhiệt độ</th>
                <th>Lượng mưa</th>
                <th>Gió</th>
            </tr>
        </thead>
        <tbody>
    """
    for item in weather_info:
        # Định dạng lại thời gian cho đẹp
        try:
            dt = datetime.fromisoformat(item['time'].replace('Z', '+00:00'))
            time_str = dt.strftime('%H:%M %d/%m/%Y')
        except Exception:
            time_str = item['time']
        body += f"""
            <tr>
                <td>{time_str}</td>
                <td>{item['temperature']}°C</td>
                <td>{item['precipitation']} mm</td>
                <td>{item['windspeed_max']} km/h</td>
            </tr>
        """
    body += """
        </tbody>
    </table>
    <p style='color:#64748b;font-size:13px;'>Cảm ơn bạn đã sử dụng dịch vụ dự báo thời tiết!</p>
    """
    msg = MIMEMultipart()
    msg['From'] = MAIL_USERNAME
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.sendmail(MAIL_USERNAME, to_email, msg.as_string())
        print(f"Đã gửi email tới {to_email}")
    except Exception as e:
        print(f"Lỗi gửi email tới {to_email}: {e}")

# Hàm lấy danh sách subscriber từ DB
def get_all_subscribers():
    from api_app.models import Subscriber
    return Subscriber.objects.filter(is_active=True)

# Hàm lấy dữ liệu thời tiết từ API
def get_weather_data(province):
    url = f"http://127.0.0.1:8000/api/get-weather-data/?province={province}"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"Không lấy được dữ liệu thời tiết cho {province}")
            return []
    except Exception as e:
        print(f"Lỗi gọi API thời tiết: {e}")
        return []

# Hàm gửi email cho tất cả subscriber
def send_daily_weather_emails():
    print(f"[Scheduler] Bắt đầu gửi email lúc {datetime.now()}")
    for sub in get_all_subscribers():
        weather = get_weather_data(sub.province)
        if weather:
            send_weather_email(sub.email, sub.province, weather)

# Chỉ khởi tạo scheduler khi chạy server thật sự (tránh khi migrate, shell, v.v.)
def is_runserver():
    import sys
    return (len(sys.argv) > 1 and sys.argv[1] == 'runserver')

if is_runserver() and os.environ.get('RUN_MAIN', None) != 'true':
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_weather_emails, 'cron', hour=7, minute=0)
    scheduler.start()
    print('APScheduler for daily weather email started!')


