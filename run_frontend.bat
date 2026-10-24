@echo off
title NutriGuide - React Frontend Web (:5173)
cd /d "%~dp0frontend"
echo ====================================================
echo Starting NutriGuide Frontend on http://localhost:5173
echo ====================================================
call npm.cmd run dev -- --host 0.0.0.0 --port 5173
pause
