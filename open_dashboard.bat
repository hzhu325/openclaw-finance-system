@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0verify_and_open.ps1"
echo.
echo If the browser did not open, copy the http://127.0.0.1 URL above into Edge or Chrome.
pause
