import os
import csv
import requests
from datetime import datetime
from prefect import flow, task
from dotenv import load_dotenv

# ----------------------------------------------------
# [PHASE 1] CẤU HÌNH VÀ CHUẨN BỊ MÔI TRƯỜNG (SETUP)
# ----------------------------------------------------

# [BƯỚC 1.1] Tải cấu hình
load_dotenv() # Tải các biến môi trường từ file .env
API_KEY = os.getenv("API_KEY") # Lấy khóa API
CITIES = os.getenv("CITIES", "").split(",") # Lấy danh sách thành phố

# SỬA ĐỔI QUAN TRỌNG: SỬ DỤNG ĐƯỜNG DẪN TƯƠNG ĐỐI
# Thư mục gốc cho project: thư mục chứa file script này
# Dùng os.path.abspath(__file__) để lấy đường dẫn tuyệt đối của file script
# và os.path.dirname() để lấy thư mục chứa nó.
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) if '__file__' in locals() else os.getcwd()

# --- Thư mục lưu CSV ---
# [BƯỚC 1.2] Định nghĩa và chuẩn bị thư mục lưu file thô
# CSV_DIR sẽ là: <thư_mục_chứa_script>/csv
CSV_DIR = os.path.join(BASE_DIR, "csv")
os.makedirs(CSV_DIR, exist_ok=True) # Tạo thư mục nếu chưa tồn tại

# --- Cấu hình LOG FILE ---
# LOGS_DIR sẽ là: <thư_mục_chứa_script>/logs
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_FILE = os.path.join(LOGS_DIR, "weather_extract.log")
os.makedirs(LOGS_DIR, exist_ok=True) # Tạo thư mục logs nếu chưa tồn tại

def write_log(message):
    """[Hàm tiện ích] Ghi log ra console và file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    try:
        # Ghi vào file log
        # Sử dụng LOG_FILE đã được định nghĩa với đường dẫn tương đối/tuyệt đối
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception as e:
        print(f"[ERROR LOGGING] Không thể ghi vào file log: {e}")

# ------------------ TASKS ------------------
# Tasks là các đơn vị công việc chính trong Flow

@task
def get_weather(city):
    """
    [TASK 1: EXTRACT] Lấy dữ liệu thời tiết thô cho 1 thành phố từ OpenWeatherMap API.
    """
    # [BƯỚC 2.1] Xây dựng URL truy vấn API
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=vi"
    try:
        # [BƯỚC 2.2] Gọi API và nhận dữ liệu JSON
        res = requests.get(url, timeout=10).json()
        
        # [BƯỚC 2.3] Xử lý và trích xuất dữ liệu thành công
        if "main" in res:
            write_log(f"[SUCCESS] Đã lấy dữ liệu thời tiết cho: {city}")
            return {
                "city": city,
                "temperature": res["main"].get("temp"),
                "feels_like": res["main"].get("feels_like"),
                "humidity": res["main"].get("humidity"),
                "pressure": res["main"].get("pressure"),
                "wind_speed": res.get("wind", {}).get("speed"),
                "clouds": res.get("clouds", {}).get("all"),
                "description": res.get("weather", [{}])[0].get("description"),
                "timestamp": datetime.now(), # Ghi lại thời điểm chính xác của dữ liệu
                "record_date": datetime.now().date() # Ghi lại ngày
            }
        # Trả về lỗi nếu dữ liệu không đầy đủ
        write_log(f"[WARNING] Dữ liệu không đầy đủ cho: {city}. Phản hồi: {res.get('message', 'Không rõ')}")
        return {"city": city, "error": "Không có dữ liệu"} 
        
    except Exception as e:
        # Xử lý lỗi kết nối
        write_log(f"[FAILED] Lỗi kết nối API cho {city}: {str(e)}")
        return {"city": city, "error": str(e)}

@task
def save_csv(data):
    """
    [TASK 2: LOAD] Lưu dữ liệu thời tiết đã trích xuất thành file CSV thô.
    """
    # [BƯỚC 3.1] Lọc các bản ghi thành công (không có key "error")
    success_data = [d for d in data if "error" not in d]
    if not success_data:
        write_log("[CẢNH BÁO] Không có dữ liệu để lưu CSV")
        return None

    # [BƯỚC 3.2] Tạo tên file CSV duy nhất bằng timestamp
    # Sử dụng CSV_DIR đã được định nghĩa là đường dẫn tương đối (tuyệt đối hóa)
    filename = os.path.join(CSV_DIR, f"weather_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
    
    # [BƯỚC 3.3] Ghi dữ liệu vào file
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        # Xác định các cột (fieldnames)
        writer = csv.DictWriter(f, fieldnames=success_data[0].keys())
        writer.writeheader() # Ghi tiêu đề cột
        writer.writerows(success_data) # Ghi dữ liệu
    
    write_log(f"[INFO] Lưu CSV thành công: {filename}, {len(success_data)} bản ghi")
    return filename

# ------------------ FLOW ------------------

@flow
def weather_extract_flow():
    """
    [FLOW CHÍNH] Điều phối quá trình trích xuất dữ liệu.
    """
    write_log("[INFO] Bắt đầu flow trích xuất dữ liệu thời tiết.")
    # [BƯỚC 4.1] Thực thi Task 1: Gọi get_weather cho TẤT CẢ các thành phố (chạy song song/độc lập)
    # Lưu ý: Trong Prefect, gọi task như thế này sẽ khiến các task chạy tuần tự trừ khi có cấu hình khác.
    # Trong môi trường Prefect thực tế, `map` hoặc `submit` sẽ cần thiết cho tính song song.
    data = [get_weather(city) for city in CITIES]
    
    # [BƯỚC 4.2] Thực thi Task 2: Lưu kết quả thành CSV (phụ thuộc vào Task 1)
    csv_file = save_csv(data)
    
    write_log(f"[INFO] Hoàn tất flow: CSV={csv_file}")

if __name__ == "__main__":
    weather_extract_flow()