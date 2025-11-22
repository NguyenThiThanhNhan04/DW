import os
import pymysql
import pandas as pd
from datetime import datetime

# --- Cấu hình MySQL (Sử dụng cấu hình hiện tại của bạn) ---
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "",
    "database": "weather_staging", # Thay thế nếu bảng C ở DB khác
    "charset": "utf8mb4"
}

def export_final_to_csv():
    """Trích xuất dữ liệu từ weather_final_C và lưu về máy tính cá nhân."""
    
    conn = None
    try:
        # 1. Định nghĩa thư mục và tên file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = r"C:\Users\Phu\Documents\DW\csv\export" # Thư mục lưu file trên máy tính cá nhân
        os.makedirs(output_dir, exist_ok=True)
        
        file_name = f"weather_final_c_{timestamp}.csv"
        output_path = os.path.join(output_dir, file_name)
        
        print(f"[INFO] Bắt đầu xuất dữ liệu sang: {output_path}")

        # 2. Câu lệnh SQL SELECT
        SQL_QUERY = """
        SELECT 
            id, city, temperature, feels_like, humidity, pressure, wind_speed, 
            clouds, description, timestamp, record_date
        FROM 
            weather_final_C;
        """
        
        # 3. Kết nối và tải dữ liệu bằng Pandas
        conn = pymysql.connect(**DB_CONFIG)
        
        # Tải dữ liệu vào DataFrame
        df = pd.read_sql(SQL_QUERY, conn)
        
        # 4. Lưu DataFrame thành file CSV
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO weather_stage_logs (city, status, csv_file, timestamp, activity_type)
            VALUES (%s, %s, %s, NOW(), %s)
        """, ('ALL_CITIES', f'SUCCESS ({len(df)} rows)', output_path, 'EXPORT'))
        
        conn.commit()
        
        print(f"✅ Xuất dữ liệu thành công {len(df)} bản ghi.")
        print(f"File đã lưu về máy cá nhân tại: {output_path}")

    except pymysql.Error as err:
        print(f"❌ [ERROR] Lỗi Database trong quá trình xuất: {err}")
        # Thử ghi log lỗi vào DB nếu kết nối đã thành công
        if conn and conn.open:
             cur = conn.cursor()
             cur.execute("""
                 INSERT INTO weather_stage_logs (city, status, csv_file, timestamp, activity_type)
                 VALUES (%s, %s, %s, NOW(), %s)
             """, ('N/A', f'FAILED: {err}', output_path or 'N/A', 'EXPORT'))
             conn.commit()
    except Exception as e:
        print(f"❌ Đã xảy ra lỗi: {e}")
    finally:
        if conn and conn.open:
            conn.close()

# --- Run Script ---
if __name__ == "__main__":
    export_final_to_csv()