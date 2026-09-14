@echo off
title ngrok Tunnel - RemoteDesktop
chcp 65001 >nul
echo ========================================
echo   RemoteDesktop 信令服务器 + ngrok
echo ========================================
echo.
echo 检查ngrok配置...
python -c "import os; print('NGROK_AUTH_TOKEN:', '已设置' if os.getenv('NGROK_AUTH_TOKEN') else '未设置')"
echo.
if "%NGROK_AUTH_TOKEN%"=="" (
    echo ⚠️  请先设置ngrok Auth Token
    echo.
    echo 设置方法 (Windows):
    echo   set NGROK_AUTH_TOKEN=YOUR_TOKEN
    echo.
    echo 或者运行安装脚本:
    echo   install_ngrok.bat
    echo.
    pause
    exit /b 1
)
echo.
echo 🚀 启动ngrok隧道...
echo.
uv run python main_ngrok.py
pause
