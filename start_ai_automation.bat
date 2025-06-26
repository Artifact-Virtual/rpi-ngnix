@echo off
echo 🤖 Reverse Ingress-Nginx - AI Automation Suite
echo ==============================================
echo.

:: Check if Node.js is installed
node --version >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

:: Check if we're in the correct directory
if not exist "automation_scripts" (
    echo ❌ automation_scripts directory not found
    echo Please run this script from the cert-nginx directory
    pause
    exit /b 1
)

:: Install npm dependencies if needed
if not exist "node_modules" (
    echo 📦 Installing Node.js dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo Choose an option:
echo 1. Start AI Automation Dashboard (Recommended)
echo 2. Run Health Check
echo 3. Run Security Scan
echo 4. Run Performance Test
echo 5. Run Content Analysis
echo 6. Run Visual Regression Test
echo 7. Run Complete AI Suite
echo 8. Generate Report
echo 9. Exit
echo.

set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto dashboard
if "%choice%"=="2" goto health
if "%choice%"=="3" goto security
if "%choice%"=="4" goto performance
if "%choice%"=="5" goto content
if "%choice%"=="6" goto visual
if "%choice%"=="7" goto suite
if "%choice%"=="8" goto report
if "%choice%"=="9" goto exit
goto invalid

:dashboard
echo 🚀 Starting AI Automation Dashboard...
node automation_scripts/orchestrator_fixed.js dashboard
goto end

:health
echo 🏥 Running Health Check...
node automation_scripts/automation.js health
goto end

:security
echo 🛡️ Running Security Scan...
node automation_scripts/advanced_ai_automation.js security
goto end

:performance
echo ⚡ Running Performance Test...
node automation_scripts/advanced_ai_automation.js performance
goto end

:content
echo 🧠 Running Content Analysis...
node automation_scripts/advanced_ai_automation.js content
goto end

:visual
echo 📸 Running Visual Regression Test...
node automation_scripts/advanced_ai_automation.js visual
goto end

:suite
echo 🚀 Running Complete AI Suite...
node automation_scripts/advanced_ai_automation.js all
goto end

:report
echo 📊 Generating Report...
node automation_scripts/orchestrator_fixed.js report
goto end

:invalid
echo ❌ Invalid choice. Please select 1-9.
pause
goto start

:exit
echo 👋 Goodbye!
goto end

:end
pause
