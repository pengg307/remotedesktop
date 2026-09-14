# RemoteDesktop 信令服务器 - ngrok配置指南

## 当前状态
```
✅ 信令服务器: 运行中
   局域网: http://192.168.1.3:8000
   Token: 485Q7V (已生成)
❌ ngrok隧道: 未配置
```

## 为什么需要ngrok？
手机用SIM卡网络，电脑在局域网，两者不在同一网络。
ngrok创建一个公网URL，让手机能访问电脑的服务。

---

## 方案A: 手动配置ngrok（推荐）

### 步骤1: 注册ngrok账号
1. 打开浏览器: https://dashboard.ngrok.com/signup
2. 填写邮箱和密码
3. 验证邮箱

### 步骤2: 获取Auth Token
1. 登录后点击 "Getting Started"
2. 找到 "Authtoken" 部分
3. 点击 "Look for an authtoken?"
4. 复制token: `2xYz1234abcDEFghIJKlmno...`

### 步骤3: 下载ngrok
1. 访问: https://ngrok.com/download
2. 选择 "Windows 64-bit"
3. 下载并解压到: `E:\ngrok`

### 步骤4: 配置ngrok
打开CMD，运行:
```cmd
cd E:\ngrok
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### 步骤5: 启动隧道
```cmd
cd E:\ngrok
ngrok http 8000
```

你会看到:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

### 步骤6: Android连接
- 服务器: `https://abc123.ngrok.io`
- Token: 从API获取

---

## 方案B: 使用Python脚本

### 1. 设置环境变量
```powershell
# PowerShell
$env:NGROK_AUTH_TOKEN="YOUR_TOKEN"

# CMD
set NGROK_AUTH_TOKEN=YOUR_TOKEN
```

### 2. 运行启动脚本
```bash
cd E:\aiprojects\RemoteDesktop\signaling
uv run python main_ngrok.py
```

---

## 方案C: GitHub Actions自动配置

### 1. 运行workflow
访问: https://github.com/pengg307/remotedesktop/actions/workflows/setup-ngrok.yml
点击 "Run workflow"，输入ngrok token

### 2. 获取公网URL
Workflow完成后会显示ngrok URL

---

## 快速测试（WiFi）

如果现在只想测试功能：
1. 手机连接与电脑相同的WiFi
2. Android应用设置:
   - 服务器: `http://192.168.1.3:8000`
   - Token: 485Q7V

---

## 验证服务

```bash
# 测试信令服务器
curl -X POST http://localhost:8000/api/token

# 期望返回:
# {"token":"XXXXXX","room_id":"...","expires_in_minutes":30}
```

---

## 问题排查

### Q: ngrok连接失败？
A: 检查:
- Token是否正确
- 网络连接是否正常
- 防火墙是否阻止

### Q: Android连接不上？
A: 检查:
- ngrok URL是否正确（https://开头）
- Token是否过期
- 手机网络是否通畅

### Q: 想要固定URL？
A: 升级ngrok到付费计划，或注册免费账号获取子域名

---

## 下一步

**请选择:**
1. 手动配置ngrok（推荐）
2. 使用Python脚本
3. 先用WiFi测试局域网
4. 其他问题
