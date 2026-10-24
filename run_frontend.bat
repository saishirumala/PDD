@echo off
title NutriGuide - React Frontend Client
cd /d "%~dp0frontend"
echo ====================================================
echo Starting NutriGuide Frontend on http://localhost:5173
echo ====================================================
call npm.cmd run dev
pause
