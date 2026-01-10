@echo off
color 0B
echo.
echo ========================================
echo    CARE-BRIDGE AI - System Check
echo ========================================
echo.

echo Checking Backend Server (Port 8000)...
netstat -an | findstr ":8000" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Backend is RUNNING on http://127.0.0.1:8000
) else (
    echo [!!] Backend is NOT RUNNING
    echo     Start with: python main.py
)

echo.
echo Checking Frontend Server (Port 5173)...
netstat -an | findstr ":5173" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Frontend is RUNNING on http://localhost:5173
) else (
    echo [!!] Frontend is NOT RUNNING
    echo     Start with: cd frontend ^&^& npm run dev
)

echo.
echo ========================================
echo    Access Your Application
echo ========================================
echo.
echo Frontend:   http://localhost:5173
echo Backend:    http://127.0.0.1:8000
echo API Docs:   http://127.0.0.1:8000/docs
echo.
echo ========================================
echo.
pause
