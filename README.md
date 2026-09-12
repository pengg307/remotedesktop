# 远程桌面控制软件

Android手机 → Windows电脑 远程桌面控制

## 技术栈

- **Windows端**: Python 3.11 + mss + aiortc (WebRTC)
- **Android端**: Flutter + flutter_webrtc
- **信令服务器**: Python FastAPI + WebSocket

## 快速开始

### 本地运行（已完成）

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

**已创建的 Workflow**: `.github/workflows/build-apk.yml`

**触发条件**:
- 推送到 main/master 分支
- 手动触发 (workflow_dispatch)

**构建步骤**:
1. Checkout 代码
2. 设置 Java 17
3. 设置 Flutter 3.16.0
4. 构建 release APK
5. 上传 artifact (保留30天)

## 下一步：推送到GitHub

### 步骤1: 创建 GitHub 仓库

访问 https://github.com/new 创建两个仓库：

**仓库1 - 主项目**:
- Name: `remote-desktop`
- Visibility: 公开或私有
- 不要初始化 README

**仓库2 - Flutter客户端**:
- Name: `flutter-remote-desktop`
- Visibility: 公开或私有
- 不要初始化 README

### 步骤2: 推送代码

```bash
# 推送主项目
cd E:\aiprojects\RemoteDesktop
git remote add origin https://github.com/pengg307/remote-desktop.git
git push -u origin main

# 推送Flutter子项目
cd E:\aiprojects\RemoteDesktop\flutter_remote
git remote add origin https://github.com/pengg307/flutter-remote-desktop.git
git push -u origin main
```

### 步骤3: 查看构建

推送后自动触发 GitHub Actions，在仓库的 **Actions** 标签页查看构建进度。

构建完成后下载 APK artifact：
- 路径: `build/app/outputs/flutter-apk/app-release.apk`
- 安装: `adb install app-release.apk`

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
│   ├── .github/workflows/
│   │   └── build-apk.yml  # GitHub Actions workflow
│   └── pubspec.yaml
├── Dockerfile           # Docker构建配置
├── build_android.sh     # 本地Docker构建脚本
└── README.md
```

## 功能状态

| 模块 | 状态 | 说明 |
|------|------|------|
| **信令服务器** | ✅ 完成 | FastAPI + WebSocket，Token认证正常 |
| **Windows端** | ✅ 完成 | 屏幕捕获、WebRTC、键鼠模拟 |
| **Android代码** | ✅ 完成 | Flutter + WebRTC客户端 |
| **GitHub Actions** | ✅ 配置好 | 自动构建APK |
| **推送到GitHub** | ⏳ 待操作 | 需要你创建仓库并推送 |

## 使用说明

1. Windows端运行后显示6位Token（如 `ABCD12`）
2. Android APP输入Token连接
3. 手机端显示Windows桌面，触摸控制鼠标
