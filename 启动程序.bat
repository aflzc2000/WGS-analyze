@echo off
setlocal

set "SCRIPT_DIR=%~dp0"

set "PATH=%SCRIPT_DIR%Blast\Windows;%PATH%"

.\Python\Windows\python.exe .\Code\run_webui.py

pause
endlocal
