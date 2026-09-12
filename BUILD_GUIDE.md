# 远程桌面控制软件 - 完整构建指南

## 🎯 快速开始（推荐）

### 方法1：本地 Flutter 构建（最快）
```bash
cd E:\aiprojects\RemoteDesktop\flutter_remote
flutter pub get
flutter build apk --release
```
**APK 位置**: `flutter_remote/build/app/outputs/flutter-apk/app-release.apk`

### 方法2：Docker 构建
```bash
cd E:\aiprojects\RemoteDesktop
bash build_android.sh
```
**APK 位置**: `output/app-release.apk`

### 方法3：GitHub Actions 自动构建
推送代码到 main 分支会自动触发构建，或在 Actions 页面手动触发。
**查看**: https://github.com/pengg307/remotedesktop/actions

---

## 📋 详细步骤

### 1. 安装 Flutter（如果没有）

#### Windows:
```powershell
# 下载 Flutter SDK
git clone -b stable --depth 1 https://github.com/flutter/flutter.git C:\flutter
$env:PATH = "C:\flutter\bin;$env:PATH"
flutter doctor
```

#### macOS/Linux:
```bash
git clone -b stable --depth 1 https://github.com/flutter/flutter.git ~/flutter
export PATH="$PATH:~/flutter/bin"
flutter doctor
```

### 2. 验证环境
```bash
flutter doctor
# 确保以下项为 ✅:
# - Android license status
# - Android SDK
```

### 3. 构建 APK
```bash
cd E:\aiprojects\RemoteDesktop\flutter_remote
flutter pub get
flutter build apk --release
```

### 4. 传输 APK 到手机
```bash
# USB 传输
adb install build/app/outputs/flutter-apk/app-release.apk

# 或微信/QQ传输文件
```

---

## 📱 连接测试

### 1. 启动 Windows 端
```bash
cd E:\aiprojects\RemoteDesktop\pyhost
uv run python main.py --token TEST01
```

### 2. 启动信令服务器
```bash
cd E:\aiprojects\RemoteDesktop\signaling
uv run python main.py
```

### 3. 打开手机 APP
- Token: `TEST01`
- 服务器地址: `http://您的Windows_IP:8000`
- 点击连接

---

## 🔧 Docker 构建详解

### 前提条件
- 已安装 Docker Desktop
- Docker 服务正在运行

### 构建命令
```bash
cd E:\aiprojects\RemoteDesktop
bash build_android.sh
```

### 自定义构建
```bash
# 指定 Flutter 版本
docker build --build-arg FLUTTER_VERSION=3.16.0 -t remote-desktop-android .

# 只构建不运行
docker build -t remote-desktop-android .

# 运行容器获取 APK
docker run --rm -v $(pwd)/output:/output remote-desktop-android
```

---

## ❓ 常见问题

### Q1: flutter pub get 失败
```bash
# 清除缓存重试
flutter clean
flutter pub cache repair
flutter pub get
```

### Q2: Gradle 构建失败
```bash
# 更新 Gradle
cd flutter_remote/android
./gradlew wrapper --gradle-version 8.0
```

### Q3: Docker 构建超时
```bash
# 增加超时时间
docker build --network=host -t remote-desktop-android .
```

### Q4: APK 安装失败
- 开启手机的"未知来源"安装权限
- 确保 APK 未被损坏
- 尝试卸载旧版本后重新安装

---

## 📊 项目状态

| 组件 | 状态 | 端口/Token |
|------|------|-----------|
| Windows端 | ✅ 运行中 | Token: TEST01 |
| 信令服务器 | ✅ 运行中 | :8000 |
| Android客户端 | ⏳ 待构建 | - |
| GitHub仓库 | ✅ 已推送 | - |

---

## 🔗 相关链接
- **GitHub Actions**: https://github.com/pengg307/remotedesktop/actions
- **代码仓库**: https://github.com/pengg307/remotedesktop
- **Flutter文档**: https://flutter.dev/docs
