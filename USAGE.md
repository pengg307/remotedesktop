# Remote Desktop 使用指南

## Railway部署

### 1. 自动启动
- ✅ Railway部署后**自动启动**，不需要手动运行
- ✅ 每次GitHub push都会自动重新部署（如果配置了CI）
- ✅ 获取到URL后直接可用

### 2. 部署步骤
```
1. git push origin main
2. railway.app → New Project → Deploy from GitHub
3. 选 remotedesktop 仓库
4. 设置环境变量 SIGN_PORT=8000
5. 等待2分钟自动部署完成
6. 复制服务URL
```

---

## 本地测试流程

### 方案A：本地信令服务器 + Windows + Android（同一网络）
```bash
# 终端1：启动信令服务器
cd E:/aiprojects/RemoteDesktop/signaling
.venv/Scripts/python.exe start_server.py

# 终端2：启动Windows主机
cd E:/aiprojects/RemoteDesktop/pyhost
.venv/Scripts/python.exe host.py --signaling http://localhost:8000
```

### 方案B：云端信令服务器 + Windows + Android（推荐）
```bash
# Windows主机连接云端信令
python host.py --signaling https://你的railway-url.up.railway.app
```

---

## Android APP 开发状态

| 功能 | 状态 |
|------|------|
| UI界面 | ✅ 完成 |
| Token输入 | ✅ 完成 |
| 信令连接 | ⏳ 开发中 |
| WebRTC视频显示 | ⏳ 开发中 |
| 触摸控制鼠标 | ⏳ 开发中 |

---

## 下一步操作

### 你现在需要：
1. **部署信令服务器到Railway**
2. **把URL发给我**

### 我收到URL后会：
1. 修改 `pyhost/host.py` 使用云端URL
2. 测试Windows端连接
3. 继续开发Android端功能

---

## 常见问题

**Q: Railway免费吗？**
A: 有免费额度，足够测试。生产用需要付费。

**Q: Android APP怎么测试？**
A: 目前还需要开发完整的WebRTC和视频渲染，这部分我来做。

**Q: 本地服务器怎么关？**
A: Ctrl+C 或 kill进程