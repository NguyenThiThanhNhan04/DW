import os
import csv
import pymysql
from datetime import datetime
from prefect import flow, task
from pathlib import Path # Import thư viện pathlib để quản lý đường dẫn

# --- Cấu hình MySQL ---
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "", # Hãy cân nhắc sử dụng biến môi trường cho mật khẩu
    "database": "weather_staging",
    "charset": "utf8mb4"
}

# --- Định nghĩa các đường dẫn tương đối ---
# Lấy thư mục gốc của script hiện tại (giả sử script này nằm trong thư mục DW)
# Ví dụ: Nếu script nằm ở C:\Users\Phu\Documents\DW\etl_script.py
# PROJECT_ROOT sẽ là C:\Users\Phu\Documents\DW
PROJECT_ROOT = Path(__file__).resolve().parent

# Đường dẫn đến file log: DW/logs/weather_stage.log
LOG_FILE = PROJECT_ROOT / "logs" / "weather_stage.log"
os.makedirs(LOG_FILE.parent, exist_ok=True) # Tạo thư mục logs nếu chưa có

# Đường dẫn đến thư mục chứa CSV: DW/csv
CSV_DIR = PROJECT_ROOT / "csv"

def write_log(message):
    """Ghi log ra console và file"""
    # Đảm bảo thư mục logs đã được tạo
    os.makedirs(LOG_FILE.parent, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    # Sử dụng LOG_FILE đã được định nghĩa bằng Path
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# --- Task load CSV vào bảng stage (giữ nguyên logic) ---
@task
def load_csv_to_stage(csv_file):
    """Load CSV lên bảng stage giữ nguyên dữ liệu thô và log vào SQL"""
    # Chuyển Path object thành string để os.path.exists xử lý
    csv_file_str = str(csv_file) 
    
    if not os.path.exists(csv_file_str):
        write_log(f"[ERROR] File CSV không tồn tại: {csv_file_str}")
        return

    # Mở file CSV bằng đường dẫn đã chuẩn hóa
    with open(csv_file_str, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]

    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Tạo bảng stage (giữ nguyên)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather_stage (
            city TEXT,
            temperature TEXT,
            feels_like TEXT,
            humidity TEXT,
            pressure TEXT,
            wind_speed TEXT,
            clouds TEXT,
            description TEXT,
            timestamp TEXT,
            record_date TEXT
        )
    """)

    # Xóa dữ liệu cũ (giữ nguyên)
    cur.execute("TRUNCATE TABLE weather_stage")

    # Insert dữ liệu thô (giữ nguyên)
    sql = """
    INSERT INTO weather_stage
    (city, temperature, feels_like, humidity, pressure, wind_speed, clouds, description, timestamp, record_date)
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    rows = [(d.get("city"), d.get("temperature"), d.get("feels_like"), d.get("humidity"),
             d.get("pressure"), d.get("wind_speed"), d.get("clouds"), d.get("description"),
             d.get("timestamp"), d.get("record_date")) for d in data]

    cur.executemany(sql, rows)
    conn.commit()

    write_log(f"[INFO] Đã load {len(rows)} bản ghi lên bảng weather_stage từ file {csv_file_str}")

    # --- Tạo bảng log nếu chưa có (giữ nguyên) ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather_stage_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            city VARCHAR(100),
            status VARCHAR(50),
            csv_file VARCHAR(255),
            timestamp DATETIME,
            activity_type VARCHAR(50) NOT NULL DEFAULT 'LOAD'
        )
    """)

    # --- Ghi log từng bản ghi (giữ nguyên) ---
    for d in data:
        city = d.get("city")
        status = "SUCCESS" if d.get("temperature") else "FAILED: không có dữ liệu"
        # Chú ý: Sử dụng tên file CSV_FILE_STR (đường dẫn tuyệt đối) để log, giúp dễ tra cứu
        cur.execute("""
            INSERT INTO weather_stage_logs (city, status, csv_file, timestamp, activity_type)
            VALUES (%s,%s,%s,NOW(), %s)
        """, (city, status, csv_file_str, 'LOAD'))

    conn.commit()
    cur.close()
    conn.close()
    write_log(f"[INFO] Đã ghi log {len(data)} bản ghi vào weather_stage_logs")

# --- Flow chính ---
@flow
def weather_stage_flow(csv_file=None):
    # Nếu không truyền CSV, tự lấy file mới nhất
    if not csv_file:
        # Sử dụng CSV_DIR đã định nghĩa
        files = [f for f in CSV_DIR.iterdir() if f.is_file() and f.suffix == ".csv"] 
        
        if not files:
            write_log("[ERROR] Không tìm thấy file CSV nào")
            return
        # Tìm file mới nhất dựa trên thời gian tạo
        csv_file_path = max(files, key=os.path.getctime)
    else:
        # Nếu có truyền vào, đảm bảo nó là Path object
        csv_file_path = Path(csv_file)

    load_csv_to_stage(csv_file_path) # Truyền Path object vào task
    write_log("[INFO] Hoàn tất load dữ liệu thô vào weather_stage")

# --- Run ---
if __name__ == "__main__":
    weather_stage_flow()