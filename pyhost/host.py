"""
Windows远程桌面主机 - 信令服务器版本
功能：屏幕捕获 + WebRTC + 输入模拟 + 云端信令
"""
import asyncio
import json
import logging
import time
import sys
import os
from typing import Optional

import mss
import websockets
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer
from av import VideoFrame
import numpy as np

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
        
        return {
            'width': int(monitor.get('width', 1920)),
            'height': int(monitor.get('height', 1080)),
            'left': int(monitor.get('left', 0)),
            'top': int(monitor.get('top', 0)),
        }
    
    def capture(self, quality: int = 85) -> tuple[bytes, int]:
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
    
    def _get_screen_size(self) -> tuple[int, int]:
        width = self.user32.GetSystemMetrics(0)
        height = self.user32.GetSystemMetrics(1)
        return (width, height)
    
    def mouse_move(self, x: int, y: int):
        abs_x = int(x * 65535 / self.screen_info[0])
        abs_y = int(y * 65535 / self.screen_info[1])
        self._send_mouse_input(0x0001 | 0x8000, abs_x, abs_y)
    
    def mouse_click(self, button: str = 'left', double_click: bool = False):
        if button == 'left':
            flags = 0x0002
            self._send_mouse_input(flags, 0, 0)
            if double_click:
                time.sleep(0.01)
                self._send_mouse_input(flags, 0, 0)
            time.sleep(0.01)
            self._send_mouse_input(0x0004, 0, 0)
        elif button == 'right':
            self._send_mouse_input(0x0008, 0, 0)
            time.sleep(0.01)
            self._send_mouse_input(0x0010, 0, 0)
    
    def mouse_wheel(self, delta: int):
        self._send_mouse_input(0x0800, 0, delta)
    
    def key_press(self, key: str, press: bool = True):
        # 简化版
        pass
    
    def _send_mouse_input(self, flags: int, dx: int, dy: int):
        self.user32.mouse_event(flags, dx, dy, 0, 0)


class RemoteVideoTrack:
    """自定义WebRTC视频轨道"""
    
    def __init__(self, capture: ScreenCapture):
        self.capture = capture
        self._queue = asyncio.Queue()
        self._running = True
        self._task = None
        self.kind = 'video'
    
    async def recv(self):
        return await self._queue.get()
    
    def start(self):
        self._task = asyncio.create_task(self._capture_loop())
    
    async def _capture_loop(self):
        """捕获循环"""
        while self._running:
            try:
                jpeg_data, _ = self.capture.capture()
                
                # 解码JPEG为numpy数组
                arr = np.frombuffer(jpeg_data, dtype=np.uint8)
                img = __import__('cv2').imdecode(arr, __import__('cv2').IMREAD_COLOR)
                
                if img is not None:
                    # 转换为YUV420P帧
                    frame = VideoFrame(
                        width=img.shape[1],
                        height=img.shape[0],
                        type='yuv420p'
                    )
                    # 拷贝数据
                    frame.planes[0].update(img[:, :, 2].tobytes())  # Y
                    frame.planes[1].update(img[:, :, 1].tobytes())  # U
                    frame.planes[2].update(img[:, :, 0].tobytes())  # V
                    await self._queue.put(frame)
                
                await asyncio.sleep(0.033)  # 30 FPS
            except Exception as e:
                logger.error(f"Capture error: {e}")
                await asyncio.sleep(0.1)
    
    def stop(self):
        self._running = False


