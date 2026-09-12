# 远程桌面控制软件 - 快速开始指南

## 项目结构

```
RemoteDesktop/
├── pyhost/              # Windows端服务（Python + WebRTC）
│   ├── main.py          # 入口（uv run python main.py --token ABCD12）
│   ├── host.py          # 核心逻辑：屏幕捕获+WebRTC+输入模拟
│   └── pyproject.toml   # Python依赖配置
│
├── signaling/           # 信令服务器（Python FastAPI）
│   ├── main.py
│   └── pyproject.toml
│
├── flutter_remote/      # Android客户端（Flutter）
│   ├── lib/main.dart    # Flutter应用入口
│   └── pubspec.yaml     # Flutter依赖
│
├── docs/QUICKSTART.md
├── install.py           # 依赖安装脚本
├── start.sh             # 启动脚本
└── README.md
```

---

## 快速启动

### 终端1：启动信令服务器
```bash
cd /e/aiprojects/RemoteDesktop/signaling
uv run python main.py
```
监听 `http://localhost:8000`

### 终端2：启动Windows端服务
```bash
cd /e/aiprojects/RemoteDesktop/pyhost
uv run python main.py --token ABCD12
```
会生成 `offer_ABCD12.json`，等待Android连接。

### Android端
在手机上运行Flutter构建的APP，输入Token `ABCD12` 和服务器地址（局域网IP）。

---

## 当前状态

| 模块 | 状态 | 说明 |
|------|------|------|
| **信令服务器** | ✅ 完成 | FastAPI + WebSocket，Token生成正常 |
| **Windows端** | ✅ 完成 | 屏幕捕获、WebRTC Offer生成、键鼠模拟 |
| **Android端** | ⏳ 代码已写好 | 需要Flutter环境构建APK |

---

## 技术栈

- **Windows端**: Python 3.11 + mss(屏幕捕获) + aiortc(WebRTC) + opencv-python
- **信令服务器**: Python FastAPI + websockets
- **Android端**: Flutter + flutter_webrtc

---

## 后续步骤

1. **测试本地连通性**：在同一台机器上用浏览器模拟Android端测试WebRTC连接
2. **构建Android APK**：安装Flutter后运行 `flutter build apk`
3. **优化延迟**：调整编码参数、降低分辨率
4. **添加虚拟键盘**：在Android端集成IME
5. **发布**：确认功能稳定后推送到Git仓库
