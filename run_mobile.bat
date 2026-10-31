@echo off
title NutriGuide - Expo Mobile App (:8081)
cd /d "%~dp0mobile"

for /f "tokens=*" %%a in ('powershell -NoProfile -Command "(Get-NetIPAddress -InterfaceAlias 'Wi-Fi' -AddressFamily IPv4).IPAddress"') do set WIFI_IP=%%a
if "%WIFI_IP%"=="" set WIFI_IP=10.50.251.137

echo ====================================================
echo Starting NutriGuide Mobile App on exp://%WIFI_IP%:8081
echo ====================================================
set NODE_TLS_REJECT_UNAUTHORIZED=0
set REACT_NATIVE_PACKAGER_HOSTNAME=%WIFI_IP%
call npx.cmd expo start --host lan --port 8081
pause
