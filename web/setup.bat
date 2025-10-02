@echo off
echo ==========================================
echo    TSUNAMI ALERT WEB DASHBOARD SETUP
echo ==========================================
echo.

echo [INFO] Setting up Tsunami Alert Web Dashboard...
echo.

:: Check if Python is installed
echo [1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8 or newer from https://python.org
    echo Make sure to add Python to PATH during installation
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [OK] Python %PYTHON_VERSION% found

:: Check if pip is available
echo.
echo [2/6] Checking pip installation...
pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip not found!
    echo Please install pip or reinstall Python with pip included
    pause
    exit /b 1
)
echo [OK] pip is available

:: Upgrade pip
echo.
echo [3/6] Upgrading pip...
python -m pip install --upgrade pip
echo [OK] pip upgraded

:: Install requirements
echo.
echo [4/6] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install some dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)
echo [OK] All dependencies installed successfully

:: Create necessary directories
echo.
echo [5/6] Creating necessary directories...
if not exist "uploads" mkdir uploads
if not exist "logs" mkdir logs
if not exist "backups" mkdir backups
echo [OK] Directories created

:: Create sample .env file if it doesn't exist
echo.
echo [6/6] Setting up configuration...
if not exist ".env" (
    echo Creating sample .env file...
    (
        echo # TSUNAMI ALERT DASHBOARD CONFIGURATION
        echo.
        echo # RTSP Stream Configuration
        echo RTSP_URL=
        echo CAMERA_LOCATION=
        echo.
        echo # CSV Data Path
        echo OMBAK_CSV_PATH=deteksi_ombak.csv
        echo.
        echo # WhatsApp Configuration ^(Optional^)
        echo TWILIO_ACCOUNT_SID=
        echo TWILIO_AUTH_TOKEN=
        echo WHATSAPP_FROM=whatsapp:+14155238886
        echo WHATSAPP_TO=whatsapp:+62812345678
        echo.
        echo # SMS Configuration ^(Optional^)
        echo SMS_FROM=+14155238886
        echo SMS_TO=+62812345678
        echo.
        echo # Detection Thresholds ^(pixels^)
        echo GARIS_EXTREME_Y=180
        echo GARIS_SANGAT_TINGGI_Y=210
        echo GARIS_TINGGI_Y=230
        echo GARIS_SEDANG_Y=250
        echo GARIS_RENDAH_Y=280
    ) > .env
    echo [OK] Sample .env file created
    echo [INFO] Please edit .env file with your actual configuration
) else (
    echo [OK] .env file already exists
)

echo.
echo ==========================================
echo         SETUP COMPLETED SUCCESSFULLY!
echo ==========================================
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Run start.bat to launch the dashboard
echo 3. Open http://localhost:5000 in your browser
echo.
echo For RTSP stream testing, you can use:
echo - IP Camera RTSP URL
echo - rtsp://192.168.1.100:554/stream
echo - Local webcam: use webcam index (0, 1, 2, etc.)
echo.
echo For WhatsApp/SMS alerts:
echo - Sign up for Twilio account at https://twilio.com
echo - Get your Account SID and Auth Token
echo - Configure WhatsApp Sandbox or SMS service
echo.
echo Documentation: README.md
echo Support: Check the README.md file for troubleshooting
echo.
pause