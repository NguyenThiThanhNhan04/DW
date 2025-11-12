                  +--------------------+
                  |    CSV nguồn       |
                  | weather_xxx.csv    |
                  +---------+----------+
                            |
                            v
                  +--------------------+
                  |  weather_stage     |  <- Python load CSV
                  +---------+----------+
                            |
                            | CALL sp_stage_to_final()
                            v
                  +--------------------+
                  |  weather_stage_A   |  <- dữ liệu tạm, giữ lần chạy gần nhất
                  +---------+----------+
                            |
                            v
                  +--------------------+
                  |  weather_stage_B   |  <- dữ liệu tạm, copy từ A
                  +---------+----------+
                            |
                            v
                  +--------------------+
                  |  weather_final_C   |  <- Fact table
                  |  (city, record_date, temperature, ...)  |
                  +--------------------+
