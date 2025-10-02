# setup.bat - Script setup awal untuk aplikasi web
@echo off
echo ================================================
echo    SETUP SISTEM MONITORING DETEKSI OMBAK
echo ================================================
echo.

echo Membuat virtual environment...
python -m venv venv

echo.
echo Mengaktifkan virtual environment...
call venv\Scripts\activate

echo.
echo Menginstall dependencies...
pip install -r requirements_web.txt

echo.
echo ================================================
echo Setup selesai!
echo.
echo Untuk menjalankan aplikasi:
echo 1. Jalankan start.bat
echo 2. Atau aktifkan venv dan jalankan: python app.py
echo 3. Buka browser ke: http://localhost:5000
echo.
echo CATATAN PENTING:
echo - Pastikan URL RTSP/HTTP kamera sudah benar
echo - Sesuaikan parameter garis deteksi sesuai view kamera
echo - Aplikasi akan berjalan headless (tanpa window OpenCV)
echo ================================================

pause