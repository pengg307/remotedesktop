@rem 构建Android APK
@echo off
echo ========================================
echo   RemoteDesk Android Build Script
echo ========================================
echo.

cd /d "%~dp0android_remote"

echo [1/3] 检查Gradle...
if exist gradlew.bat (
    echo   Gradle Wrapper found
) else (
    echo   ERROR: gradlew.bat not found
    pause
    exit /b 1
)

echo [2/3] 构建APK...
call gradlew.bat assembleDebug

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] 构建失败
    pause
    exit /b 1
)

echo [3/3] 完成
echo.
echo APK位置: app\build\outputs\apk\debug\app-debug.apk
echo.
echo ========================================
pause
