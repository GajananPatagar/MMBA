@echo off
echo ╔══════════════════════════════════════════╗
echo ║   MMBA Auto-Installer for Windows       ║
echo ║   IHTM Department                       ║
echo ╚══════════════════════════════════════════╝

echo [1/3] Checking Python...
python --version 2>nul
if errorlevel 1 (
    echo Python not found. Downloading...
    curl -fsSL https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd64.exe -o python_installer.exe
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python_installer.exe
)

echo [2/3] Installing brain...
python installer.py

echo [3/3] Starting MMBA...
MMBA.exe --mode status

echo.
echo ✓ MMBA Ready! 
echo Run anytime: MMBA.exe --mode manual
pause
