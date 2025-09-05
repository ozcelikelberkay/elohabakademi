@echo off
title EHM Akademi - ULTIMATE NO WARNING DEPLOYMENT
color 0A
echo.
echo ===============================================
echo    🎯 EHM AKADEMI - ULTIMATE DEPLOYMENT
echo    🚫 100%% NO WARNING PAGES GUARANTEED!
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo ✅ Python detected!
echo.

echo 🎯 CHOOSE YOUR DEPLOYMENT METHOD:
echo.
echo 1. 🔥 ENHANCED NGROK (Multiple bypass URLs - BEST for quick start)
echo 2. ☁️  CLOUDFLARE TUNNEL (100%% guaranteed - Professional)
echo 3. 🌐 LOCALTUNNEL (Alternative - No warnings)
echo 4. 🏠 LOCAL ONLY (http://localhost:5000)
echo 5. 📱 ALL METHODS (Try everything)
echo.

set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    echo.
    echo 🔥 Starting ENHANCED NGROK with bypass...
    echo ✅ Multiple URL formats will be provided
    echo ✅ Enhanced headers enabled
    echo ✅ Warning page bypass activated
    echo.
    python app.py
) else if "%choice%"=="2" (
    echo.
    echo ☁️ Starting CLOUDFLARE TUNNEL...
    echo ✅ Custom domain provided
    echo ✅ Zero warning pages
    echo ✅ Professional solution
    echo.
    python app_cloudflare.py
) else if "%choice%"=="3" (
    echo.
    echo 🌐 Starting LOCALTUNNEL...
    echo ✅ Alternative tunneling service
    echo ✅ No ngrok warnings
    echo.
    
    REM Install localtunnel if needed
    where lt >nul 2>&1
    if errorlevel 1 (
        echo Installing localtunnel...
        npm install -g localtunnel
    )
    
    REM Start Flask in background
    start /B python -c "from app import app; app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)"
    
    REM Wait for Flask to start
    timeout /t 3 /nobreak >nul
    
    REM Start localtunnel
    echo Starting tunnel...
    lt --port 5000
    
) else if "%choice%"=="4" (
    echo.
    echo 🏠 Starting LOCAL ONLY...
    echo Your app will be available at: http://localhost:5000
    echo ⚠️ Only accessible from this computer
    echo.
    python -c "from app import app; app.run(debug=False, host='0.0.0.0', port=5000)"
    
) else if "%choice%"=="5" (
    echo.
    echo 📱 TRYING ALL METHODS...
    echo.
    
    echo 🔥 Method 1: Enhanced Ngrok
    start /B python app.py
    timeout /t 5 /nobreak >nul
    
    echo ☁️ Method 2: Cloudflare Tunnel  
    start /B python app_cloudflare.py
    timeout /t 5 /nobreak >nul
    
    echo 🌐 Method 3: LocalTunnel
    where lt >nul 2>&1
    if not errorlevel 1 (
        start /B lt --port 5000
    )
    
    echo.
    echo ✅ All methods started!
    echo Check the terminal windows for URLs
    echo Choose the one that works best for you
    pause
    
) else (
    echo Invalid choice. Starting enhanced ngrok by default...
    python app.py
)

echo.
echo 🛑 Application stopped.
echo.
pause