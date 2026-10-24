@echo off
title NutriGuide - FastAPI Backend Server
cd /d "%~dp0backend"
echo ===================================================
echo Starting NutriGuide Backend on http://localhost:8000
echo ===================================================
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
) else (
    echo Python virtual environment not found in backend\venv!
    echo Running with system python:
    python -m uvicorn app.main:app --reload --port 8000
)
pause
