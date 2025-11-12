@echo off
chcp 65001 >nul

echo ===============================
echo 🚀 BẮT ĐẦU CHẠY FLOW THỜI TIẾT
echo ===============================

REM --- Di chuyển đến thư mục dự án ---
cd /d "C:\Users\Phu\Documents\DW"

REM --- Kiểm tra file Python có tồn tại không ---
if not exist "weather_vn_flow.py" (
    echo ❌ Không tìm thấy file weather_vn_flow.py
    pause
    exit /b
)

REM --- Kích hoạt môi trường ảo ---
if exist "airflow_env\Scripts\activate.bat" (
    call "airflow_env\Scripts\activate.bat"
) else (
    echo ❌ Không tìm thấy môi trường airflow_env
    pause
    exit /b
)

REM --- Tạo thư mục logs nếu chưa có ---
if not exist "logs" mkdir logs

REM --- Lấy timestamp ---
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set DATE=%%c-%%a-%%b
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set TIME=%%a-%%b
set TIMESTAMP=%DATE%_%TIME%

echo.
echo 🔄 Đang chạy file Python...
echo.

REM --- Chạy script Python và lưu log ---
python weather_vn_flow.py >> "logs\weather_%TIMESTAMP%.log" 2>&1

if %errorlevel% neq 0 (
    echo ❌ ĐÃ XẢY RA LỖI KHI CHẠY PYTHON!
) else (
    echo ✅ HOÀN TẤT THÀNH CÔNG!
)

echo.
echo ===============================
echo 📄 Log được lưu tại: logs\weather_%TIMESTAMP%.log
echo ===============================
pause
