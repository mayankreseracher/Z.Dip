@echo off
title Zytor Sovereign • Media Engine with bclone & Tor
echo ======================================================================
echo           ZYTOR SOVEREIGN : MEDIA ENGINE + BCLONE + TOR
echo ======================================================================
echo.

cd /d "%~dp0"

set "PYTHON_EXE=C:\Users\Mayank\AppData\Local\Programs\Python\Python312\python.exe"

if not exist "%PYTHON_EXE%" (
    set "PYTHON_EXE=python"
)

echo [1/3] Verifying bclone and yt-dlp toolchains...
if not exist "bin\bclone.exe" (
    echo [ERROR] bin\bclone.exe not found!
    pause
    exit /b 1
)
if not exist "bin\yt-dlp.exe" (
    echo [ERROR] bin\yt-dlp.exe not found!
    pause
    exit /b 1
)

echo [2/3] Checking Tor SOCKS5 proxy on 127.0.0.1:9050 / 9150...
echo [3/3] Launching Zytor Engine Server on http://127.0.0.1:8088 ...
echo.
echo Opening browser...
start http://127.0.0.1:8088

"%PYTHON_EXE%" server.py
pause
