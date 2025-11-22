import pandas as pd
import pymysql
from pymysql import Error
import os
import glob
import sys 

# 🛠️ CẤU HÌNH KẾT NỐI CHÍNH (Dành cho Data Warehouse - Fact/Dims)
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "weather_dw1", # Database chính: weather_dw1
    "charset": "utf8mb4"
}

# 🛠️ CẤU HÌNH KẾT NỐI LOG (Dành cho bảng Log trong weather_staging)
LOG_DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "weather_staging", # Database Log: weather_staging <--- ĐÍCH GHI LOG
    "charset": "utf8mb4"
}

print("Starting ETL process for fact_weather...")

connection = None
cursor = None
log_conn = None 

# Khởi tạo biến để sử dụng trong khối except/finally
load_status = 'N/A'
log_message = 'Chưa hoàn tất'
rows_processed = 0
latest_file_name = 'N/A' 

try:
    # 1. Kết nối database chính (weather_dw1)
    print("Attempting to connect to database using PyMySQL...")
    connection = pymysql.connect(**DB_CONFIG) 
    cursor = connection.cursor() 
    print("Database connected successfully.")

    # --- PHASE E (EXTRACT) & T (TRANSFORM) ---
    
    # [BƯỚC 1] Kết nối DB & Lấy Dims
    print("[BƯỚC 1] Loading dimensions from DB...")
    cursor.execute("SELECT date_id, full_date FROM dim_date")
    result_date = cursor.fetchall()
    df_dim_date = pd.DataFrame(result_date, columns=['date_id', 'full_date'])
    
    cursor.execute("SELECT city_id, city_name FROM dim_city")
    result_city = cursor.fetchall()
    df_dim_city = pd.DataFrame(result_city, columns=['city_id', 'city_name'])

    # [BƯỚC 2] Transform Dims (Date to String)
    df_dim_date['full_date'] = df_dim_date['full_date'].astype(str)
    print("[BƯỚC 2] Đã chuẩn hóa dim_date sang String.")

    # [BƯỚC 3] Tìm File CSV Mới Nhất
    script_dir = r"C:\Users\Phu\Documents\DW\csv\export"
    search_pattern = os.path.join(script_dir, 'weather_final_c_*.csv')
    list_of_files = glob.glob(search_pattern)
    
    if not list_of_files:
        raise FileNotFoundError(f"Không tìm thấy file CSV nào khớp với mẫu: {search_pattern}")
    
    latest_file = max(list_of_files, key=os.path.getctime)
    latest_file_name = os.path.basename(latest_file)
    print(f"[BƯỚC 3] Đang đọc file mới nhất: {latest_file_name}")
    
    # [BƯỚC 4] Read CSV & Parse Date
    df_staging = pd.read_csv(latest_file, quotechar='"')
    
    temp_date_series = pd.to_datetime(df_staging['record_date'], format='mixed', dayfirst=True)
    df_staging['join_date_str'] = temp_date_series.dt.strftime('%Y-%m-%d')
    df_staging['timestamp_dt'] = pd.to_datetime(df_staging['timestamp'], format='mixed', dayfirst=True)
    print("[BƯỚC 4] Đã đọc và parse ngày tháng từ CSV.")

    # [BƯỚC 5-7.5] MERGE, Validation, Type Casting & Constraint Check
    print("[BƯỚC 5] Performing dimension lookups (merging)...")
    
    df_merged = pd.merge(df_staging, df_dim_date, left_on='join_date_str', right_on='full_date', how='left')
    df_final = pd.merge(df_merged, df_dim_city, left_on='city', right_on='city_name', how='left')

    failed_lookups = df_final[df_final['date_id'].isnull() | df_final['city_id'].isnull()]
    if not failed_lookups.empty:
        print(f"Warning: Có {len(failed_lookups)} dòng lỗi lookup (sẽ bỏ qua).")
    
    df_fact = df_final.dropna(subset=['date_id', 'city_id']).copy()
    print(f"[BƯỚC 6] Đã lọc dữ liệu. Số dòng hợp lệ: {len(df_fact)}")

    numeric_cols = ['temperature', 'feels_like', 'humidity', 'pressure', 'wind_speed', 'clouds']
    for col in numeric_cols:
        df_fact[col] = pd.to_numeric(df_fact[col], errors='coerce')
    
    df_fact['date_id'] = df_fact['date_id'].astype(int)
    df_fact['city_id'] = df_fact['city_id'].astype(int)
    print("[BƯỚC 7] Đã ép kiểu dữ liệu (Numeric/Int).")

    print("[BƯỚC 7.5] Kiểm tra unique constraint trên (date_id, city_id, timestamp)...")
    try:
        cursor.execute("SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS WHERE TABLE_SCHEMA = 'weather_dw1' AND TABLE_NAME = 'fact_weather' AND CONSTRAINT_NAME = 'unique_date_city'")
        old_constraint = cursor.fetchone()[0]
        if old_constraint > 0:
            print("   🔧 Xóa constraint cũ 'unique_date_city'...")
            cursor.execute("ALTER TABLE fact_weather DROP INDEX unique_date_city")
            connection.commit()
        
        cursor.execute("SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS WHERE TABLE_SCHEMA = 'weather_dw1' AND TABLE_NAME = 'fact_weather' AND CONSTRAINT_NAME = 'unique_date_city_time'")
        new_constraint = cursor.fetchone()[0]
        if new_constraint == 0:
            print("   ⚠️ Chưa có unique constraint mới, đang tạo...")
            cursor.execute("ALTER TABLE fact_weather ADD CONSTRAINT unique_date_city_time UNIQUE (date_id, city_id, timestamp)")
            connection.commit()
            print("   ✅ Đã tạo constraint 'unique_date_city_time' thành công!")
        else:
            print("   ✓ Đã có constraint 'unique_date_city_time'.")
    except Exception as e:
        print(f"   ⚠️ Lỗi khi tạo constraint: {e}")

    columns_to_load = ['date_id', 'city_id', 'temperature', 'feels_like', 'humidity', 'pressure', 'wind_speed', 'clouds', 'description', 'timestamp_dt']
    df_load = df_fact[columns_to_load]

    # --- PHASE L (LOAD) ---

    if len(df_load) == 0:
        log_message = f"Không có dữ liệu mới để thêm vào. File: {latest_file_name}"
        load_status = "WARNING"
        print("[BƯỚC 8] ⚠️ Không có dữ liệu để thêm vào. Bỏ qua bước INSERT.")
    else:
        print(f"[BƯỚC 8] Preparing to INSERT/UPDATE {len(df_load)} rows...")

        data_tuples = [tuple(x) for x in df_load.values]

        insert_query = """
        INSERT INTO fact_weather (date_id, city_id, temperature, feels_like, humidity, pressure, wind_speed, clouds, description, timestamp) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            temperature = VALUES(temperature),
            feels_like = VALUES(feels_like),
            humidity = VALUES(humidity),
            pressure = VALUES(pressure),
            wind_speed = VALUES(wind_speed),
            clouds = VALUES(clouds),
            description = VALUES(description)
        """
        
        cursor.executemany(insert_query, data_tuples)
        connection.commit()
        rows_processed = cursor.rowcount 

        load_status = "SUCCESS"
        log_message = f"Hoàn tất ETL. Đã xử lý {rows_processed} dòng từ {latest_file_name}."

        print(f"--- Load Complete ---")
        print(f"✅ Successfully processed {rows_processed} rows.")
        print(f"💡 Dữ liệu mới (date_id, city_id, timestamp khác) được thêm vào.")
        print(f"💡 Dữ liệu trùng (cùng date_id, city_id, timestamp) được cập nhật.")
    
