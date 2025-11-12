/*
 Navicat Premium Dump SQL

 Source Server         : weather_dw
 Source Server Type    : MariaDB
 Source Server Version : 100432 (10.4.32-MariaDB)
 Source Host           : localhost:3306
 Source Schema         : weather_staging

 Target Server Type    : MariaDB
 Target Server Version : 100432 (10.4.32-MariaDB)
 File Encoding         : 65001

 Date: 11/11/2025 17:35:31
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for weather_final_c
-- ----------------------------
DROP TABLE IF EXISTS `weather_final_c`;
CREATE TABLE `weather_final_c`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `city` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `temperature` float NULL DEFAULT NULL,
  `feels_like` float NULL DEFAULT NULL,
  `humidity` int(11) NULL DEFAULT NULL,
  `pressure` int(11) NULL DEFAULT NULL,
  `wind_speed` float NULL DEFAULT NULL,
  `clouds` int(11) NULL DEFAULT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `timestamp` datetime NULL DEFAULT NULL,
  `record_date` date NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `unique_city_date`(`city`, `record_date`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 12 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of weather_final_c
-- ----------------------------
INSERT INTO `weather_final_c` VALUES (1, 'Hà Nội', 24, 24.47, 77, 1011, 2.15, 100, 'mây đen u ám', '2025-11-11 17:15:06', '2025-11-11');
INSERT INTO `weather_final_c` VALUES (2, 'Hải Phòng', 23.95, 24.44, 78, 1011, 1.03, 20, 'mây thưa', '2025-11-11 17:15:06', '2025-11-11');
INSERT INTO `weather_final_c` VALUES (3, 'Hà Giang', 20.83, 21.5, 97, 1012, 0.22, 100, 'mây đen u ám', '2025-11-11 17:15:07', '2025-11-11');
INSERT INTO `weather_final_c` VALUES (4, 'Cao Bằng', 21.61, 21.99, 83, 1012, 0.85, 100, 'mây đen u ám', '2025-11-11 17:15:08', '2025-11-11');

-- ----------------------------
-- Table structure for weather_stage
-- ----------------------------
DROP TABLE IF EXISTS `weather_stage`;
CREATE TABLE `weather_stage`  (
  `city` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `temperature` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `feels_like` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `humidity` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `pressure` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `wind_speed` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `clouds` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `timestamp` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `record_date` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of weather_stage
-- ----------------------------
INSERT INTO `weather_stage` VALUES ('Hà Nội', '24', '24.47', '77', '1011', '2.15', '100', 'mây đen u ám', '2025-11-11 17:15:06.050614', '2025-11-11');
INSERT INTO `weather_stage` VALUES ('Hải Phòng', '23.95', '24.44', '78', '1011', '1.03', '20', 'mây thưa', '2025-11-11 17:15:06.738085', '2025-11-11');
INSERT INTO `weather_stage` VALUES ('Hà Giang', '20.83', '21.5', '97', '1012', '0.22', '100', 'mây đen u ám', '2025-11-11 17:15:07.384226', '2025-11-11');
INSERT INTO `weather_stage` VALUES ('Cao Bằng', '21.61', '21.99', '83', '1012', '0.85', '100', 'mây đen u ám', '2025-11-11 17:15:08.051917', '2025-11-11');

-- ----------------------------
-- Table structure for weather_stage_a
-- ----------------------------
DROP TABLE IF EXISTS `weather_stage_a`;
CREATE TABLE `weather_stage_a`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `city` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `temperature` float NULL DEFAULT NULL,
  `feels_like` float NULL DEFAULT NULL,
  `humidity` int(11) NULL DEFAULT NULL,
  `pressure` int(11) NULL DEFAULT NULL,
  `wind_speed` float NULL DEFAULT NULL,
  `clouds` int(11) NULL DEFAULT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `timestamp` datetime NULL DEFAULT NULL,
  `record_date` date NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `unique_city_date`(`city`, `record_date`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 8 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of weather_stage_a
-- ----------------------------
INSERT INTO `weather_stage_a` VALUES (1, 'Hà Nội', 24, 24.47, 77, 1011, 2.15, 100, 'mây đen u ám', '2025-11-11 17:15:06', '2025-11-11');
INSERT INTO `weather_stage_a` VALUES (2, 'Hải Phòng', 23.95, 24.44, 78, 1011, 1.03, 20, 'mây thưa', '2025-11-11 17:15:06', '2025-11-11');
INSERT INTO `weather_stage_a` VALUES (3, 'Hà Giang', 20.83, 21.5, 97, 1012, 0.22, 100, 'mây đen u ám', '2025-11-11 17:15:07', '2025-11-11');
INSERT INTO `weather_stage_a` VALUES (4, 'Cao Bằng', 21.61, 21.99, 83, 1012, 0.85, 100, 'mây đen u ám', '2025-11-11 17:15:08', '2025-11-11');

-- ----------------------------
-- Table structure for weather_stage_b
-- ----------------------------
DROP TABLE IF EXISTS `weather_stage_b`;
CREATE TABLE `weather_stage_b`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `city` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `temperature` float NULL DEFAULT NULL,
  `feels_like` float NULL DEFAULT NULL,
  `humidity` int(11) NULL DEFAULT NULL,
  `pressure` int(11) NULL DEFAULT NULL,
  `wind_speed` float NULL DEFAULT NULL,
  `clouds` int(11) NULL DEFAULT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `timestamp` datetime NULL DEFAULT NULL,
  `record_date` date NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `unique_city_date`(`city`, `record_date`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of weather_stage_b
-- ----------------------------
INSERT INTO `weather_stage_b` VALUES (1, 'Hà Nội', 24, 24.47, 77, 1011, 2.15, 100, 'mây đen u ám', '2025-11-11 17:15:06', '2025-11-11');
INSERT INTO `weather_stage_b` VALUES (2, 'Hải Phòng', 23.95, 24.44, 78, 1011, 1.03, 20, 'mây thưa', '2025-11-11 17:15:06', '2025-11-11');
INSERT INTO `weather_stage_b` VALUES (3, 'Hà Giang', 20.83, 21.5, 97, 1012, 0.22, 100, 'mây đen u ám', '2025-11-11 17:15:07', '2025-11-11');
INSERT INTO `weather_stage_b` VALUES (4, 'Cao Bằng', 21.61, 21.99, 83, 1012, 0.85, 100, 'mây đen u ám', '2025-11-11 17:15:08', '2025-11-11');

-- ----------------------------
-- Table structure for weather_stage_logs
-- ----------------------------
DROP TABLE IF EXISTS `weather_stage_logs`;
CREATE TABLE `weather_stage_logs`  (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `city` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `status` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `csv_file` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL DEFAULT NULL,
  `timestamp` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 5 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of weather_stage_logs
-- ----------------------------
INSERT INTO `weather_stage_logs` VALUES (1, 'Hà Nội', 'SUCCESS', 'C:\\Users\\Phu\\Documents\\DW\\csv\\weather_20251111_171508.csv', '2025-11-11 17:29:52');
INSERT INTO `weather_stage_logs` VALUES (2, 'Hải Phòng', 'SUCCESS', 'C:\\Users\\Phu\\Documents\\DW\\csv\\weather_20251111_171508.csv', '2025-11-11 17:29:52');
INSERT INTO `weather_stage_logs` VALUES (3, 'Hà Giang', 'SUCCESS', 'C:\\Users\\Phu\\Documents\\DW\\csv\\weather_20251111_171508.csv', '2025-11-11 17:29:52');
INSERT INTO `weather_stage_logs` VALUES (4, 'Cao Bằng', 'SUCCESS', 'C:\\Users\\Phu\\Documents\\DW\\csv\\weather_20251111_171508.csv', '2025-11-11 17:29:52');

-- ----------------------------
-- Procedure structure for sp_stage_to_fact_keep_AB
-- ----------------------------
DROP PROCEDURE IF EXISTS `sp_stage_to_fact_keep_AB`;
delimiter ;;
CREATE PROCEDURE `sp_stage_to_fact_keep_AB`()
BEGIN
    DECLARE rows_in_A INT DEFAULT 0;
    DECLARE rows_in_B INT DEFAULT 0;
    DECLARE rows_in_fact INT DEFAULT 0;

    -- 1️⃣ Xóa dữ liệu tạm cũ trước khi nạp mới
    TRUNCATE TABLE weather_stage_A;
    TRUNCATE TABLE weather_stage_B;

    -- 2️⃣ Lấy dữ liệu từ weather_stage vào stage_A
    INSERT INTO weather_stage_A (city, temperature, feels_like, humidity, pressure, wind_speed, clouds, description, timestamp, record_date)
    SELECT city, temperature, feels_like, humidity, pressure, wind_speed, clouds, description, timestamp, record_date
    FROM weather_dw.weather_stage;

    SELECT COUNT(*) INTO rows_in_A FROM weather_stage_A;

    -- 3️⃣ Copy từ A sang B
    INSERT INTO weather_stage_B SELECT * FROM weather_stage_A;
    SELECT COUNT(*) INTO rows_in_B FROM weather_stage_B;

    -- 4️⃣ Chèn/Update vào Fact table (weather_final_C)
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

    -- 5️⃣ Đếm tổng số bản ghi trong Fact table
    SELECT COUNT(*) INTO rows_in_fact FROM weather_final_C;

    -- 6️⃣ Hiển thị log
    SELECT CONCAT('Số bản ghi trong stage_A (tạm): ', rows_in_A) AS log_info;
    SELECT CONCAT('Số bản ghi trong stage_B (tạm): ', rows_in_B) AS log_info;
    SELECT CONCAT('Tổng số bản ghi hiện tại trong Fact table: ', rows_in_fact) AS log_info;

    -- ✅ LƯU Ý: Không xóa dữ liệu tạm trong A/B, để bạn xem dữ liệu lần chạy gần nhất
END
;;
delimiter ;

-- ----------------------------
-- Procedure structure for sp_stage_to_final
-- ----------------------------
DROP PROCEDURE IF EXISTS `sp_stage_to_final`;
delimiter ;;
CREATE PROCEDURE `sp_stage_to_final`()
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
    FROM weather_dw.weather_stage;

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
END
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
