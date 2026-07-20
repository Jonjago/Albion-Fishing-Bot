@echo off
setlocal
cd /d "%~dp0"
title Albion Fishing Bot

echo ==================================================
echo    Albion Fishing Bot
echo ==================================================
echo.

set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY where python >nul 2>&1 && set "PY=python"

if not defined PY (
  echo  [X] Python was not found on this computer.
  echo.
  echo      1. Download Python from https://www.python.org/downloads/
  echo      2. During the installation, tick "Add python.exe to PATH"
  echo      3. Run this file again
  echo.
  pause
  exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
  echo  [1/3] Setting up a private Python environment ^(first run only^)...
  %PY% -m venv .venv
  if errorlevel 1 goto :fail
) else (
  echo  [1/3] Python environment found.
)

echo  [2/3] Checking required packages...
".venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
".venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
if errorlevel 1 goto :fail

echo  [3/3] Starting the bot...
echo.
".venv\Scripts\python.exe" dashboard.py
if errorlevel 1 goto :fail

exit /b 0

:fail
echo.
echo  [X] Something went wrong. Copy the messages above when asking for help.
echo.
pause
exit /b 1
