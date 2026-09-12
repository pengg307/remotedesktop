# 远程桌面控制软件

Android手机 → Windows电脑 远程桌面控制

## 技术栈

- **Windows端**: Python 3.11 + mss + aiortc (WebRTC)
- **Android端**: Flutter + flutter_webrtc
- **信令服务器**: Python FastAPI + WebSocket

## 快速开始

### 本地运行

**终端1 - 信令服务器**:
```bash
cd E:\aiprojects\RemoteDesktop\signaling
uv run python main.py
```

**终端2 - Windows端**:
```bash
cd E:\aiprojects\RemoteDesktop\pyhost
uv run python main.py --token ABCD12
```

### GitHub Actions 构建 APK

**当前状态**: 
- Workflow: .github/workflows/build-apk.yml
- 最新构建: Run #6 (进行中)
- Flutter版本: 3.19.0

**触发方式**:
- 推送代码到 main/master 分支
- 手动触发 (workflow_dispatch)

**查看构建**:
https://github.com/pengg307/remotedesktop/actions

## 项目结构

```
RemoteDesktop/
├── pyhost/              # Windows端服务 ✅
│   ├── host.py          # 核心逻辑
│   └── main.py          # 入口
├── signaling/           # 信令服务器 ✅
│   └── main.py
├── flutter_remote/      # Android客户端 ✅
│   ├── lib/main.dart
│   └── pubspec.yaml
├── .github/workflows/
│   └── build-apk.yml    # GitHub Actions配置
└── README.md
```

## 功能状态

| 模块 | 状态 | 说明 |
|------|------|------|
| **信令服务器** | ✅ 完成 | FastAPI + WebSocket，Token认证正常 |
| **Windows端** | ✅ 完成 | 屏幕捕获、WebRTC、键鼠模拟 |
| **Android代码** | ✅ 完成 | Flutter + WebRTC客户端 |
| **GitHub Actions** | ⏳ 调试中 | 正在解决构建依赖问题 |

## 使用说明

1. Windows端运行后显示6位Token
2. Android APP输入Token连接
3. 手机端显示Windows桌面，触摸控制鼠标

## 下一步

1. 等待GitHub Actions构建成功
2. 下载APK安装到手机测试
3. 如有问题，根据构建日志修复代码
4. 验证连接功能后继续开发新功能
