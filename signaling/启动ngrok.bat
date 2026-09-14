@echo off
title RemoteDesktop - ngrok隧道
chcp 65001 >nul
echo ========================================
echo   RemoteDesktop 信令服务器
echo   + ngrok公网隧道
echo ========================================
echo.

:: 在这里填入你的ngrok Auth Token
:: 获取地址: https://dashboard.ngrok.com/signup
set NGROK_AUTH_TOKEN=YOUR_TOKEN_HERE

echo 正在检查配置...
echo.

:: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未添加到PATH
    echo.
    echo 请先安装Python 3.8+
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

:: 检查uv
uv --version >nul 2>&1
if errorlevel 1 (
    echo ❌ uv未安装
    echo.
    echo 正在安装uv...
    powershell -Command "irm https://astral.sh/uv/install.ps1 | iex"
    if errorlevel 1 (
        echo ❌ uv安装失败
        pause
        exit /b 1
    )
)

:: 检查pyngrok
cd /d %~dp0
call uv sync 2>nul

:: 检查Token
if "%NGROK_AUTH_TOKEN%"=="YOUR_TOKEN_HERE" (
    echo ⚠️  请先配置ngrok Token
    echo.
    echo 步骤:
    echo 1. 打开文件: %~dp0启动ngrok.bat
    echo 2. 找到第8行: set NGROK_AUTH_TOKEN=YOUR_TOKEN_HERE
    echo 3. 替换为: set NGROK_AUTH_TOKEN=你的实际token
    echo 4. 保存并双击运行
    echo.
    echo 获取Token: https://dashboard.ngrok.com/signup
    echo.
    pause
    exit /b 1
)

echo ✅ 环境检查通过
echo.
echo 🚀 正在启动ngrok隧道...
echo.

:: 启动ngrok隧道
uv run python main_ngrok.py

pause
