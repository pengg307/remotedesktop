"""
Windows远程桌面主机 - 内置信令服务器模式
功能：屏幕捕获 + WebRTC + 输入模拟 + 本地信令服务器
适用于Tailscale内网环境
"""
import asyncio
import json
import logging
import time
import sys
import os
from typing import Optional
from datetime import datetime, timedelta
import secrets
import string

import mss
from aiortc import RTCPeerConnection, RTCSessionDescription
from av import VideoFrame
import numpy as np
import websockets
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pyhost")


class ScreenCapture:
    """屏幕捕获模块"""
    
    def __init__(self, screen_index: int = 0):
        self.mss = mss.mss()
        self.screen_index = screen_index
        self.info = self._get_screen_info()
        self.last_frame_time = 0
        self.frame_count = 0
        self.fps = 0
        
    def _get_screen_info(self) -> dict:
        """获取屏幕信息"""
        monitors = self.mss.monitors
        if self.screen_index < len(monitors):
            monitor = monitors[self.screen_index]
        else:
            monitor = monitors[0] if monitors else {'left': 0, 'top': 0, 'width': 1920, 'height': 1080}
        
        return {\
            'width': int(monitor.get('width', 1920)),
            'height': int(monitor.get('height', 1080)),
            'left': int(monitor.get('left', 0)),
            'top': int(monitor.get('top', 0)),
        }
    
    def capture(self, quality: int = 85) -> tuple:
        """捕获屏幕并压缩为JPEG"""
        start = time.perf_counter()
        screenshot = self.mss.grab({
            'left': self.info['left'],
            'top': self.info['top'],
            'width': self.info['width'],
            'height': self.info['height'],
        })
        
        buffer = __import__('io').BytesIO()
        from PIL import Image
        img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
        img_rgb = img.convert('RGB')
        
        # 缩放到最大1280
        max_dimension = 1280
        if max(img_rgb.width, img_rgb.height) > max_dimension:
            ratio = max_dimension / max(img_rgb.width, img_rgb.height)
            new_size = (int(img_rgb.width * ratio), int(img_rgb.height * ratio))
            img_rgb = img_rgb.resize(new_size, Image.LANCZOS)
        
        img_rgb.save(buffer, format='JPEG', quality=quality, optimize=True)
        jpeg_data = buffer.getvalue()
        
        elapsed = (time.perf_counter() - start) * 1000
        self.frame_count += 1
        self._update_fps(elapsed)
        
        return jpeg_data, elapsed
    
    def _update_fps(self, last_elapsed: float):
        now = time.time()
        if now - self.last_frame_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_frame_time = now
    
    def get_info(self) -> dict:
        return self.info.copy()


