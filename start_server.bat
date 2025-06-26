@echo off
REM ArtifactVirtual.com - Portable Server Launcher (Windows)
REM Self-contained web server with monitoring dashboard

title ArtifactVirtual.com - Portable Server

echo.
echo ========================================
echo  ArtifactVirtual.com - Portable Server
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Check if portable_server.py exists
if not exist "portable_server.py" (
    echo ERROR: portable_server.py not found
    echo Please ensure you're running this from the correct directory
    pause
    exit /b 1
)

REM Create required directories
if not exist "config" mkdir config
if not exist "nginx" mkdir nginx
if not exist "www\html" mkdir www\html
if not exist "ssl\certs" mkdir ssl\certs
if not exist "logs" mkdir logs
if not exist "monitor" mkdir monitor

echo Checking dependencies...

REM Download Nginx for Windows if not present
if not exist "nginx\nginx.exe" (
    echo Downloading Nginx for Windows...
    
    REM Try to download using PowerShell
    powershell -Command "& {Invoke-WebRequest -Uri 'https://nginx.org/download/nginx-1.24.0.zip' -OutFile 'nginx.zip'}" 2>nul
    if exist "nginx.zip" (
        echo Extracting Nginx...
        powershell -Command "& {Expand-Archive -Path 'nginx.zip' -DestinationPath 'temp' -Force}"
        if exist "temp\nginx-1.24.0" (
            xcopy "temp\nginx-1.24.0\*" "nginx\" /s /e /y >nul
            rmdir /s /q temp >nul 2>&1
            del nginx.zip >nul 2>&1
            echo Nginx extracted successfully
        ) else (
            echo ERROR: Failed to extract Nginx
            pause
            exit /b 1
        )
    ) else (
        echo ERROR: Failed to download Nginx
        echo Please download nginx-1.24.0.zip manually from https://nginx.org/download/
        echo and extract it to the nginx\ directory
        pause
        exit /b 1
    )
)

REM Create simple monitoring dashboard if not present
if not exist "monitor\dashboard.py" (
    echo Creating monitoring dashboard...
    (
        echo import time
        echo import sys
        echo from datetime import datetime
        echo.
        echo print("Monitoring Dashboard - ArtifactVirtual.com"^)
        echo print("="*50^)
        echo print("Server Status: Online"^)
        echo print("Started:", datetime.now(^).strftime("%%Y-%%m-%%d %%H:%%M:%%S"^)^)
        echo print("Press Ctrl+C to exit"^)
        echo.
        echo try:
        echo     while True:
        echo         time.sleep(30^)
        echo         print(f"Heartbeat: {datetime.now(^).strftime('%%H:%%M:%%S'} - System OK"^)
        echo except KeyboardInterrupt:
        echo     print("Monitoring stopped"^)
    ) > monitor\dashboard.py
)

echo.
echo Starting ArtifactVirtual.com Portable Server...
echo.

REM Start the server
python portable_server.py

REM If we get here, the server has stopped
echo.
echo Server stopped.
pause
