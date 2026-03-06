@echo off
title YouTube One-Time Authentication Setup
color 0B

echo.
echo ╔══════════════════════════════════════════════════════╗
echo ║   YOUTUBE ONE-TIME SETUP (Do This Just ONCE!)       ║
echo ╚══════════════════════════════════════════════════════╝
echo.
echo This will:
echo  1. Install needed packages
echo  2. Open browser for YouTube login
echo  3. Create your auth token file
echo  4. Show you what to copy to GitHub
echo.
echo Press any key to start...
pause >nul

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Python not installed!
    echo Download from: https://python.org
    echo Make sure to check "Add to PATH" during install!
    pause
    exit /b 1
)

echo Installing packages...
pip install google-api-python-client google-auth-oauthlib --quiet

echo.
echo Running authentication...
python auth_setup.py

pause
