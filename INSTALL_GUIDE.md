# ADB 安装与连接指南

## 本地构建APK

### 方法1：使用命令行（推荐）
```bash
cd E:\aiprojects\RemoteDesktop\android_remote

# 检查Gradle是否可用
gradle --version

# 如果不可用，下载Gradle
# 访问 https://gradle.org/releases/ 下载Gradle 8.0+

# 构建APK
gradle assembleRelease

# 或使用wrapper（如果有gradle-wrapper.jar）
./gradlew assembleRelease
```

### 方法2：使用Android Studio
1. 打开Android Studio
2. File -> Open -> 选择 `E:\aiprojects\RemoteDesktop\android_remote`
3. 等待Gradle同步完成
4. Build -> Build Bundle(s) / APK(s) -> Build APK(s)
5. APK位置: `app/build/outputs/apk/release/app-release.apk`

## 传输到手机

### 方法1：USB连接
```bash
# 检查设备连接
adb devices

# 安装APK
adb install app/build/outputs/apk/release/app-release.apk
```

### 方法2：微信传输
直接发送APK文件到手机

### 方法3：云盘
上传到云盘后手机下载

## 连接测试
打开APP，输入：
- Token: `TEST01`
- 服务器: `http://您的Windows_IP:8000`
