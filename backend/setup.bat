@echo off
echo Setting up SecureEye AI Backend...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo Creating directories...
if not exist models mkdir models
if not exist logs mkdir logs
if not exist data mkdir data

REM Copy environment template
echo Setting up environment file...
if not exist .env (
    copy env_template.txt .env
    echo Created .env file from template
) else (
    echo .env file already exists
)

echo.
echo Backend setup complete!
echo.
echo IMPORTANT: Please configure your .env file with Firebase credentials:
echo 1. Go to Firebase Console: https://console.firebase.google.com
echo 2. Select your project: eye-61167
echo 3. Go to Project Settings > Service Accounts
echo 4. Generate a new private key
echo 5. Update the .env file with your credentials
echo.
echo To run the backend:
echo 1. Activate virtual environment: venv\Scripts\activate.bat
echo 2. Run: python app.py
echo.
pause
