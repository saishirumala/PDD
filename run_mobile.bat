@echo off
title NutriGuide - Expo Mobile App (:8081)
cd /d "%~dp0mobile"
echo ====================================================
echo Starting NutriGuide Mobile App on exp://192.168.29.149:8081
echo ====================================================
set NODE_TLS_REJECT_UNAUTHORIZED=0
set REACT_NATIVE_PACKAGER_HOSTNAME=192.168.29.149
call npx.cmd expo start --host lan --port 8081
pause
