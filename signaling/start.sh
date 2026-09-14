#!/bin/bash
# 启动信令服务器脚本
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到python3"
    exit 1
fi

echo "=========================================="
echo "  RemoteDesktop Signaling Server"
echo "=========================================="
echo ""

# 检查依赖
if [ ! -d "venv" ]; then
    echo "[1/3] 创建虚拟环境..."
    python3 -m venv venv
fi

echo "[2/3] 激活虚拟环境..."
source venv/bin/activate

echo "[3/3] 安装依赖..."
pip install -r requirements.txt -q

echo ""
echo "启动服务器..."
echo "  地址: http://localhost:8000"
echo "  健康检查: curl http://localhost:8000/api/health"
echo ""

python3 start_server.py