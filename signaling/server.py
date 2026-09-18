"""
Remote Desktop Signaling Server
云端信令服务器 - 用于WebRTC握手和房间管理
部署到云端ECS后，Android和Windows通过它交换SDP，建立直连
"""
import os
import sys
import secrets
import string
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Set
from dataclasses import dataclass, field
from enum import Enum

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

# ============ 配置 ============
class Config:
    HOST = os.getenv("SIGN_HOST", "0.0.0.0")
    PORT = int(os.getenv("SIGN_PORT", "8000"))
    TOKEN_LENGTH = int(os.getenv("TOKEN_LENGTH", "6"))
    ROOM_EXPIRE_MINUTES = int(os.getenv("ROOM_EXPIRE", "30"))
    MAX_ROOMS = int(os.getenv("MAX_ROOMS", "100"))
    
    # STUN服务器（Google免费）
    STUN_SERVERS = [
        "stun:stun.l.google.com:19302",
        "stun:stun1.l.google.com:19302",
    ]
    
    # TURN服务器（可选，如果STUN穿透失败）
    TURN_SERVER = os.getenv("TURN_SERVER", "")
    TURN_USER = os.getenv("TURN_USER", "")
    TURN_PASS = os.getenv("TURN_PASS", "")


# ============ 数据模型 ============
class Role(str, Enum):
    HOST = "host"       # Windows端
    CLIENT = "client"   # Android端


@dataclass
class Room:
    room_id: str
    token: str
    created_at: datetime
    expires_at: datetime
    
    host_ws: Optional[WebSocket] = None
    client_ws: Optional[WebSocket] = None
    host_connected: bool = False
    client_connected: bool = False
    
    # WebRTC ICE候选和SDP
    host_offer: Optional[str] = None
    client_answer: Optional[str] = None
    
    # 连接状态
    state: str = "waiting"  # waiting, connecting, connected, closed
    
    # 已连接的WebSocket集合（支持多客户端）
    _clients: Set[WebSocket] = field(default_factory=set)
    
    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.expires_at


# ============ 协议消息定义 ============
class MessageType(str, Enum):
    # 握手
    JOIN_ACK = "join_ack"      # 加入成功确认

    # WebRTC信令
    SDP_OFFER = "sdp_offer"    # 发送SDP Offer
    SDP_ANSWER = "sdp_answer"  # 发送SDP Answer
    ICE_CANDIDATE = "ice_candidate"  # ICE候选

    # 输入控制
    INPUT = "input"            # 触摸/鼠标事件

    # 状态
    CONNECTING = "connecting"  # 正在连接
    CONNECTED = "connected"    # 连接成功
    CLOSED = "closed"          # 连接关闭
    ERROR = "error"            # 错误信息


class Message(BaseModel):
    type: str
    data: dict = field(default_factory=dict)


