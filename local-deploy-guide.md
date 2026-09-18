# 本地运行 + Cloudflare Tunnel 部署指南

## 方案对比

| 方式 | 优点 | 缺点 |
|------|------|------|
| ngrok | 简单快速 | 需要注册获取Token |
| Cloudflare Tunnel | 完全免费，无需Token | 需要Cloudflare账号 |
| Oracle Cloud VM | 永久免费VPS | 需要国外信用卡 |
| Railway/Fly.io | 托管服务 | 收费或免费额度有限 |

---

## 方案1: 本地运行 + ngrok（推荐测试）

### 1. 注册ngrok账号
- 打开 https://dashboard.ngrok.com/signup
- 注册后进入 Dashboard
- 复制 **Authtoken**

### 2. 安装ngrok
```bash
# Windows
winget install ngrok.ngrok

# 或手动下载
# https://ngrok.com/download
```

### 3. 配置ngrok
```bash
ngrok config add-authtoken YOUR_TOKEN
```

### 4. 运行信令服务器
```bash
cd E:/aiprojects/RemoteDesktop/signaling
python main_ngrok.py
```

### 5. 获取公网URL
输出类似：
```
🌐 公网URL: https://abc123.ngrok-free.app
```

把这个URL给Android端使用。

---

## 方案2: Cloudflare Tunnel（完全免费）

### 1. 注册Cloudflare
- 打开 https://dash.cloudflare.com/sign-up
- 免费账号即可

### 2. 安装cloudflared
```bash
winget install cloudflare.cloudflared
# 或
npm install -g global-cloudflare-tunnel
```

### 3. 运行隧道
```bash
# 方式A: 直接隧道
cloudflared tunnel --url http://localhost:8000

# 方式B: 持久隧道
cloudflared tunnel login  # 验证域名所有权
cloudflared tunnel create remotedesk
cloudflared tunnel route dns remotedesk remotedesk.yourdomain.com
cloudflared tunnel run remotedesk
```

### 4. 获取URL
```
https://remotedesk.trycloudflare.com
```

---

## 方案3: Oracle Cloud永久免费VPS

### 1. 注册账号
- https://www.oracle.com/cloud/free/
- 需要**国外信用卡**（Visa/MasterCard）
- 区域选 **Asia Pacific - Singapore**

### 2. 创建免费VPS
- Compute → Instances → Create Instance
- Ubuntu 22.04, Arm-based, 1 OCPU, 1GB RAM
- 免费2台

### 3. SSH连接部署
```bash
# 连接
ssh -i ~/.ssh/id_rsa ubuntu@YOUR_PUBLIC_IP

# 安装依赖
sudo apt update && sudo apt install python3-pip git -y

# 克隆代码
git clone https://github.com/pengg307/remotedesktop.git
cd remotedesktop/signaling

# 运行
pip3 install -r requirements.txt
nohup python3 start_server.py > server.log 2>&1 &
```

---

## 推荐顺序

1. **先用ngrok/Cloudflare Tunnel测试**（最快）
2. **确认功能正常后**，再考虑Oracle Cloud长期方案

---

你有ngrok Token吗？还是需要我帮你配置Cloudflare Tunnel？
