# GitHub 推送指南

## 当前状态

✅ 代码已准备好，本地Git仓库已初始化
❌ GitHub仓库未创建或URL不匹配

## 需要做的步骤

### 步骤1: 在GitHub创建仓库

访问 https://github.com/new 创建两个仓库：

**仓库1 - 主项目**:
- Name: `remote-desktop` (或你喜欢的名字)
- Description: Android远程桌面控制Windows
- Visibility: 公开或私有
- ❌ 不要勾选 "Initialize this repository with a README"

**仓库2 - Flutter客户端**:
- Name: `flutter-remote-desktop` (或你喜欢的名字)
- Description: Flutter远程桌面Android客户端
- Visibility: 公开或私有
- ❌ 不要勾选 "Initialize this repository with a README"

### 步骤2: 告诉我正确的GitHub URL

创建好仓库后，把下面的URL告诉我：
- 主项目URL: `https://github.com/你的用户名/xxx`
- Flutter客户端URL: `https://github.com/你的用户名/xxx`

### 步骤3: 我帮你推送

拿到正确URL后，我会执行：
```bash
# 主项目
git remote set-url origin https://github.com/你的用户名/remote-desktop.git
git push -u origin main

# Flutter子项目
cd flutter_remote
git remote set-url origin https://github.com/你的用户名/flutter-remote-desktop.git
git push -u origin main
```

### 步骤4: GitHub Actions自动构建

推送成功后，GitHub会自动：
1. 触发 workflow
2. 在Ubuntu服务器上构建Flutter项目
3. 生成APK文件
4. 上传为artifact

你可以在仓库的 **Actions** 标签页查看构建进度。

## 注意事项

- GitHub Actions免费额度：每月2000分钟
- APK artifact保留30天
- 构建完成后从Artifacts下载APK安装到手机
