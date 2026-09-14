@echo off
REM 启动信令服务器脚本 (Windows)
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo ==========================================
echo   RemoteDesktop Signaling Server
echo ==========================================
echo.

REM 检查Python
where python >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到python
    pause
    exit /b 1
)

echo [1/3] 创建虚拟环境...
if not exist "venv" (
    python -m venv venv
)

echo [2/3] 激活虚拟环境...
call venv\Scripts\activate.bat

echo [3/3] 安装依赖...
pip install -r requirements.txt --quiet

echo.
echo 启动服务器...
echo   地址: http://localhost:8000
echo   健康检查: curl http://localhost:8000/api/health
echo.

python start_server.py
pause