#!/bin/bash
# Windows远程桌面服务 - 一键启动脚本

echo "================================"
echo "远程桌面控制软件 - 启动脚本"
echo "================================"
echo ""

cd /e/aiprojects/RemoteDesktop

# 检查信令服务器是否已启动
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ 信令服务器已在运行"
else
    echo "启动信令服务器..."
    cd signaling
    uv run python main.py &
    SIGNALING_PID=$!
    echo "  信令服务器PID: $SIGNALING_PID"
    sleep 1
    cd ..
fi

# 询问Token
echo ""
read -p "请输入连接Token (6位字母+数字): " TOKEN

# 启动Windows端
echo ""
echo "启动Windows端服务..."
cd pyhost
uv run python main.py --token "$TOKEN"
cd ..
