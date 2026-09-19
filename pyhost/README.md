# Remote Desktop Host (Windows端)

内置信令服务器模式，适用于Tailscale内网环境。

## 启动方式

```bash
cd E:/aiprojects/RemoteDesktop/pyhost
uv run python main.py
```

或指定token：
```bash
uv run python main.py --token ABC123
```

## 输出示例

```
==================================================
远程桌面主机已启动
==================================================
信令地址: http://100.x.x.x:8000
Token: ABC123
房间ID: a1b2c3d4e5f6
==================================================

请用Android APP输入以上信息连接
```

## 工作原理

1. Windows端启动时，内置信令服务器运行在本地（如 `http://100.x.x.x:8000`）
2. Android APP通过Tailscale网络访问该地址
3. APP输入Token后建立WebSocket连接
4. Windows端创建WebRTC Offer，保存为JSON文件
5. APP读取JSON文件创建Answer
6. WebRTC连接建立，视频流传输

## 依赖

```bash
pip install -r requirements.txt
```

或：
```bash
uv pip install -r requirements.txt
```
