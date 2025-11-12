-- --DROP PROCEDURE IF EXISTS sp_stage_to_final;--

DELIMITER //

CREATE PROCEDURE sp_stage_to_final()
BEGIN
    DECLARE rows_in_A INT DEFAULT 0;
    DECLARE rows_in_B INT DEFAULT 0;
    DECLARE rows_inserted INT DEFAULT 0;

    -- Xóa dữ liệu tạm trong A và B trước khi nạp mới
    TRUNCATE TABLE weather_stage_A;
    TRUNCATE TABLE weather_stage_B;

    -- Bước 1: Lấy dữ liệu mới từ weather_dw.weather_stage vào A
    INSERT INTO weather_stage_A (city, temperature, feels_like, humidity, pressure, wind_speed, clouds, description, timestamp, record_date)
    SELECT city, temperature, feels_like, humidity, pressure, wind_speed, clouds, description, timestamp, record_date
    FROM weather_staging.weather_stage;

    -- Đếm số bản ghi trong A
    SELECT COUNT(*) INTO rows_in_A FROM weather_stage_A;

    -- Bước 2: Copy từ A sang B
    INSERT INTO weather_stage_B SELECT * FROM weather_stage_A;

    -- Đếm số bản ghi trong B
    SELECT COUNT(*) INTO rows_in_B FROM weather_stage_B;

    -- Bước 3: Chèn/Update dữ liệu sang final_C (Fact table)
    INSERT INTO weather_final_C (city, temperature, feels_like, humidity, pressure, wind_speed, clouds, description, timestamp, record_date)
    SELECT b.city, b.temperature, b.feels_like, b.humidity, b.pressure, b.wind_speed, b.clouds, b.description, b.timestamp, b.record_date
    FROM weather_stage_B b
    ON DUPLICATE KEY UPDATE
        temperature = VALUES(temperature),
        feels_like = VALUES(feels_like),
        humidity = VALUES(humidity),
        pressure = VALUES(pressure),
        wind_speed = VALUES(wind_speed),
        clouds = VALUES(clouds),
        description = VALUES(description),
        timestamp = VALUES(timestamp);

    -- Đếm tổng số bản ghi hiện tại trong final_C
    SELECT COUNT(*) INTO rows_inserted FROM weather_final_C;

    -- Hiển thị log
    SELECT CONCAT('Số bản ghi trong stage_A (tạm): ', rows_in_A) AS log_info;
    SELECT CONCAT('Số bản ghi trong stage_B (tạm): ', rows_in_B) AS log_info;
    SELECT CONCAT('Tổng số bản ghi hiện tại trong weather_final_C (Fact table): ', rows_inserted) AS log_info;

    -- ✅ LƯU Ý: Không xóa dữ liệu tạm trong A/B, để xem dữ liệu lần chạy gần nhất
END //

DELIMITER ;