class InputSimulator:
    """输入模拟模块"""
    
    def __init__(self):
        self.user32 = __import__('ctypes').windll.user32
        self.screen_info = self._get_screen_size()
    
    def _get_screen_size(self) -> tuple:
        """获取屏幕尺寸"""
        width = self.user32.GetSystemMetrics(0)
        height = self.user32.GetSystemMetrics(1)
        return (width, height)
    
    def move_mouse(self, x: float, y: float):
        """移动鼠标 (0-100坐标)"""
        sx = int(x / 100 * self.screen_info[0])
        sy = int(y / 100 * self.screen_info[1])
        self.user32.SetCursorPos(sx, sy)
    
    def click(self, x: float, y: float):
        """点击鼠标"""
        self.move_mouse(x, y)
        self.user32.mouse_event(0x0002, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTDOWN
        time.sleep(0.05)
        self.user32.mouse_event(0x0004, 0, 0, 0, 0)  # MOUSEEVENTF_LEFTUP
    
    def right_click(self, x: float, y: float):
        """右键点击"""
        self.move_mouse(x, y)
        self.user32.mouse_event(0x0008, 0, 0, 0, 0)  # MOUSEEVENTF_RIGHTDOWN
        time.sleep(0.05)
        self.user32.mouse_event(0x0010, 0, 0, 0, 0)  # MOUSEEVENTF_RIGHTUP


def generate_token(length: int = 6) -> str:
    """生成6位Token，排除混淆字符"""
    chars = string.ascii_uppercase + string.digits
    safe_chars = [c for c in chars if c not in '0O1Il']
    return ''.join(secrets.choice(safe_chars) for _ in range(length))


class SignalingServer:
    """本地信令服务器"""
    
    def __init__(self, host: 'RemoteDesktopHost'):
        self.host = host
        self.app = FastAPI(title="RemoteDesktop Local Signaling")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self._setup_routes()
        self.server = None
    
    def _setup_routes(self):
        """设置路由"""
        
        @self.app.post("/api/token")
        async def create_token():
            """创建新连接Token"""
            token = generate_token()
            room_id = secrets.token_hex(8)
            
            self.host.rooms[room_id] = {
                "token": token,
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(minutes=30)).isoformat(),
                "host_ws": None,
                "client_ws": None,
            }
            self.host.token_to_room[token] = room_id
            
            return {
                "token": token,
                "room_id": room_id,
                "expires_in_minutes": 30
            }
        
        @self.app.get("/api/room/{room_id}")
        async def get_room_status(room_id: str):
            """查询房间状态"""
            if room_id not in self.host.rooms:
                raise HTTPException(status_code=404, detail="Room not found")
            return self.host.rooms[room_id]
        
        @self.app.websocket("/ws/{room_id}")
        async def websocket_endpoint(websocket: WebSocket, room_id: str):
            """WebSocket信令通道"""
            if room_id not in self.host.rooms:
                await websocket.close(code=4004, reason="Invalid room")
                return
            
            await websocket.accept()
            room = self.host.rooms[room_id]
            
            # 判断角色
            if room["host_ws"] is None:
                room["host_ws"] = websocket
                logger.info(f"[Room {room_id}] Host connected")
                role = "host"
            else:
                room["client_ws"] = websocket
                logger.info(f"[Room {room_id}] Client connected")
                role = "client"
                # 通知host有客户端连接
                await room["host_ws"].send_json({
                    "type": "client_connected",
                    "data": {"room_id": room_id}
                })
            
            try:
                while True:
                    data = await websocket.receive_json()
                    
                    # 转发消息给另一端
                    other_ws = room["client_ws"] if role == "host" else room["host_ws"]
                    if other_ws and data.get("type") not in ["sdp_offer", "sdp_answer", "ice_candidate"]:
                        # 输入事件直接转发
                        if data.get("type") == "input":
                            await other_ws.send_json(data)
                        else:
                            await other_ws.send_json(data)
                    
                    logger.debug(f"[Room {room_id}] Forwarded: {data.get('type')}")
                    
            except WebSocketDisconnect:
                logger.info(f"[Room {room_id}] {role} disconnected")
                if role == "host":
                    room["host_ws"] = None
                else:
                    room["client_ws"] = None
            
            except Exception as e:
                logger.error(f"[Room {room_id}] Error: {e}")
                await websocket.close(code=1011, reason=str(e))
    
    async def start(self, host: str = "0.0.0.0", port: int = 8000):
        """启动服务器"""
        config = uvicorn.Config(self.app, host=host, port=port, log_level="info")
        self.server = uvicorn.Server(config)
        await self.server.serve()
    
    async def stop(self):
        """停止服务器"""
        if self.server:
            self.server.should_exit = True


