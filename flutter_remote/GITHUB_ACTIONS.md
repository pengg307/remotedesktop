# GitHub Actions: Build Android APK

## Workflow 配置
文件: `.github/workflows/build-apk.yml`

## 触发条件
- 推送到 main/master 分支
- Pull request 到 main/master
- 手动触发 (workflow_dispatch)

## 构建步骤
1. Checkout 代码
2. 设置 Java 17 (Temurin)
3. 设置 Flutter 3.16.0 stable
4. 获取依赖 (flutter pub get)
5. 构建 release APK
6. 上传 APK 作为 artifact (保留30天)

## 使用方法
1. 推送代码到 GitHub:
   ```bash
   git push origin main
   ```
2. 在 GitHub Actions 页面查看构建进度
3. 构建完成后下载 APK artifact

## Artifact 位置
- APK: `build/app/outputs/flutter-apk/app-release.apk`
- 下载后安装到Android设备:
  ```bash
  adb install app-release.apk
  ```
