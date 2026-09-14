@echo off
title ngrok Tunnel Setup
chcp 65001 >nul
echo ========================================
echo   ngrok 自动安装配置
echo ========================================
echo.
echo 正在下载ngrok...
python install_ngrok.py
echo.
pause
