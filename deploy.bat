@echo off
REM Boehm Tech TaskMaster Deployment Script for Windows
REM This script sets up and runs the TaskMaster application

echo 🚀 Boehm Tech TaskMaster Deployment Script
echo ==========================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.11 or higher.
    pause
    exit /b 1
)

echo ✅ Python is installed

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Create necessary directories
echo 📁 Creating directories...
if not exist "src\static\uploads" mkdir src\static\uploads
if not exist "src\database" mkdir src\database

echo.
echo ✅ Setup complete!
echo.
echo 🎯 Default Admin Credentials:
echo    Username: admin
echo    Password: admin123
echo.
echo 🌐 Starting the application...
echo    Access it at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

REM Start the application
python src\main.py

pause

