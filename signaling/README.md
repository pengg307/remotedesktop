# 云端信令服务器 - 使用说明

## 文件结构
```
signaling/
├── server.py        # 信令服务器主代码
├── start_server.py  # 启动入口（读取环境变量）
├── requirements.txt # Python依赖
├── test_server.py   # 测试脚本
├── start.sh         # Linux启动脚本
├── start.bat        # Windows启动脚本
└── DEPLOY.md        # 完整部署文档
```

## 快速启动（本地测试）

```bash
cd E:/aiprojects/RemoteDesktop/signaling/
pip install -r requirements.txt
python test_server.py
```

## 云端部署步骤

### 1. 上传到ECS
```bash
scp -r signaling/ root@你的服务器IP:/opt/remotedesktop/
```

### 2. 在云端启动
```bash
ssh root@你的服务器IP
cd /opt/remotedesktop/signaling/
pip install -r requirements.txt
python start_server.py
```

### 3. 验证
```bash
curl http://你的服务器IP:8000/api/health
curl -X POST http://你的服务器IP:8000/api/token
```

## API接口

### 创建房间
```bash
curl -X POST http://你的服务器IP:8000/api/token
# 返回: {"room_id": "...", "token": "XY7Z9P", "expires_in_minutes": 30}
```

### WebSocket连接
- Windows端: `ws://服务器IP:8000/ws/{room_id}?role=host`
- Android端: `ws://服务器IP:8000/ws/{room_id}?role=client`

### 消息协议
```json
{
  "type": "join|sdp_offer|sdp_answer|ice_candidate|connecting|closed",
  "data": {...}
}
```

## 下一步

1. 先在云端部署测试连通性
2. 如果通，修改pyhost/host.py使用云端信令
3. 如果不通，考虑其他方案（ngrok/公网穿透）