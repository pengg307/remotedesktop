#!/bin/bash
# 远程桌面 - Docker构建脚本
# 用法: bash build_android.sh

set -e

echo "=========================================="
echo " 远程桌面控制软件 - Docker构建脚本"
echo "=========================================="
echo ""

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "❌ 错误: Docker 未安装"
    echo "请先安装 Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# 项目路径
PROJECT_DIR="/e/aiprojects/RemoteDesktop"
OUTPUT_DIR="$PROJECT_DIR/output"

echo "📂 项目目录: $PROJECT_DIR"
echo "📦 输出目录: $OUTPUT_DIR"
echo ""

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

echo "🚀 开始 Docker 构建..."
echo ""

# 构建 Docker 镜像
docker build -t remote-desktop-android "$PROJECT_DIR"

echo ""
echo "✅ Docker 镜像构建完成"
echo ""
echo "📱 正在生成 APK..."
echo ""

# 运行容器并复制 APK
docker run --rm \
    -v "$OUTPUT_DIR:/output" \
    remote-desktop-android

echo ""
echo "=========================================="
echo " 构建完成！"
echo "=========================================="
echo ""
echo "📦 APK 位置: $OUTPUT_DIR/app-release.apk"
echo ""
echo "下一步:"
echo "  1. 将 APK 传输到手机"
echo "  2. 在手机上安装并打开"
echo "  3. 输入 Token: TEST01"
echo "  4. 输入服务器地址: http://您的IP:8000"
echo ""
