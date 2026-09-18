# Remote Desktop Signaling Server

FastAPI WebSocket信令服务器，用于WebRTC远程桌面握手。

## 功能

- Token生成（6位，排除混淆字符）
- 房间管理（30分钟过期）
- SDP Offer/Answer交换
- ICE候选转发
- 触摸事件转发

## API

```
GET  /api/health          → {"status":"ok","rooms":N}
POST /api/token           → {"room_id":"...","token":"ABC123"}
GET  /api/room/{id}       → 房间状态
WS   /ws/{room_id}?role=host|client  → WebSocket信令通道
```

## 消息格式

```json
{
  "type": "join_ack|sdp_offer|sdp_answer|ice_candidate|input|connecting|closed",
  "data": {...}
}
```

## 部署

### Render（推荐）
1. 打开 https://render.com
2. New + → Web Service
3. 连接GitHub仓库
4. 配置：
   - Root Directory: `signaling/`
   - Build: `pip install -r requirements.txt`
   - Start: `python server.py`
5. 创建后获得URL

### Vercel（备选）
- 可用，但WebSocket支持有限制
- 建议优先Render

## 本地测试

```bash
cd signaling
uvicorn server:app --reload --port 8000
python test_e2e.py
```
