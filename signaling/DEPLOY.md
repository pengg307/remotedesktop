# === Railway Deploy ===
# 1. 在 https://railway.app 注册
# 2. New Project -> Deploy from GitHub repo
# 3. 选择本仓库的 signaling/ 目录
# 4. Railway 会自动检测 FastAPI 并部署
# 5. 部署完成后设置环境变量: SIGN_PORT=8000

# === Fly.io Deploy ===
# 1. 安装 flyctl: winget install fly.cli
# 2. fly auth login
# 3. cd signaling/ && fly launch
# 4. fly deploy

# === Render Deploy ===
# 1. 在 https://render.com 注册
# 2. New Web Service -> 连接GitHub
# 3. Root Directory: signaling
# 4. Build Command: pip install -r requirements.txt
# 5. Start Command: uvicorn server:app --host 0.0.0.0 --port $PORT