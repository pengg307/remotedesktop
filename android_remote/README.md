# Remote Desktop Android APP

## 功能
- 输入6位Token连接远程桌面
- 显示Windows屏幕（WebRTC视频流）
- 触摸控制鼠标
- 云端信令服务器集成

## 构建步骤

### 方法1：Android Studio（推荐）
1. 打开 Android Studio
2. File → Open → 选择 `E:/aiprojects/RemoteDesktop/android_remote`
3. 等待Gradle同步完成
4. Run → Run 'app' 或 Build → Build APK

### 方法2：命令行构建
```bash
cd E:/aiprojects/RemoteDesktop/android_remote
./gradlew assembleDebug
```

APK位置: `app/build/outputs/apk/debug/app-debug.apk`

## 安装
```bash
adb install app/build/outputs/apk/debug/app-debug.apk
```

## 配置
首次运行需要输入：
1. 信令服务器URL（Railway部署后获得）
2. 6位Token

## 权限
- 网络访问
- 音频录制（可选）
- 相机（可选）

## 技术栈
- Kotlin
- WebRTC (org.webrtc:google-webrtc)
- OkHttp (WebSocket)
- Material Design
