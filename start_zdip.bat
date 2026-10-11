@echo off
setlocal enabledelayedexpansion
title Z.Dip Sovereign Engine • Video & Cloud Pipeline
echo ======================================================================
echo           Z.DIP : SOVEREIGN VIDEO EXTRACTION & CLOUD ENGINE
echo ======================================================================
echo.

cd /d "%~dp0"

:: 1. Auto-discover Python executable
set "PYTHON_CMD="

where python >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=python"
    goto :found_python
)

where py >nul 2>&1
if %errorlevel% equ 0 (
    set "PYTHON_CMD=py -3"
    goto :found_python
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :found_python
)

if exist "C:\Python312\python.exe" (
    set "PYTHON_CMD=C:\Python312\python.exe"
    goto :found_python
)

echo [!] ERROR: Python 3.10+ was not found on your system PATH.
echo     Please install Python from https://www.python.org/downloads/
echo     and ensure "Add Python to PATH" is checked during installation.
pause
exit /b 1

:found_python
echo [1/3] Using Python: %PYTHON_CMD%

echo [2/3] Checking Tor SOCKS5 daemon status...
echo [3/3] Launching Z.Dip Sovereign Dashboard on http://127.0.0.1:8088 ...
echo.
echo Opening browser...
start http://127.0.0.1:8088

%PYTHON_CMD% -m zdip.server
pause