# ============ 信令服务器 ============
class SignalingServer:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.token_to_room: Dict[str, str] = {}
        self._lock = asyncio.Lock()
        
    async def create_room(self) -> dict:
        """创建新房间"""
        async with self._lock:
            # 清理过期房间
            await self._cleanup_expired()
            
            if len(self.rooms) >= Config.MAX_ROOMS:
                raise RuntimeError("房间数量已达上限")
            
            # 生成唯一Token
            attempts = 0
            while attempts < 100:
                token = self._generate_token()
                if token not in self.token_to_room:
                    break
                attempts += 1
            
            if attempts >= 100:
                raise RuntimeError("无法生成唯一Token")
            
            room_id = secrets.token_hex(8)
            now = datetime.now()
            
            room = Room(
                room_id=room_id,
                token=token,
                created_at=now,
                expires_at=now + timedelta(minutes=Config.ROOM_EXPIRE_MINUTES),
            )
            
            self.rooms[room_id] = room
            self.token_to_room[token] = room_id
            
            return {
                "room_id": room_id,
                "token": token,
                "expires_in_minutes": Config.ROOM_EXPIRE_MINUTES,
                "stun_servers": Config.STUN_SERVERS,
            }
    
    async def _cleanup_expired(self):
        """清理过期房间"""
        now = datetime.now()
        expired = [rid for rid, r in self.rooms.items() if r.is_expired]
        for rid in expired:
            self._remove_room(rid)
    
    def _generate_token(self) -> str:
        """生成6位Token，排除混淆字符"""
        chars = string.ascii_uppercase + string.digits
        safe_chars = [c for c in chars if c not in '0O1Il']
        return ''.join(secrets.choice(safe_chars) for _ in range(Config.TOKEN_LENGTH))
    
    def _remove_room(self, room_id: str):
        """移除房间"""
        if room_id in self.rooms:
            room = self.rooms[room_id]
            if room.token in self.token_to_room:
                del self.token_to_room[room.token]
            del self.rooms[room_id]
    
    async def get_room(self, room_id: str) -> Optional[Room]:
        """获取房间信息"""
        return self.rooms.get(room_id)
    
    async def join_room(self, room_id: str, ws: WebSocket, role: Role):
        """加入房间"""
        room = await self.get_room(room_id)
        if not room:
            raise ValueError(f"房间不存在: {room_id}")
        
        if role == Role.HOST and room.host_connected:
            raise ValueError("Host已连接")
        if role == Role.CLIENT and room.client_connected:
            raise ValueError("Client已连接")
        
        await ws.accept()
        room._clients.add(ws)
        
        if role == Role.HOST:
            room.host_ws = ws
            room.host_connected = True
        else:
            room.client_ws = ws
            room.client_connected = True
        
        # 通知加入成功（只发给自己）
        await ws.send_json({
            "type": MessageType.JOIN_ACK.value,
            "data": {
                "role": role.value,
                "room_id": room_id,
                "token": room.token,
                "stun_servers": Config.STUN_SERVERS,
            }
        })
    
    async def handle_message(self, room_id: str, ws: WebSocket, msg: dict):
        """处理信令消息"""
        room = await self.get_room(room_id)
        if not room or ws not in room._clients:
            return
        
        msg_type = msg.get("type")
        data = msg.get("data", {})
        
        if msg_type == MessageType.SDP_OFFER.value:
            # Host发送SDP Offer给Client
            if room.host_ws == ws:
                room.host_offer = data.get("sdp")
                if room.client_ws and room.client_ws in room._clients:
                    await room.client_ws.send_json({
                        "type": MessageType.SDP_OFFER.value,
                        "data": {"sdp": data["sdp"]}
                    })
        
        elif msg_type == MessageType.SDP_ANSWER.value:
            # Client发送SDP Answer给Host
            if room.client_ws == ws:
                room.client_answer = data.get("sdp")
                if room.host_ws and room.host_ws in room._clients:
                    await room.host_ws.send_json({
                        "type": MessageType.SDP_ANSWER.value,
                        "data": {"sdp": data["sdp"]}
                    })
        
        elif msg_type == MessageType.ICE_CANDIDATE.value:
            # ICE候选转发
            target_ws = room.client_ws if ws == room.host_ws else room.host_ws
            if target_ws and target_ws in room._clients:
                await target_ws.send_json({
                    "type": MessageType.ICE_CANDIDATE.value,
                    "data": data
                })
        
        elif msg_type == MessageType.CONNECTING.value:
            room.state = "connecting"
            # 通知双方
            for client_ws in room._clients:
                await client_ws.send_json({
                    "type": MessageType.CONNECTING.value,
                    "data": {}
                })
        
        elif msg_type == MessageType.INPUT.value:
            # 触摸事件转发（Client → Host）
            if room.client_ws == ws and room.host_ws and room.host_ws in room._clients:
                await room.host_ws.send_json({
                    "type": MessageType.INPUT.value,
                    "data": data
                })

        elif msg_type == MessageType.CLOSED.value:
            room.state = "closed"
    
    async def leave_room(self, ws: WebSocket):
        """离开房间"""
        for room in list(self.rooms.values()):
            if ws not in room._clients:
                continue
            
            room._clients.discard(ws)
            
            is_host = room.host_ws == ws
            is_client = room.client_ws == ws
            
            if is_host:
                room.host_connected = False
                room.host_ws = None
            if is_client:
                room.client_connected = False
                room.client_ws = None
            
            # 通知对方（如果还在线）
            for client_ws in list(room._clients):
                try:
                    await client_ws.send_json({
                        "type": MessageType.CLOSED.value,
                        "data": {"reason": "peer_left"}
                    })
                except Exception:
                    pass
            
            # 不要立即删除房间——等待另一方断开或超时
            # 房间会在_cleanup_expired()中按过期时间清理
            break


# ============ FastAPI应用 ============
app = FastAPI(title="RemoteDesktop Signaling Server")
signaling = SignalingServer()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "rooms": len(signaling.rooms),
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/token", response_model=dict)
async def create_token():
    """创建新连接Token"""
    try:
        result = await signaling.create_room()
        return result
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/room/{room_id}")
async def get_room_status(room_id: str):
    """查询房间状态"""
    room = await signaling.get_room(room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    
    return {
        "room_id": room.room_id,
        "token": room.token,
        "state": room.state,
        "host_connected": room.host_connected,
        "client_connected": room.client_connected,
        "expires_at": room.expires_at.isoformat(),
    }


@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """WebSocket信令通道"""
    # 先获取连接角色（通过查询参数）
    role_param = websocket.query_params.get("role", "client")
    try:
        role = Role(role_param)
    except ValueError:
        role = Role.CLIENT
    
    try:
        await signaling.join_room(room_id, websocket, role)
        
        # 处理消息
        while True:
            data = await websocket.receive_json()
            await signaling.handle_message(room_id, websocket, data)
            
    except WebSocketDisconnect:
        await signaling.leave_room(websocket)
    except Exception as e:
        logging.error(f"Error in room {room_id}: {e}")
        await signaling.leave_room(websocket)


@app.post("/api/cleanup")
async def cleanup_expired_rooms(background_tasks: BackgroundTasks):
    """清理过期房间"""
    await signaling._cleanup_expired()
    return {"remaining": len(signaling.rooms)}


@app.on_event("shutdown")
async def shutdown():
    """服务关闭时清理所有房间"""
    for room in list(signaling.rooms.values()):
        signaling._remove_room(room.room_id)


def main():
    """启动服务器"""
    print("=" * 60)
    print("  RemoteDesktop Signaling Server")
    print("=" * 60)
    print(f"  Host:     {Config.HOST}")
    print(f"  Port:     {Config.PORT}")
    print(f"  STUN:     {Config.STUN_SERVERS}")
    print(f"  Rooms:    {Config.MAX_ROOMS} max")
    print(f"  Expires:  {Config.ROOM_EXPIRE_MINUTES} minutes")
    print("=" * 60)
    print()
    
    uvicorn.run(
        app,
        host=Config.HOST,
        port=Config.PORT,
        log_level="info"
    )


if __name__ == "__main__":
    main()
