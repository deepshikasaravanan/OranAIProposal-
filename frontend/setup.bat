@echo off
title Proposal Bot Frontend Setup

echo 🚀 Setting up Proposal Bot Frontend...

:: Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

:: Get Node.js version
for /f "tokens=1 delims=v" %%i in ('node -v') do set NODE_VERSION=%%i
echo ✅ Node.js %NODE_VERSION% detected

:: Navigate to script directory
cd /d "%~dp0"

:: Check if package.json exists
if not exist "package.json" (
    echo ❌ package.json not found. Are you in the frontend directory?
    pause
    exit /b 1
)

:: Install dependencies
echo 📦 Installing dependencies...
where npm >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ npm not found. Please install Node.js with npm.
    pause
    exit /b 1
)

call npm install
if %errorlevel% equ 0 (
    echo ✅ Dependencies installed successfully
) else (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

:: Check if backend is running
echo 🔍 Checking if backend is running on localhost:8000...
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:8000/health' -TimeoutSec 5 | Out-Null; exit 0 } catch { exit 1 }" >nul 2>nul
if %errorlevel% equ 0 (
    echo ✅ Backend is running
) else (
    echo ⚠️  Backend is not running on localhost:8000
    echo    Please start the backend first:
    echo    cd .. ^&^& python -m uvicorn web.app:app --reload --port 8000
)

echo.
echo 🎉 Setup complete!
echo.
echo Available commands:
echo   npm run dev     - Start development server
echo   npm run build   - Build for production
echo   npm run preview - Preview production build
echo   npm run lint    - Run ESLint
echo.
echo To start the development server:
echo   npm run dev
echo.
echo The frontend will be available at: http://localhost:3000
echo.
pause