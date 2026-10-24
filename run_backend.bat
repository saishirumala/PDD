@echo off
title NutriGuide - FastAPI Backend Server (:8000)
cd /d "%~dp0backend"
echo ===================================================
echo Starting NutriGuide Backend on http://0.0.0.0:8000
echo ===================================================
if exist "venv\Scripts\python.exe" (
    venv\Scripts\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
) else (
    echo Python virtual environment not found in backend\venv!
    echo Running with system python:
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
)
pause
