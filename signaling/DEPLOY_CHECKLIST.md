# Remote Desktop 信令服务器 - 部署清单

## 已完成
- ✅ server.py (395行) - FastAPI WebSocket信令服务器
- ✅ requirements.txt - Python依赖
- ✅ Dockerfile - Docker部署配置
- ✅ Procfile - Railway部署配置
- ✅ .gitignore - Git忽略规则
- ✅ DEPLOY.md - 部署文档
- ✅ test_e2e.py - 端到端测试脚本
- ✅ GitHub Actions工作流

## 待部署

### 方式1: Railway（推荐，最简单）
1. 访问 https://railway.app
2. 用GitHub登录
3. New Project → Deploy from GitHub repo
4. 选择仓库 `pengg307/remotedesktop`
5. 设置环境变量: `SIGN_PORT=8000`
6. Railway自动部署，获得URL: `https://xxx.railway.app`

### 方式2: Fly.io
```bash
fly apps create remotedesk-signaling
fly deploy
```

### 方式3: Render
1. 访问 https://render.com
2. New Web Service → 连接GitHub
3. Root Directory: `signaling`
4. Build: `pip install -r requirements.txt`
5. Start: `uvicorn server:app --host 0.0.0.0 --port $PORT`

## 部署后验证
```bash
curl https://你的服务-url/api/health
curl -X POST https://你的服务-url/api/token
```

成功后告诉我URL，我来修改Windows端接入。