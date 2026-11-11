@echo off
title Pasha Hunt 2.0 (APINEX Edition)
cd /d "%~dp0"
where pythonw >nul 2>nul && (start "" pythonw desktop_app.py && exit /b)
where python >nul 2>nul && (start "" python desktop_app.py && exit /b)
if exist "%LOCALAPPDATA%\Programs\Pasha Hunt\PashaHunt.exe" (
    start "" "%LOCALAPPDATA%\Programs\Pasha Hunt\PashaHunt.exe"
    exit /b
)
pause
