# Android APK 构建指南

## 方法一：Android Studio（推荐）

### 步骤
1. 打开 Android Studio
2. File → Open
3. 选择目录: `E:/aiprojects/RemoteDesktop/android_remote`
4. 等待Gradle同步完成（可能需要下载依赖）
5. 点击 Run 按钮（绿色三角形）或菜单 Run → Run 'app'
6. 选择你的设备（手机或模拟器）
7. 等待安装完成

### 输出位置
```
E:/aiprojects/RemoteDesktop/android_remote/app/build/outputs/apk/debug/app-debug.apk
```

---

## 方法二：命令行构建

### 前置条件
- 已安装 Android SDK
- 已设置 ANDROID_HOME 环境变量

### 步骤
```bash
cd E:/aiprojects/RemoteDesktop/android_remote
./gradlew assembleDebug
```

或直接双击运行:
```
build_apk.bat
```

---

## 方法三：导入现有项目

如果之前有用Android Studio打开过这个项目：

1. 打开 Android Studio
2. File → Open
3. 选择 `E:/aiprojects/RemoteDesktop/android_remote`
4. 等待同步完成
5. 点击 Run

---

## 常见问题

### Q: Gradle同步失败
**A:** 检查网络连接，可能是maven仓库访问问题。可以尝试：
- 使用VPN
- 或在gradle.properties中配置国内镜像

### Q: 构建错误
**A:** 尝试：
1. Build → Clean Project
2. Build → Rebuild Project
3. File → Invalidate Caches / Restart

### Q: 安装失败
**A:** 
1. 在手机上开启"开发者选项"和"USB调试"
2. 用数据线连接手机
3. 在Android Studio中选择你的设备点击Run

---

## 测试APP

构建成功后，APP功能：

1. **输入服务器地址**: 填入你的Railway URL
2. **输入Token**: 从信令服务器获取的6位Token
3. **点击连接**: 等待建立WebRTC连接
4. **显示屏幕**: 连接成功后会显示Windows屏幕

---

## 后续开发

收到你的云端URL后，我会：
1. 修改Windows端代码接入云端
2. 测试真实视频流
3. 优化Android端触摸控制