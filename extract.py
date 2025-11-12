import os
import csv
import requests
from datetime import datetime
from prefect import flow, task
from dotenv import load_dotenv

# --- Load cấu hình ---
load_dotenv()
API_KEY = os.getenv("API_KEY")
CITIES = os.getenv("CITIES", "").split(",")

# --- Thư mục lưu CSV ---
CSV_DIR = r"D:\DW\csv"
os.makedirs(CSV_DIR, exist_ok=True)

# ------------------ TASKS ------------------

@task
def get_weather(city):
    """Lấy dữ liệu thời tiết cho 1 thành phố"""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=vi"
    try:
        res = requests.get(url, timeout=10).json()
        if "main" in res:
            return {
                "city": city,
                "temperature": res["main"].get("temp"),
                "feels_like": res["main"].get("feels_like"),
                "humidity": res["main"].get("humidity"),
                "pressure": res["main"].get("pressure"),
                "wind_speed": res.get("wind", {}).get("speed"),
                "clouds": res.get("clouds", {}).get("all"),
                "description": res.get("weather", [{}])[0].get("description"),
                "timestamp": datetime.now(),
                "record_date": datetime.now().date()
            }
        return {"city": city, "error": "Không có dữ liệu"}
    except Exception as e:
        return {"city": city, "error": str(e)}

@task
def save_csv(data):
    """Lưu dữ liệu thành CSV"""
    success_data = [d for d in data if "error" not in d]
    if not success_data:
        print("[CẢNH BÁO] Không có dữ liệu để lưu CSV")
        return None

    filename = os.path.join(CSV_DIR, f"weather_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=success_data[0].keys())
        writer.writeheader()
        writer.writerows(success_data)

    print(f"[INFO] Lưu CSV thành công: {filename}, {len(success_data)} bản ghi")
    return filename

# ------------------ FLOW ------------------

@flow
def weather_extract_flow():
    data = [get_weather(city) for city in CITIES]
    csv_file = save_csv(data)
    print(f"[INFO] Hoàn tất bước 1: CSV={csv_file}")

if __name__ == "__main__":
    weather_extract_flow()