except Error as e:
    log_message = f"Lỗi Database: {e}. File: {latest_file_name}"
    load_status = "FAILED"
    print(f"❌ FATAL ERROR (PyMySQL): {e}")
    if connection:
        connection.rollback()
    
except FileNotFoundError as e:
    log_message = f"Lỗi File: {e}"
    load_status = "FAILED"
    print(f"❌ LỖI FILE: {e}")

except Exception as e:
    log_message = f"Lỗi không xác định: {e}. File: {latest_file_name}"
    load_status = "FAILED"
    print(f"❌ LỖI KHÔNG XÁC ĐỊNH: {e}")
    if connection:
        connection.rollback()

finally:
    # ⚠️ GHI LOG VÀO DB (SỬ DỤNG KẾT NỐI RIÊNG ĐẾN weather_staging)
    if connection: 
        try:
            # 1. Mở kết nối đến DB Log (weather_staging)
            log_conn = pymysql.connect(**LOG_DB_CONFIG) # <--- ĐÃ SỬ DỤNG LOG_DB_CONFIG
            log_cursor = log_conn.cursor()
            
            # 2. Đảm bảo bảng log tồn tại (trong weather_staging)
            log_cursor.execute("""
                CREATE TABLE IF NOT EXISTS weather_stage_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    city VARCHAR(100),
                    status VARCHAR(50),
                    csv_file VARCHAR(255),
                    timestamp DATETIME,
                    activity_type VARCHAR(50) NOT NULL DEFAULT 'LOAD'
                )
            """)
            
            # 3. Ghi bản ghi log cuối cùng
            log_cursor.execute("""
                INSERT INTO weather_stage_logs (city, status, csv_file, timestamp, activity_type)
                VALUES (%s, %s, %s, NOW(), %s)
            """, ('ALL_CITIES_ETL', load_status, log_message, 'Load2_DW'))
            log_conn.commit()
            
        except Exception as log_err:
             print(f"❌ LỖI GHI LOG VÀO DB WEATHER_STAGING: {log_err}")
        finally:
            if log_conn and log_conn.open:
                log_conn.close()
    
    # Đóng kết nối chính
    if connection and connection.open:
        if cursor:
            cursor.close()
        connection.close()
        print("\n🔒 ETL process finished. Database connection closed.")