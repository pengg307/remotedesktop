@echo off
REM Git Push with Auto-Retry Script (Windows Batch)
REM For unstable network connections (China -> GitHub)

setlocal enabledelayedexpansion

set "REPO_DIR=%~1"
set "MAX_RETRIES=10"
set "RETRY_DELAY=10"

if "%REPO_DIR%"=="" set "REPO_DIR=."

echo ==================================
echo Git Push Auto-Retry Script
echo ==================================
echo Repository: %REPO_DIR%
echo Max retries: %MAX_RETRIES%
echo Retry delay: %RETRY_DELAY%s
echo.

cd /d "%REPO_DIR%" || exit /b 1

REM Check if there are changes to push
echo Checking git status...
git status --short
echo.

REM Try to push with retry logic
for /l %%i in (1,1,%MAX_RETRIES%) do (
    echo [%%i/%MAX_RETRIES%] Attempting to push...
    
    git push origin main 2>&1
    if !errorlevel! equ 0 (
        echo.
        echo ==================================
        echo Push successful!
        echo ==================================
        exit /b 0
    )
    
    echo Network error detected
    if %%i LSS %MAX_RETRIES% (
        echo Waiting %RETRY_DELAY%s before retry...
        ping -n %RETRY_DELAY% 127.0.0.1 >nul
    )
)

echo.
echo ==================================
echo Failed after %MAX_RETRIES% attempts
echo ==================================
echo.
echo Suggestions:
echo 1. Check your network connection
echo 2. Try using a VPN/proxy
echo 3. Wait a few minutes and try again
echo 4. Consider using SSH instead of HTTPS
exit /b 1
