@echo off
title NutriGuide Full Stack Launcher
echo ====================================================
echo Launching NutriGuide Full Stack (Backend + Frontend)
echo ====================================================
start "NutriGuide Backend (:8000)" cmd /c "%~dp0run_backend.bat"
start "NutriGuide Frontend (:5173)" cmd /c "%~dp0run_frontend.bat"
echo.
echo Both servers are launching in separate windows!
echo - Backend API:  http://localhost:8000 (Swagger docs at /docs)
echo - Frontend Web: http://localhost:5173
echo ====================================================
timeout /t 5
