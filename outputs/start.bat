@echo off
setlocal
cd /d "%~dp0"
set "PYTHON_EXE=J:\GIT\MINICONDA\envs\ai_center\python.exe"

if not exist "%PYTHON_EXE%" (
  echo Python interpreter not found:
  echo %PYTHON_EXE%
  pause
  exit /b 1
)

start "Open Signal Desk" http://127.0.0.1:8765
"%PYTHON_EXE%" server.py
pause
