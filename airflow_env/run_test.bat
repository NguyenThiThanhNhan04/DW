@echo off
REM ===== Kích hoạt môi trường ảo =====
call "C:\Users\Phu\Documents\DW\airflow_env\Scripts\activate.bat"

REM ===== Tạo folder logs nếu chưa có =====
if not exist "logs" mkdir logs

REM ===== Lấy timestamp =====
for /f "tokens=1-4 delims=/: " %%a in ("%date% %time%") do (
    set TIMESTAMP=%%a-%%b-%%c_%%d
)

REM ===== Chạy flow và lưu log =====
python "C:\Users\Phu\Documents\DW\weather_vn_flow.py" >> "logs\weather_%TIMESTAMP%.log" 2>&1

REM ===== Thoát môi trường ảo =====
deactivate
