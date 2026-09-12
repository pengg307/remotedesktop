# 远程桌面控制软件

Android手机 → Windows电脑 远程桌面控制

## 技术栈

- **Windows端**: Python 3.11 + mss + aiortc (WebRTC)
- **Android端**: Flutter + flutter_webrtc
- **信令服务器**: Python FastAPI + WebSocket

## 快速开始

### 1. 启动信令服务器（终端1）
```bash
cd E:\aiprojects\RemoteDesktop\signaling
uv run python main.py
```

### 2. 启动Windows端服务（终端2）
```bash
cd E:\aiprojects\RemoteDesktop\pyhost
uv run python main.py --token ABCD12
```

### 3. Android端连接
输入Token `ABCD12` 即可建立连接

## 项目结构

```
RemoteDesktop/
├── pyhost/              # Windows端服务
│   ├── main.py          # 入口
│   ├── host.py          # 核心逻辑（屏幕捕获+WebRTC+输入模拟）
│   └── pyproject.toml   # 依赖配置
├── signaling/           # 信令服务器
│   ├── main.py
│   └── pyproject.toml
├── flutter_remote/      # Android客户端（待构建）
│   ├── lib/main.dart
│   └── pubspec.yaml
├── docs/QUICKSTART.md
├── install.py
├── start.sh
└── README.md
```

## 功能

- [x] 屏幕捕获与视频流
- [x] WebRTC P2P连接
- [x] 键鼠模拟控制
- [ ] Android客户端（待构建）
- [ ] 虚拟键盘
- [ ] 文件传输

## 安全

- Token认证机制
- WebRTC内置DTLS加密
- 端到端加密通信
