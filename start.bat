@echo off
REM Addis Care Kepler - One-Command Startup Script for Windows
REM This script clones the repository and runs the application automatically

echo 🏥 Addis Care: Medicaid Crisis Analysis
echo ======================================
echo 🚀 One-Command Setup ^& Launch
echo ======================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher and try again
    pause
    exit /b 1
)

REM Check if git is installed
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Git is not installed or not in PATH
    echo Please install Git and try again
    pause
    exit /b 1
)

REM Clone repository if it doesn't exist
if not exist "addis-care-kepler" (
    echo 📥 Cloning repository...
    git clone https://github.com/nolansingroy/addis-care-kepler.git
    if errorlevel 1 (
        echo ❌ Failed to clone repository
        pause
        exit /b 1
    )
)

REM Change to repository directory
cd addis-care-kepler

REM Run the Python setup script
echo 🚀 Starting automated setup...
python run.py

echo ✅ Setup complete!
pause
