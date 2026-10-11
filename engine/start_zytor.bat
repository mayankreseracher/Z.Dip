@echo off
setlocal enabledelayedexpansion
title Zytor Sovereign • Media Engine with bclone & Tor
echo ======================================================================
echo           ZYTOR SOVEREIGN : MEDIA ENGINE + BCLONE + TOR
echo ======================================================================
echo.

cd /d "%~dp0"

:: Auto-discover Python executable
set "PYTHON_CMD=python"
where python >nul 2>&1
if %errorlevel% neq 0 (
    where py >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYTHON_CMD=py -3"
    ) else if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
        set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    )
)

echo [1/3] Using Python: %PYTHON_CMD%
echo [2/3] Checking Tor SOCKS5 proxy on 127.0.0.1:9050 / 9150...
echo [3/3] Launching Zytor Engine Server on http://127.0.0.1:8088 ...
echo.
echo Opening browser...
start http://127.0.0.1:8088

%PYTHON_CMD% server.py
pause
