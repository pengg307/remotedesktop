# 远程桌面控制软件 - GitHub推送说明

## GitHub Actions Workflow 已创建

**文件位置**: `flutter_remote/.github/workflows/build-apk.yml`

## 工作流程

当代码推送到GitHub后，会自动触发以下构建流程：

1. ✅ Checkout 代码
2. ✅ 设置 Java 17 (Temurin)
3. ✅ 设置 Flutter 3.16.0 stable
4. ✅ 获取依赖 (flutter pub get)
5. ✅ 构建 release APK
6. ✅ 上传 APK artifact (保留30天)

## 手动推送到GitHub

由于GitHub仓库需要手动创建，请按以下步骤操作：

### 步骤1: 在GitHub创建仓库
访问 https://github.com/new 创建新仓库：
- Repository name: `remote-desktop`
- Visibility: 公开或私有
- 不要初始化README

### 步骤2: 推送代码
```bash
# 主项目
cd E:\aiprojects\RemoteDesktop
git remote add origin https://github.com/你的用户名/remote-desktop.git
git push -u origin main

# Flutter子项目
cd E:\aiprojects\RemoteDesktop\flutter_remote
git remote add origin https://github.com/你的用户名/flutter-remote-desktop.git
git push -u origin main
```

### 步骤3: 查看构建结果
1. 访问GitHub仓库的Actions标签页
2. 查看 workflow 运行状态
3. 构建完成后下载APK artifact

## 构建产物

- **APK路径**: `build/app/outputs/flutter-apk/app-release.apk`
- **保留时间**: 30天
- **安装方法**:
  ```bash
  adb install app-release.apk
  ```

## 注意事项

1. GitHub Actions免费额度：每月2000分钟（对小型项目足够）
2. APK文件大小限制：100MB以内
3. 如需发布到Google Play，需构建AAB格式
