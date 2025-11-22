import pymysql
from pymysql import cursors
from typing import List, Tuple

# ********** THÔNG SỐ KẾT NỐI DB **********
# Vui lòng kiểm tra lại 3 tham số sau:
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '' 
DB_PORT = 3306

DW_NAME = 'weather_dw1'
MART_NAME = 'weather_mart'

# Lệnh bật/tắt kiểm tra khóa ngoại
SQL_DISABLE_FK = "SET FOREIGN_KEY_CHECKS = 0;"
SQL_ENABLE_FK = "SET FOREIGN_KEY_CHECKS = 1;"


# 1. Tải Dimension: Xóa và chèn lại toàn bộ (Full Load)
SQL_TRUNCATE_DIMS = [
    f"TRUNCATE TABLE `{MART_NAME}`.`dim_city`;",
    f"TRUNCATE TABLE `{MART_NAME}`.`dim_date`;"
]

SQL_LOAD_DIM_CITY = f"""
    INSERT INTO `{MART_NAME}`.`dim_city` (`city_id`, `city_name`)
    SELECT `city_id`, `city_name` FROM `{DW_NAME}`.`dim_city`;
"""

# *** ĐÃ SỬA LỖI #1054 Ở ĐÂY: Dùng tên cột thực tế trong Mart/DW ***
SQL_LOAD_DIM_DATE = f"""
    INSERT INTO `{MART_NAME}`.`dim_date` (
        `date_id`, `full_date`, `day_of_week_id`, `month_id`, `day_name`, 
        `month_name`, `year`, `month_year`, `day_of_month`, `day_of_year`, 
        `week_of_year`, `iso_week`, `week_start_date`, `iso_week_number`, 
        `iso_week_code`, `iso_week_start`, `quarter_name`, `quarter_id`, 
        `holiday_name`, `is_weekend`
    )
    SELECT 
        `date_id`, `full_date`, `day_of_week_id`, `month_id`, `day_name`, 
        `month_name`, `year`, `month_year`, `day_of_month`, `day_of_year`, 
        `week_of_year`, `iso_week`, `week_start_date`, `iso_week_number`, 
        `iso_week_code`, `iso_week_start`, `quarter_name`, `quarter_id`, 
        `holiday_name`, `is_weekend`
    FROM `{DW_NAME}`.`dim_date`;
"""

# 2. Tải Fact Aggregate: Tính toán và chèn (Aggregate Load)
# Các lệnh này đã được sửa lỗi month_id/month_of_year trước đó và được giữ nguyên
SQL_LOAD_FACT_DAILY = f"""
    REPLACE INTO `{MART_NAME}`.`fact_daily_weather_agg` (
      `date_id`, `city_id`, `avg_temperature`, `max_temperature`, `min_temperature`, 
      `avg_feels_like`, `max_feels_like`, `min_feels_like`, `avg_humidity`, 
      `avg_pressure`, `avg_wind_speed`, `max_wind_speed`, `total_measurements`
    )
    SELECT
      fw.date_id, fw.city_id,
      AVG(fw.temperature), MAX(fw.temperature), MIN(fw.temperature),
      AVG(fw.feels_like), MAX(fw.feels_like), MIN(fw.feels_like),
      AVG(fw.humidity), AVG(fw.pressure),
      AVG(fw.wind_speed), MAX(fw.wind_speed),
      COUNT(fw.weather_id) AS total_measurements
    FROM
      `{DW_NAME}`.`fact_weather` fw 
    GROUP BY
      fw.date_id, fw.city_id;
"""

SQL_LOAD_FACT_MONTHLY = f"""
    REPLACE INTO `{MART_NAME}`.`fact_monthly_weather_agg` (
      `weather_year`, `month_of_year`, `city_id`, `avg_temperature`, `max_temperature`, 
      `min_temperature`, `avg_feels_like`, `max_feels_like`, `min_feels_like`, 
      `avg_humidity`, `avg_pressure`, `avg_wind_speed`, `max_wind_speed`, `total_measurements`
    )
    SELECT
      dd.year AS weather_year, dd.month_id AS month_of_year, fw.city_id,
      AVG(fw.temperature), MAX(fw.temperature), MIN(fw.temperature),
      AVG(fw.feels_like), MAX(fw.feels_like), MIN(fw.feels_like),
      AVG(fw.humidity), AVG(fw.pressure),
      AVG(fw.wind_speed), MAX(fw.wind_speed),
      COUNT(fw.weather_id) AS total_measurements
    FROM
      `{DW_NAME}`.`fact_weather` fw 
    JOIN
      `{DW_NAME}`.`dim_date` dd ON fw.date_id = dd.date_id
    GROUP BY
      dd.year, dd.month_id, fw.city_id;
"""


def execute_etl_queries(queries: List[str]):
    """Thực thi danh sách các câu lệnh SQL."""
    conn = None
    try:
        conn = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            cursorclass=cursors.Cursor
        )
        
        cursor = conn.cursor()
        
        for query in queries:
            print(f"-> Executing: {query[:50]}...")
            cursor.execute(query)
            
        conn.commit()
        print("✅ Tất cả các lệnh SQL đã được thực thi và Commit thành công!")

    except Exception as e:
        print(f"❌ Lỗi trong quá trình ETL: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(SQL_ENABLE_FK)
                conn.commit()
            except Exception as e:
                pass
            conn.close()


def run_weather_mart_load():
    """Chạy toàn bộ quy trình tải dữ liệu vào Mart."""
    print("🚀 Bắt đầu quy trình tải dữ liệu từ DW sang Mart...")
    
    etl_steps = [
        # 0. Tắt kiểm tra khóa ngoại để cho phép TRUNCATE
        SQL_DISABLE_FK,
        
        # 1. Reset Dimensions
        *SQL_TRUNCATE_DIMS,
        SQL_LOAD_DIM_CITY,
        SQL_LOAD_DIM_DATE, # Đã sửa lỗi tên cột ở đây
        
        # 2. Load Facts Aggregate
        SQL_LOAD_FACT_DAILY,
        SQL_LOAD_FACT_MONTHLY,
    ]

    execute_etl_queries(etl_steps)
    print("✨ Quy trình tải Mart hoàn tất.")

if __name__ == "__main__":
    run_weather_mart_load()