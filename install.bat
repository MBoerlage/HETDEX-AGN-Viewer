@echo off
setlocal enabledelayedexpansion
title HAS DATA SIG HETDEX Viewer - Installer
cd /d "%~dp0"

echo.
echo  ================================================================
echo   HAS DATA SIG HETDEX Viewer - Installation
echo  ================================================================
echo.

:: ────────────────────────────────────────────────────────────────────────────
:: STEP 1  Check for Python
:: ────────────────────────────────────────────────────────────────────────────
echo  [1/4]  Checking for Python...

python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYVER=%%v
    echo         Found: !PYVER!
    set PYTHON=python
    goto :step2
)

py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    for /f "tokens=*" %%v in ('py --version 2^>^&1') do set PYVER=%%v
    echo         Found Python Launcher: !PYVER!
    set PYTHON=py
    goto :step2
)

:: Python not found — try winget (available on Windows 10 1903+ and Windows 11)
echo         Python not found.
echo.
echo  [1/4]  Attempting to install Python 3.12 via winget...

winget --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  ERROR: winget is not available on this system.
    echo.
    echo  Please install Python manually:
    echo    1. Visit  https://www.python.org/downloads/
    echo    2. Download Python 3.12 or newer
    echo    3. Run the installer
    echo    4. IMPORTANT: tick "Add Python to PATH"
    echo    5. Re-run this installer (install.bat)
    echo.
    pause
    exit /b 1
)

winget install -e --id Python.Python.3.12 ^
    --accept-package-agreements ^
    --accept-source-agreements
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  ERROR: Automatic Python installation failed.
    echo  Please install Python manually from https://www.python.org/downloads/
    echo  Tick "Add Python to PATH" during setup, then re-run this installer.
    echo.
    pause
    exit /b 1
)

echo.
echo  Python 3.12 installed.
echo.
echo  IMPORTANT: The PATH variable updates only take effect in a new terminal.
echo  Please CLOSE this window and run install.bat again to continue.
echo.
pause
exit /b 0

:: ────────────────────────────────────────────────────────────────────────────
:: STEP 2  Upgrade pip
:: ────────────────────────────────────────────────────────────────────────────
:step2
echo.
echo  [2/4]  Upgrading pip...
%PYTHON% -m pip install --upgrade pip --quiet
if %ERRORLEVEL% NEQ 0 (
    echo         WARNING: pip upgrade failed — continuing with existing version.
)
echo         Done.

:: ────────────────────────────────────────────────────────────────────────────
:: STEP 3  Install Python packages
:: ────────────────────────────────────────────────────────────────────────────
echo.
echo  [3/4]  Installing required packages:
echo         numpy  astropy  astroquery  flask
echo         (This may take a minute on first install)
echo.
%PYTHON% -m pip install numpy astropy astroquery flask
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  ERROR: Package installation failed.
    echo  Check your internet connection and try again.
    echo.
    pause
    exit /b 1
)
echo.
echo         Packages installed successfully.

:: ────────────────────────────────────────────────────────────────────────────
:: STEP 4  Download NGC catalog and run cross-match
:: ────────────────────────────────────────────────────────────────────────────
echo.
echo  [4/4]  Downloading the NGC catalog from VizieR and matching
echo         with the HETDEX AGN catalog...
echo         (Requires internet — may take up to 2 minutes)
echo.
%PYTHON% match_ngc.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo  WARNING: NGC catalog match encountered an error.
    echo  The viewer will work but Tab 4 (NGC Matches) may be empty.
    echo  You can re-run  python match_ngc.py  later to retry.
)

:: ────────────────────────────────────────────────────────────────────────────
:: Done
:: ────────────────────────────────────────────────────────────────────────────
echo.
echo  ================================================================
echo   Installation complete!
echo.
echo   Double-click  launch.bat  to open the viewer.
echo  ================================================================
echo.
pause