class HostServer:
    """主机服务 - 连接云端信令服务器"""
    
    def __init__(self, signaling_url: str, token: str):
        self.signaling_url = signaling_url.rstrip('/')
        self.token = token
        self.room_id = None
        self.ws = None
        self.pc: Optional[RTCPeerConnection] = None
        self.capture = ScreenCapture()
        self.input_sim = InputSimulator()
        self.video_track = None
        self.is_running = False
        
    async def connect_to_signaling(self):
        """连接到信令服务器获取房间"""
        logger.info(f"[*] 连接信令服务器: {self.signaling_url}")
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # 获取token和room_id
            async with session.post(f"{self.signaling_url}/api/token") as resp:
                result = await resp.json()
                self.room_id = result['room_id']
                self.token = result['token']
                stun_servers = result.get('stun_servers', [])
                logger.info(f"[+] 房间: {self.room_id}, Token: {self.token}")
                logger.info(f"[+] STUN: {stun_servers}")
            
            # 连接WebSocket
            ws_url = f"wss://{self.signaling_url.replace('https://', '').replace('http://', '')}/ws/{self.room_id}?role=host"
            logger.info(f"[*] WebSocket: {ws_url}")
            
            self.ws = await websockets.connect(ws_url)
            logger.info(f"[+] WebSocket已连接")
            
            # 接收join_ack
            msg = await asyncio.wait_for(self.ws.recv(), timeout=10)
            data = json.loads(msg)
            assert data['type'] == 'join_ack', f"Unexpected: {data}"
            logger.info(f"[+] 加入成功，角色: {data['data']['role']}")
            
            return stun_servers
    
    async def start_webrtc(self, stun_servers: list):
        """启动WebRTC"""
        self.pc = RTCPeerConnection()
        
        # 添加视频轨道
        self.video_track = RemoteVideoTrack(self.capture)
        self.pc.addTrack(self.video_track)
        
        # 配置ICE服务器
        ice_servers = [{'url': s} for s in stun_servers]
        if ice_servers:
            self.pc.setConfiguration({'iceServers': ice_servers})
        
        logger.info(f"[+] WebRTC配置完成，创建Offer...")
        
        # 创建Offer
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)
        
        # 发送SDP Offer
        await self.ws.send(json.dumps({
            "type": "sdp_offer",
            "data": {"sdp": offer.sdp}
        }))
        logger.info(f"[→] 发送SDP Offer")
        
        return offer
    
    async def receive_answer(self):
        """接收SDP Answer"""
        msg = await asyncio.wait_for(self.ws.recv(), timeout=30)
        data = json.loads(msg)
        
        if data['type'] != 'sdp_answer':
            raise RuntimeError(f"Expected sdp_answer, got {data['type']}")
        
        answer_sdp = data['data']['sdp']
        answer = RTCSessionDescription(sdp=answer_sdp, type='answer')
        await self.pc.setRemoteDescription(answer)
        
        logger.info(f"[+] 收到SDP Answer，开始建立连接...")
        self.is_running = True
        
        # 开始捕获
        self.video_track.start()
        
        # 发送connecting
        await self.ws.send(json.dumps({"type": "connecting", "data": {}}))
        
        return True
    
    async def handle_ice_candidates(self):
        """处理ICE候选"""
        while self.is_running:
            try:
                msg = await asyncio.wait_for(self.ws.recv(), timeout=1)
                data = json.loads(msg)
                
                if data['type'] == 'ice_candidate':
                    candidate = data['data'].get('candidate')
                    if candidate:
                        await self.pc.addIceCandidate(candidate)
                        logger.info(f"[←] 收到ICE候选")
                
                elif data['type'] == 'closed':
                    logger.info(f"[!] 对方已断开")
                    break
                    
            except asyncio.TimeoutError:
                continue
    
    async def handle_input(self):
        """处理输入事件（如果需要通过信令服务器转发）"""
        while self.is_running:
            try:
                msg = await asyncio.wait_for(self.ws.recv(), timeout=1)
                data = json.loads(msg)
                
                if data['type'] == 'input':
                    action = data['data'].get('action')
                    if action == 'mouse_move':
                        self.input_sim.mouse_move(data['data'].get('x', 0), data['data'].get('y', 0))
                    elif action == 'mouse_click':
                        self.input_sim.mouse_click(data['data'].get('button', 'left'))
                    # ... 其他输入处理
                
            except asyncio.TimeoutError:
                continue
    
    async def close(self):
        """关闭连接"""
        self.is_running = False
        if self.video_track:
            self.video_track.stop()
        if self.pc:
            await self.pc.close()
        if self.ws:
            await self.ws.close()
        logger.info(f"[-] 已断开连接")


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Windows远程桌面主机")
    parser.add_argument("--signaling", required=True, help="信令服务器URL，如 https://xxx.railway.app")
    args = parser.parse_args()
    
    logger.info("=" * 60)
    logger.info("  Remote Desktop Host (Signaling Server)")
    logger.info("=" * 60)
    logger.info(f"  信令服务器: {args.signaling}")
    logger.info("=" * 60)
    
    host = HostServer(args.signaling, "")
    
    try:
        # 1. 连接信令服务器
        stun_servers = await host.connect_to_signaling()
        
        # 2. 启动WebRTC
        await host.start_webrtc(stun_servers)
        
        # 3. 接收Answer
        await host.receive_answer()
        
        # 4. 处理ICE候选
        ice_task = asyncio.create_task(host.handle_ice_candidates())
        
        # 5. 主循环
        while host.is_running:
            await asyncio.sleep(1)
        
        ice_task.cancel()
        
    except KeyboardInterrupt:
        logger.info("[!] 用户中断")
    except Exception as e:
        logger.error(f"[!] 错误: {e}", exc_info=True)
    finally:
        await host.close()


if __name__ == "__main__":
    asyncio.run(main())
