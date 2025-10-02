@echo off
echo ==========================================
echo    TSUNAMI ALERT WEB DASHBOARD
echo ==========================================
echo.

echo [1/4] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
echo ✓ Python found

echo.
echo [2/4] Installing/updating dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✓ Dependencies installed

echo.
echo [3/4] Checking required modules...
python -c "import cv2, flask, numpy, pandas" 2>nul
if errorlevel 1 (
    echo ERROR: Some required modules are missing
    echo Please run: pip install -r requirements.txt
    pause
    exit /b 1
)
echo ✓ Required modules available

echo.
echo [4/4] Starting web application...
echo.
echo ==========================================
echo  Dashboard akan tersedia di:
echo  http://localhost:5000
echo ==========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause