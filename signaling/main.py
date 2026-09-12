"""
Windows远程桌面服务 - 信令服务器
功能：Token生成、连接握手、房间管理
"""
import os
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="RemoteDesktop Signaling Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 内存存储房间信息
rooms: dict[str, dict] = {}
# Token -> 房间ID映射
token_to_room: dict[str, str] = {}


def generate_token(length: int = 6) -> str:
    """生成6位Token，排除混淆字符"""
    chars = string.ascii_uppercase + string.digits
    safe_chars = [c for c in chars if c not in '0O1Il']
    return ''.join(secrets.choice(safe_chars) for _ in range(length))


@app.post("/api/token")
async def create_token():
    """创建新连接Token"""
    token = generate_token()
    room_id = secrets.token_hex(8)
    
    rooms[room_id] = {
        "token": token,
        "created_at": datetime.now().isoformat(),
        "expires_at": (datetime.now() + timedelta(minutes=30)).isoformat(),
        "host_connected": False,
        "client_connected": False,
    }
    token_to_room[token] = room_id
    
    return {
        "token": token,
        "room_id": room_id,
        "expires_in_minutes": 30
    }


@app.get("/api/room/{room_id}")
async def get_room_status(room_id: str):
    """查询房间状态"""
    if room_id not in rooms:
        raise HTTPException(status_code=404, detail="Room not found")
    return rooms[room_id]


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket信令通道"""
    if room_id not in rooms:
        await websocket.close(code=4004, reason="Invalid room")
        return
    
    await websocket.accept()
    room = rooms[room_id]
    
    try:
        while True:
            data = await websocket.receive_json()
            
            # 转发信令数据
            # 实际生产中需要维护客户端连接列表
            # 这里简化处理，直接打印
            print(f"[Room {room_id}] Received: {data.get('type')}")
            
            # 回传给发送方确认
            await websocket.send_json({"type": "ack", "status": "ok"})
            
    except WebSocketDisconnect:
        print(f"[Room {room_id}] Client disconnected")
    except Exception as e:
        print(f"[Room {room_id}] Error: {e}")
        await websocket.close(code=1011, reason=str(e))


@app.post("/api/cleanup")
async def cleanup_expired():
    """清理过期房间"""
    now = datetime.now()
    expired = []
    
    for room_id, room in rooms.items():
        expires_at = datetime.fromisoformat(room["expires_at"])
        if now > expires_at:
            expired.append(room_id)
    
    for room_id in expired:
        del rooms[room_id]
        # 清理对应的token映射
        token = rooms.get(room_id, {}).get("token") if room_id in rooms else None
        if token and token in token_to_room:
            del token_to_room[token]
    
    return {"cleaned": len(expired), "remaining": len(rooms)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