class RemoteDesktopHost:
    """远程桌面主机"""
    
    def __init__(self, token: str = None, room_id: str = None):
        self.token = token or generate_token()
        self.room_id = room_id or secrets.token_hex(8)
        self.signaling_url = None  # 动态获取
        
        # 信令服务器
        self.signaling_server = SignalingServer(self)
        self.rooms: dict = {}
        self.token_to_room: dict = {}
        
        # 组件
        self.capture = ScreenCapture()
        self.input_sim = InputSimulator()
        
        # WebRTC
        self.pc: Optional[RTCPeerConnection] = None
        self.video_track = None
        self.audio_track = None
        self.is_running = False
        
        # 保存当前视频帧用于输入坐标映射
        self.current_width = 1280
        self.current_height = 720
    
    async def start_signaling(self):
        """启动信令服务器"""
        import socket
        # 获取本机IP（Tailscale IP优先）
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.0.0.1', 1))  # 不实际发送，只是获取路由接口IP
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'
        finally:
            s.close()
        
        self.signaling_url = f"http://{local_ip}:8000"
        
        # 将房间注册到token
        self.rooms[self.room_id] = {
            "token": self.token,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=30)).isoformat(),
            "host_ws": None,
            "client_ws": None,
        }
        self.token_to_room[self.token] = self.room_id
        
        logger.info(f"信令服务器启动: {self.signaling_url}")
        logger.info(f"Token: {self.token}")
        logger.info(f"房间ID: {self.room_id}")
        
        # 在后台启动
        asyncio.create_task(self.signaling_server.start(host="0.0.0.0", port=8000))
    
    async def create_offer(self) -> str:
        """创建WebRTC Offer"""
        self.pc = RTCPeerConnection()
        
        # 创建视频轨道
        self.video_track = VideoStreamTrack(self.capture)
        self.pc.addTrack(self.video_track)
        
        # 创建SDP Offer
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)
        
        return offer.sdp
    
    async def set_answer(self, answer_sdp: str):
        """设置Answer"""
        answer = RTCSessionDescription(sdp=answer_sdp, type="answer")
        await self.pc.setRemoteDescription(answer)
        logger.info("WebRTC连接已建立")
    
    async def close(self):
        """关闭连接"""
        self.is_running = False
        if self.pc:
            await self.pc.close()
        if self.signaling_server.server:
            await self.signaling_server.stop()
    
    def handle_input(self, data: dict):
        """处理输入事件"""
        action = data.get("action", "")
        x = data.get("x", 0)
        y = data.get("y", 0)
        
        logger.debug(f"输入事件: {action} ({x}, {y})")
        
        if action == "mouse_move":
            self.input_sim.move_mouse(x, y)
        elif action == "mouse_click":
            self.input_sim.click(x, y)
        elif action == "right_click":
            self.input_sim.right_click(x, y)


class VideoStreamTrack:
    """视频流轨道"""
    
    def __init__(self, capture: ScreenCapture):
        self.capture = capture
        self._kind = "video"
    
    @property
    def kind(self):
        return self._kind
    
    async def recv(self) -> VideoFrame:
        """捕获并返回视频帧"""
        jpeg_data, elapsed = self.capture.capture()
        
        from PIL import Image
        import io
        img = Image.open(io.BytesIO(jpeg_data))
        
        # 转换为RGB
        img_rgb = img.convert('RGB')
        frame_data = img_rgb.tobytes()
        
        # 创建VideoFrame
        frame = VideoFrame.from_ndarray(
            np.frombuffer(frame_data, dtype=np.uint8).reshape(
                img_rgb.height, img_rgb.width, 3
            ),
            format='rgb24'
        )
        
        # 设置时间戳
        frame.time_base = 1/30
        return frame


async def main(token: str = None):
    """主函数"""
    token = token or generate_token()
    
    host = RemoteDesktopHost(token)
    
    # 启动信令服务器
    await host.start_signaling()
    
    # 显示连接信息
    print("\n" + "="*50)
    print("远程桌面主机已启动")
    print("="*50)
    print(f"信令地址: {host.signaling_url}")
    print(f"Token: {host.token}")
    print(f"请用Android APP输入以上信息连接")
    print("="*50 + "\n")
    
    try:
        # 创建WebRTC Offer
        logger.info("Creating WebRTC offer...")
        offer_sdp = await host.create_offer()
        
        # 保存offer到文件
        offer_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"offer_{host.token}.json")
        with open(offer_path, 'w') as f:
            json.dump({"sdp": offer_sdp, "type": "offer"}, f, indent=2)
        logger.info(f"Offer saved to {offer_path}")
        
        # 等待Android端连接（通过信令服务器WebSocket）
        logger.info("等待客户端连接...")
        
        # 持续运行
        while host.is_running or host.pc is None or host.pc.connectionState != 'closed':
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await host.close()
        logger.info("Host stopped.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Windows Remote Desktop Host")
    parser.add_argument("--token", help="指定Token（可选，默认随机生成）")
    
    args = parser.parse_args()
    asyncio.run(main(args.token))
