@echo off
echo Starting SecureEye Dashboard...
echo.

echo Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo.
echo Checking backend dependencies...
cd backend
python -c "import flask, flask_socketio, cv2, numpy, tensorflow" 2>nul
if %errorlevel% neq 0 (
    echo Installing backend dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Starting backend server...
start "SecureEye Backend" python app.py

echo.
echo Waiting for backend to start...
timeout /t 3 /nobreak >nul

echo.
echo Starting web server...
cd ..
python -m http.server 8000

pause
