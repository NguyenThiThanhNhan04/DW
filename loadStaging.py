import os
import csv
import pymysql
from datetime import datetime
from prefect import flow, task

# --- Cấu hình MySQL ---
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "weather_staging",
    "charset": "utf8mb4"
}

# --- File log console + file ---
LOG_FILE = r"D:\DW\logs\weather_stage.log"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def write_log(message):
    """Ghi log ra console và file"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

# --- Task load CSV vào bảng stage ---
@task
def load_csv_to_stage(csv_file):
    """Load CSV lên bảng stage giữ nguyên dữ liệu thô và log vào SQL"""
    if not os.path.exists(csv_file):
        write_log(f"[ERROR] File CSV không tồn tại: {csv_file}")
        return

    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        data = [row for row in reader]

    conn = pymysql.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Tạo bảng stage
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

    # Xóa dữ liệu cũ
    cur.execute("TRUNCATE TABLE weather_stage")

    # Insert dữ liệu thô
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

    write_log(f"[INFO] Đã load {len(rows)} bản ghi lên bảng weather_stage từ file {csv_file}")

    # --- Tạo bảng log nếu chưa có ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS weather_stage_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            city VARCHAR(100),
            status VARCHAR(50),
            csv_file VARCHAR(255),
            timestamp DATETIME
        )
    """)

    # --- Ghi log từng bản ghi ---
    for d in data:
        city = d.get("city")
        status = "SUCCESS" if d.get("temperature") else "FAILED: không có dữ liệu"
        cur.execute("""
            INSERT INTO weather_stage_logs (city, status, csv_file, timestamp)
            VALUES (%s,%s,%s,NOW())
        """, (city, status, csv_file))

    conn.commit()
    cur.close()
    conn.close()
    write_log(f"[INFO] Đã ghi log {len(data)} bản ghi vào weather_stage_logs")

# --- Flow chính ---
@flow
def weather_stage_flow(csv_file=None):
    # Nếu không truyền CSV, tự lấy file mới nhất
    if not csv_file:
        csv_dir = r"D:\DW\csv"
        files = [os.path.join(csv_dir, f) for f in os.listdir(csv_dir) if f.endswith(".csv")]
        if not files:
            write_log("[ERROR] Không tìm thấy file CSV nào")
            return
        csv_file = max(files, key=os.path.getctime)

    load_csv_to_stage(csv_file)
    write_log("[INFO] Hoàn tất load dữ liệu thô vào weather_stage")

# --- Run ---
if __name__ == "__main__":
    weather_stage_flow()
