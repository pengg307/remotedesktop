#!/bin/bash
# Flutter APK 自动构建脚本
# 用法: bash build_android.sh

set -e

PROJECT_DIR="/e/aiprojects/RemoteDesktop"
FLUTTER_DIR="$PROJECT_DIR/flutter_remote"

echo "=========================================="
echo "Flutter APK 自动构建脚本"
echo "=========================================="
echo ""

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 未找到Docker，请先安装Docker"
    exit 1
fi

echo "✓ Docker已安装"

# 检查Flutter项目
if [ ! -f "$FLUTTER_DIR/pubspec.yaml" ]; then
    echo "❌ 未找到pubspec.yaml，请确认项目路径正确"
    exit 1
fi

echo "✓ Flutter项目结构正确"
echo ""

# 构建Docker镜像
echo "[1/3] 构建Docker镜像..."
docker build -t flutter-remote-build "$FLUTTER_DIR" -f "$PROJECT_DIR/Dockerfile"

# 运行容器并提取APK
echo "[2/3] 构建APK..."
CONTAINER_ID=$(docker create flutter-remote-build)
docker cp "$CONTAINER_ID":/app/build/app/outputs/flutter-apk/app-release.apk "$FLUTTER_DIR/build/app/outputs/flutter-apk/"
docker rm "$CONTAINER_ID" > /dev/null

# 验证APK
echo "[3/3] 验证构建结果..."
if [ -f "$FLUTTER_DIR/build/app/outputs/flutter-apk/app-release.apk" ]; then
    APK_SIZE=$(du -h "$FLUTTER_DIR/build/app/outputs/flutter-apk/app-release.apk" | cut -f1)
    echo "✓ APK构建成功!"
    echo "  文件大小: $APK_SIZE"
    echo "  文件路径: $FLUTTER_DIR/build/app/outputs/flutter-apk/app-release.apk"
else
    echo "❌ APK构建失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "构建完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 将APK安装到Android设备: adb install $FLUTTER_DIR/build/app/outputs/flutter-apk/app-release.apk"
echo "2. 确保手机和电脑在同一WiFi网络"
echo "3. 打开APP，输入Token连接Windows端"
