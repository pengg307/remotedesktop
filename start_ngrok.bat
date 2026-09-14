@echo off
title ngrok Tunnel - RemoteDesktop
chcp 65001 >nul
echo ========================================
echo   RemoteDesktop Signaling Tunnel
echo   (ngrok v3)
echo ========================================
echo.
echo   正在启动ngrok隧道...
echo.
ngrok http 8000
pause
