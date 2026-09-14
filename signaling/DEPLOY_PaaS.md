# Remote Desktop 云端部署指南（PaaS方案）

## 方案对比

| 平台 | 免费额度 | WebSocket支持 | 部署难度 | 推荐度 |
|------|----------|---------------|----------|--------|
| **Railway** | 500MB内存/月 | ✅ 原生支持 | ⭐ 最简单 | ⭐⭐⭐⭐⭐ |
| **Fly.io** | 3个微VM/月 | ✅ 原生支持 | ⭐⭐ | ⭐⭐⭐⭐ |
| **Render** | 750MB内存/月 | ✅ 支持 | ⭐⭐ | ⭐⭐⭐ |
| **PythonAnywhere** | 有免费层 | ⚠️ 有限支持 | ⭐ | ⭐⭐ |

---

## 方案1: Railway（最推荐）

### 步骤

#### 1. 注册账号
- 访问 https://railway.app
- 用GitHub登录

#### 2. 创建项目
```bash
# 方式1: 从GitHub部署（推荐）
# 先把代码推送到GitHub仓库

# 方式2: 本地上传
# 在Railway网页点击 "New Project" -> "Deploy from GitHub"
```

#### 3. 准备部署文件

**Procfile**（必需）：
```
web: uvicorn server:app --host 0.0.0.0 --port $PORT
```

**Dockerfile**（备选，如果Railway不支持直接部署）：
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 4. 环境变量配置
在Railway控制台添加：
```
SIGN_PORT=8000
SIGN_HOST=0.0.0.0
TOKEN_LENGTH=6
ROOM_EXPIRE=30
MAX_ROOMS=100
```

#### 5. 部署
- Railway会自动检测FastAPI应用
- 点击 "Deploy"
- 部署完成后获得URL: `https://your-app-railway.app`

#### 6. 验证
```bash
curl https://your-app-railway.app/api/health
curl -X POST https://your-app-railway.app/api/token
```

---

## 方案2: Fly.io

### 步骤

#### 1. 安装Fly CLI
```bash
# Windows
winget install fly.cli

# 或下载
https://fly.io/docs/hands-on/install-flyctl/
```

#### 2. 登录
```bash
fly auth login
```

#### 3. 初始化
```bash
cd E:/aiprojects/RemoteDesktop/signaling/
fly launch
```

#### 4. 配置 fly.toml
```toml
app = 'remotedesk-signaling'
primary_region = 'sin'  # 新加坡，离中国近

[build]
  dockerfile = 'Dockerfile'

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[vm]]
  memory = '256mb'
  cpu_kind = 'shared'
  cpus = 1
```

#### 5. 创建Dockerfile
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 6. 部署
```bash
fly apps create
fly deploy
```

#### 7. 验证
```bash
curl https://your-app.fly.dev/api/health
```

---

## 方案3: Render（最简单）

### 步骤

#### 1. 注册
- 访问 https://render.com
- GitHub登录

#### 2. 创建Web Service
- 连接GitHub仓库
- 选择 `signaling/` 目录
- 构建命令: `pip install -r requirements.txt`
- 启动命令: `uvicorn server:app --host 0.0.0.0 --port $PORT`

#### 3. 环境变量
```
SIGN_PORT=8000
SIGN_HOST=0.0.0.0
```

#### 4. 部署
- Render自动检测FastAPI
- 一键部署
- 获得URL: `https://your-app.onrender.com`

---

## 部署后使用

### 获取你的服务地址
部署成功后，你会得到一个URL，类似：
- Railway: `https://remotedesk-signal.railway.app`
- Fly.io: `https://remotedesk-signal.fly.dev`
- Render: `https://remotedesk-signal.onrender.com`

### 修改Windows端配置
```python
# pyhost/host.py 或 signaling_client.py
SIGNALING_SERVER = "wss://your-app.railway.app"  # 注意用wss://
```

### 测试连通性
```bash
curl https://your-app.railway.app/api/health
curl -X POST https://your-app.railway.app/api/token
```

---

## 推荐方案

**首选 Railway**：
- 免费额度够用（500MB内存）
- WebSocket原生支持
- 部署最简单（GitHub连接即自动部署）
- 国内访问速度快

**次选 Render**：
- 完全免费（但冷启动慢）
- 部署最简单
- 适合测试

---

## 注意事项

1. **免费额度限制**:
   - Railway: 500MB内存，无限带宽
   - Render: 750MB内存，免费版会休眠
   - Fly.io: 3个微VM，200GB带宽

2. **WebSocket超时**:
   - PaaS平台可能有连接超时限制
   - 建议设置合理的ping/pong间隔

3. **生产环境**:
   - 如果流量大，考虑升级到付费计划
   - Railway付费：$5/月起
   - 可考虑自建VPS作为备选
