#!/bin/bash
# 远程桌面 - Docker构建脚本
# 用法: bash build_android.sh

set -e

PROJECT_DIR="/e/aiprojects/RemoteDesktop"

echo "=========================================="
echo "远程桌面控制软件 - Docker构建脚本"
echo "=========================================="
echo ""

cd "$PROJECT_DIR"

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker未安装，请先安装Docker"
    exit 1
fi

echo "✓ Docker已安装"
echo ""

# 构建Docker镜像
echo "🔨 构建Docker镜像..."
docker build -t remote-desktop-android . 2>&1

echo ""
echo "✅ Docker镜像构建成功"
echo ""
echo "📱 运行容器提取APK..."
docker run --rm -v "$PROJECT_DIR/output:/output" remote-desktop-android \
    cp /app/build/app/outputs/flutter-apk/app-release.apk /output/

echo ""
echo "=========================================="
echo "✅ 构建完成！"
echo "APK位置: $PROJECT_DIR/output/app-release.apk"
echo "=========================================="
echo ""
echo "安装到手机:"
echo "  adb install $PROJECT_DIR/output/app-release.apk"
echo ""
