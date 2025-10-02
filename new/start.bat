# start.bat - Script untuk menjalankan aplikasi web deteksi ombak
@echo off
echo ================================================
echo    SISTEM MONITORING DETEKSI OMBAK - WEB APP
echo ================================================
echo.

echo Mengaktifkan virtual environment...
call venv\Scripts\activate

echo.
echo Memulai aplikasi web...
echo Aplikasi akan berjalan di: http://localhost:5000
echo.
echo Tekan Ctrl+C untuk menghentikan aplikasi
echo.

python app.py

pause