@echo off
REM Holehe Web Interface Setup Script for Windows
REM This script creates a virtual environment and installs dependencies

echo ========================================
echo     Holehe Web Interface Setup (Windows)
echo ========================================

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.7 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set python_version=%%i
echo Python version detected: %python_version%

REM Create virtual environment
echo Creating virtual environment...
if exist venv (
    echo Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)

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

REM Create templates directory
echo Creating templates directory...
if not exist templates mkdir templates

echo.
echo ========================================
echo     Setup completed successfully!
echo ========================================
echo.
echo To start the Holehe web interface:
echo 1. Activate the virtual environment:
echo    venv\Scripts\activate.bat
echo.
echo 2. Run the application:
echo    python app.py
echo.
echo 3. Open your browser and go to:
echo    http://localhost:5001
echo.
echo To deactivate the virtual environment later:
echo    deactivate
echo.
pause