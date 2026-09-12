#!/bin/bash
# 远程桌面控制软件 - 一键启动脚本

echo "=========================================="
echo "远程桌面控制软件"
echo "=========================================="
echo ""

cd /e/aiprojects/RemoteDesktop

# 启动信令服务器
echo "[1] 启动信令服务器..."
if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    cd signaling
    uv run python main.py &
    SIGNALING_PID=$!
    echo "   信令服务器 PID: $SIGNALING_PID"
    sleep 1
    cd ..
    echo "   ✓ 信令服务器已启动 (http://localhost:8000)"
else
    echo "   ✓ 信令服务器已在运行"
fi

echo ""
echo "=========================================="
echo ""
echo "现在启动Windows端服务："
echo "  cd pyhost && uv run python main.py --token [你的6位Token]"
echo ""
echo "示例："
echo "  cd pyhost && uv run python main.py --token ABCD12"
echo ""
echo "=========================================="
