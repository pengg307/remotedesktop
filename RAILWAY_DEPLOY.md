# Railway 部署指南

## 1. 获取Railway API Key

1. 登录 **https://railway.com**
2. 点击右上角头像 → **Settings**
3. 左侧菜单 → **API Keys**
4. 点击 **Generate New Token**
5. 复制Token（格式类似: `rail_v1_xxxxxxxx`）

## 2. 设置环境变量

在Terminal中运行：

```bash
# 临时设置（当前会话有效）
export RAILWAY_API_KEY='你的token'

# 或者写入临时文件
echo 'RAILWAY_API_KEY=你的token' > ~/.railway.env
```

Windows用户：
```cmd
set RAILWAY_API_KEY=你的token
```

## 3. 安装Railway CLI（可选）

```bash
# 方式1: npm
npm install -g @railway/cli

# 方式2: PowerShell
irm https://rails.cli/install.ps1 | iex
```

## 4. 部署步骤

### 方式A: 使用CLI（推荐）

```bash
cd E:/aiprojects/RemoteDesktop/signaling

# 登录
railway login

# 初始化项目
railway init
# 选择 "Create new project"

# 设置环境变量
railway variables set SIGN_PORT=8000

# 部署
railway up
```

### 方式B: 网页部署（最简单）

1. 打开 **https://railway.com**
2. 点击 **New Project**
3. 选择 **Deploy from GitHub repo**
4. 授权访问GitHub，选择 `pengg307/remotedesktop`
5. 选择分支 `main`
6. 设置环境变量：
   - `SIGN_PORT=8000`
7. 点击 **Deploy**

## 5. 部署后配置

部署成功后，Railway会给你一个URL：
```
https://remotedesk-signaling.up.railway.app
```

把这个URL发给Android和Windows端使用。

## 6. 测试连接

```bash
curl https://你的-railway-url/api/health
curl -X POST https://你的-railway-url/api/token
```

---

## ⚠️ 常见问题

### Q: WebSocket连接超时？
Railway免费版有5分钟空闲自动休眠，首次访问需要等待10-30秒。

### Q: 国内访问慢？
Railway服务器在新加坡，比Render快很多。

### Q: 免费额度够用吗？
- 500MB内存
- 无限带宽
- 够用！
