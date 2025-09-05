@echo off
title EHM Akademi - NO WARNING PAGES!
echo.
echo ========================================
echo    EHM Akademi - ZERO WARNING PAGES!
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install pyngrok if not already installed
echo Installing/checking pyngrok...
pip install pyngrok

echo.
echo 🎯 CHOOSE YOUR DEPLOYMENT METHOD:
echo.
echo 1. ENHANCED NGROK (Custom subdomain - NO warnings)
echo 2. CLOUDFLARE TUNNEL (100%% guaranteed - NO warnings) 
echo 3. ALTERNATIVE SERVICES (LocalTunnel/Serveo - NO warnings)
echo 4. LOCAL ONLY (http://localhost:5000)
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Starting ENHANCED NGROK...
    python app.py
) else if "%choice%"=="2" (
    echo.
    echo ☁️ Starting CLOUDFLARE TUNNEL...
    python start_cloudflare.py
) else if "%choice%"=="3" (
    echo.
    echo 🔄 Starting ALTERNATIVE SERVICES...
    python start_alternative.py
) else if "%choice%"=="4" (
    echo.
    echo 🏠 Starting LOCAL ONLY...
    echo Your app will be available at: http://localhost:5000
    python -c "import app; app.app.run(debug=False, host='0.0.0.0', port=5000)"
) else (
    echo Invalid choice. Starting default enhanced ngrok...
    python app.py
)

echo.
echo Application stopped.
pause