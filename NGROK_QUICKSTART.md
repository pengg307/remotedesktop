# ngrok 快速部署指南

## 为什么用ngrok？

- ✅ 完全免费（临时测试）
- ✅ 无需注册复杂流程
- ✅ 5分钟搞定
- ✅ 支持WebSocket

---

## 第一步：注册ngrok账号

1. 打开 https://dashboard.ngrok.com/signup
2. 用邮箱注册（或GitHub登录）
3. 登录后进入Dashboard

## 第二步：获取Auth Token

1. 点击左侧菜单 **Getting Started**
2. 复制 **Authtoken**（格式：`2bXz8...`）

## 第三步：安装ngrok

### Windows：
```bash
winget install ngrok.ngrok
```

### 或手动下载：
- 打开 https://ngrok.com/download
- 下载 Windows 版本
- 解压到任意目录（如 `C:\ngrok\`）

## 第四步：配置ngrok

```bash
# 设置token
ngrok config add-authtoken YOUR_TOKEN

# 验证配置
ngrok config add-authtoken 2M7x...
```

## 第五步：运行信令服务器 + ngrok隧道

### 方式1: 使用我们的脚本（推荐）

```bash
cd E:/aiprojects/RemoteDesktop/signaling
set NGROK_AUTH_TOKEN=你的token
python main_ngrok.py
```

### 方式2: 手动启动

**终端1 - 运行信令服务器：**
```bash
cd E:/aiprojects/RemoteDesktop/signaling
python -m uvicorn server:app --host 127.0.0.1 --port 8000
```

**终端2 - 启动ngrok隧道：**
```bash
ngrok http 8000
```

## 第六步：获取公网URL

ngrok会输出类似：
```
Forwarding  https://abc123.ngrok-free.app -> http://localhost:8000
```

**复制这个URL给Android端使用！**

---

## Android端配置

在Android APP中输入：
- 信令服务器地址：`https://abc123.ngrok-free.app`
- Token：从API获取（`POST /api/token`）

---

## 注意事项

⚠️ **ngrok免费版限制：**
- 每次重启URL会变
- 有连接数限制
- 适合测试，不适合生产

✅ **生产环境建议：**
- Oracle Cloud免费VPS + coturn
- 或付费TURN服务（twilio等）

---

## 验证连接

部署成功后测试：
```bash
curl https://你的ngrok-url/api/health
```

应该返回：
```json
{"status":"ok","rooms":0,"timestamp":"..."}
```
