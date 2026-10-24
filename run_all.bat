@echo off
title NutriGuide Full System Launcher
echo ====================================================
echo Launching NutriGuide (Backend + Web + Mobile)
echo ====================================================
start "NutriGuide Backend (:8000)" cmd /k "%~dp0run_backend.bat"
start "NutriGuide Web Frontend (:5173)" cmd /k "%~dp0run_frontend.bat"
start "NutriGuide Mobile App (:8081)" cmd /k "%~dp0run_mobile.bat"
echo.
echo All 3 servers are launching in separate windows!
echo - 1. Backend API:  http://localhost:8000 (Swagger docs at /docs)
echo - 2. Web Frontend: http://localhost:5173
echo - 3. Mobile App:   exp://192.168.29.149:8081 (Expo Go)
echo ====================================================
timeout /t 5
