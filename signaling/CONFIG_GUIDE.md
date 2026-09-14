# RemoteDesktop 信令服务器 - 配置指南

## 📊 当前状态
```
✅ 信令服务器: 运行中
📍 局域网地址: http://192.168.1.3:8000
📱 当前Token: (运行以下命令获取)
   curl -X POST http://localhost:8000/api/token
```

---

## 🔧 ngrok配置步骤

### 步骤1: 注册ngrok账号
1. 打开浏览器访问: https://dashboard.ngrok.com/signup
2. 填写邮箱和密码
3. 验证邮箱

### 步骤2: 获取Auth Token
1. 登录后点击左侧菜单 "Getting Started"
2. 找到 "Authtoken" 部分
3. 点击 "Look for an authtoken?"
4. 复制token值（格式如: `2xYz1234abcDEFghIJKlmno_...`）

### 步骤3: 配置启动脚本
1. 打开文件: `E:\aiprojects\RemoteDesktop\signaling\启动ngrok.bat`
2. 找到第8行:
   ```batch
   set NGROK_AUTH_TOKEN=YOUR_TOKEN_HERE
   ```
3. 替换为你的实际token:
   ```batch
   set NGROK_AUTH_TOKEN=2xYz1234abcDEFghIJKlmno_...
   ```
4. 保存文件

### 步骤4: 启动隧道
双击运行: `启动ngrok.bat`

启动后会显示:
```
✅ 公网URL: https://abc123.ngrok.io
📱 Token: XXXXXX
```

### 步骤5: Android连接
在Android应用中设置:
- **服务器**: `https://abc123.ngrok.io`
- **Token**: 从输出中获取

---

## 📱 WiFi测试（无需ngrok）

如果只想先测试功能：
1. 手机连接与电脑相同的WiFi
2. Android应用设置:
   - 服务器: `http://192.168.1.3:8000`
   - Token: (从API获取)

---

## 🔍 获取新Token
```bash
curl -X POST http://localhost:8000/api/token
```

---

## ⚙️ 启动脚本说明

### 文件位置
- `启动ngrok.bat` - Windows一键启动
- `main_ngrok.py` - Python启动脚本
- `install_ngrok.py` - ngrok自动下载工具

### 环境检查
脚本会自动检查:
- Python是否安装
- uv包管理器
- pyngrok库

---

## 🆘 问题排查

### Q: ngrok启动失败？
A: 检查:
1. Token是否正确
2. 网络连接是否正常
3. 防火墙是否阻止

### Q: Android连接不上？
A: 检查:
1. ngrok URL是否以 `https://` 开头
2. Token是否过期
3. 手机网络是否通畅

### Q: 想要固定ngrok URL？
A: 升级ngrok付费计划，或注册免费账号获取固定子域名

---

## 📝 快速命令

```powershell
# 获取Token
curl -X POST http://localhost:8000/api/token

# 查看局域网地址
ipconfig | findstr "IPv4"

# 测试ngrok连通性
curl -X POST https://xxxx.ngrok.io/api/token
```
