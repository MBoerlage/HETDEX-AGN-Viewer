@echo off
title HAS DATA SIG HETDEX Viewer
cd /d "%~dp0"

:: ── Check Python is available ────────────────────────────────────────────────
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found. Please run install.bat first.
    pause
    exit /b 1
)

:: ── Check if server is already running ──────────────────────────────────────
netstat -an 2>nul | find ":5000 " | find "LISTENING" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Server is already running on port 5000.
    start http://localhost:5000
    exit /b 0
)

:: ── Start the Flask server in a separate window ──────────────────────────────
echo Starting HAS DATA SIG HETDEX Viewer...
start "HAS DATA SIG HETDEX Server" python server.py

:: ── Wait for Flask to finish loading the FITS file (~3 s) ───────────────────
timeout /t 4 /nobreak >nul

:: ── Open browser ─────────────────────────────────────────────────────────────
start http://localhost:5000

echo.
echo Viewer is open in your browser.
echo Keep the server window open while using the tool.
echo Close the server window (or press Ctrl+C there) to stop.
