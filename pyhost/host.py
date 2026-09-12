"""
Windows远程桌面服务 - 核心模块
功能：屏幕捕获 + WebRTC + 输入模拟
"""
import asyncio
import base64
import ctypes
import io
import json
import logging
import struct
import time
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

import mss
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as sym_padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("pyhost")

INPUT_MOUSE = 0
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x1000
MOUSEEVENTF_ABSOLUTE = 0x8000

KEYEVENTF_KEYDOWN = 0x0000
KEYEVENTF_KEYUP = 0x0002


@dataclass
class ScreenInfo:
    width: int
    height: int
    left: int = 0
    top: int = 0


class ScreenCapture:
    """屏幕捕获模块"""
    
    def __init__(self, screen_index: int = 0):
        self.mss = mss.mss()
        self.screen_index = screen_index
        self.info = self._get_screen_info()
        self.last_frame_time = 0
        self.frame_count = 0
        self.fps = 0
        
    def _get_screen_info(self) -> ScreenInfo:
        """获取屏幕信息"""
        monitors = self.mss.monitors
        if self.screen_index < len(monitors):
            monitor = monitors[self.screen_index]
        else:
            monitor = monitors[0] if monitors else {'left': 0, 'top': 0, 'width': 1920, 'height': 1080}
        
        return ScreenInfo(
            width=int(monitor.get('width', 1920)),
            height=int(monitor.get('height', 1080)),
            left=int(monitor.get('left', 0)),
            top=int(monitor.get('top', 0)),
        )
    
    def capture(self, quality: int = 85) -> tuple[bytes, int]:
        """捕获屏幕并压缩为JPEG，返回(JPEG字节数据, 耗时ms)"""
        start = time.perf_counter()
        screenshot = self.mss.grab({
            'left': self.info.left,
            'top': self.info.top,
            'width': self.info.width,
            'height': self.info.height,
        })
        
        buffer = io.BytesIO()
        from PIL import Image
        img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
        img_rgb = img.convert('RGB')
        
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
        return {
            'width': self.info.width,
            'height': self.info.height,
            'left': self.info.left,
            'top': self.info.top,
            'monitor_count': len(self.mss.monitors),
        }


class InputSimulator:
    """输入模拟模块（键盘和鼠标）"""
    
    def __init__(self):
        self.user32 = ctypes.windll.user32
        self.screen_info = self._get_screen_size()
    
    def _get_screen_size(self) -> tuple[int, int]:
        width = self.user32.GetSystemMetrics(0)
        height = self.user32.GetSystemMetrics(1)
        return (width, height)
    
    def mouse_move(self, x: int, y: int):
        abs_x = int(x * 65535 / self.screen_info[0])
        abs_y = int(y * 65535 / self.screen_info[1])
        self._send_mouse_input(MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE, abs_x, abs_y)
    
    def mouse_click(self, button: str = 'left', double_click: bool = False):
        if button == 'left':
            flags = MOUSEEVENTF_LEFTDOWN
            self._send_mouse_input(flags, 0, 0)
            if double_click:
                time.sleep(0.01)
                self._send_mouse_input(flags, 0, 0)
            time.sleep(0.01)
            self._send_mouse_input(MOUSEEVENTF_LEFTUP, 0, 0)
        elif button == 'right':
            self._send_mouse_input(MOUSEEVENTF_RIGHTDOWN, 0, 0)
            time.sleep(0.01)
            self._send_mouse_input(MOUSEEVENTF_RIGHTUP, 0, 0)
    
    def mouse_wheel(self, delta: int):
        self._send_mouse_input(MOUSEEVENTF_WHEEL, 0, delta)
    
    def key_press(self, key: str, press: bool = True):
        vk_code = self._get_vk_code(key)
        if vk_code is None:
            logger.warning(f"Unknown key: {key}")
            return
        flags = KEYEVENTF_KEYDOWN if press else KEYEVENTF_KEYUP
        self.user32.keybd_event(vk_code, 0, flags, 0)
    
    def _get_vk_code(self, key: str) -> Optional[int]:
        key_map = {
            'enter': 0x0D, 'escape': 0x1B, 'tab': 0x09,
            'space': 0x20, 'backspace': 0x08, 'delete': 0x2E,
            'home': 0x24, 'end': 0x23, 'pageup': 0x21, 'pagedown': 0x22,
            'arrow_up': 0x26, 'arrow_down': 0x28, 'arrow_left': 0x25, 'arrow_right': 0x27,
            'f1': 0x70, 'f2': 0x71, 'f3': 0x72, 'f4': 0x73,
            'f5': 0x74, 'f6': 0x75, 'f7': 0x76, 'f8': 0x77,
            'f9': 0x78, 'f10': 0x79, 'f11': 0x7A, 'f12': 0x7B,
            'lcontrol': 0x11, 'rcontrol': 0xA2, 'lmenu': 0x12, 'rmenu': 0xA3,
            'lshift': 0x10, 'rshift': 0xA1, 'lwin': 0x5B, 'rwin': 0x5C,
        }
        if key.startswith('key_'):
            num = key[4:]
            if num.isdigit():
                return 0x30 + int(num)
        if len(key) == 1 and key.isalpha():
            return ord(key.upper())
        return key_map.get(key.lower())
    
    def _send_mouse_input(self, flags: int, dx: int, dy: int):
        self.user32.mouse_event(flags, dx, dy, 0, 0)


class RemoteDesktopHost:
    """远程桌面主机核心类"""
    
    def __init__(self, token: str, room_id: str):
        self.token = token
        self.room_id = room_id
        self.pc: Optional[RTCPeerConnection] = None
        self.capture = ScreenCapture()
        self.input_sim = InputSimulator()
        self.video_track = None
        self.data_channel = None
        self.is_running = False
        self.key = self._derive_key(token)
    
    def _derive_key(self, token: str) -> bytes:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'remotedesktop',
            iterations=100000,
        )
        return kdf.derive(token.encode())
    
    async def create_offer(self) -> str:
        """创建WebRTC Offer"""
        self.pc = RTCPeerConnection()
        self.video_track = RemoteVideoTrack(self)
        self.video_track.kind = 'video'
        self.pc.addTrack(self.video_track)
        
        # 修复：使用关键字参数而非字典
        self.data_channel = self.pc.createDataChannel("control", ordered=True)
        self.data_channel.on("message", self._on_control_message)
        
        offer = await self.pc.createOffer()
        await self.pc.setLocalDescription(offer)
        
        return json.dumps({'type': offer.type, 'sdp': offer.sdp})
    
    async def set_answer(self, answer_sdp: str):
        """设置远端Answer"""
        answer_data = json.loads(answer_sdp)
        answer = RTCSessionDescription(sdp=answer_data['sdp'], type=answer_data['type'])
        await self.pc.setRemoteDescription(answer)
    
    def _on_control_message(self, message):
        """处理控制消息"""
        try:
            data = json.loads(message)
            action = data.get('action')
            
            if action == 'mouse_move':
                self.input_sim.mouse_move(data.get('x', 0), data.get('y', 0))
            elif action == 'mouse_click':
                self.input_sim.mouse_click(data.get('button', 'left'), data.get('double_click', False))
            elif action == 'mouse_wheel':
                self.input_sim.mouse_wheel(data.get('delta', 0))
            elif action == 'key_press':
                self.input_sim.key_press(data.get('key', ''), data.get('press', True))
            elif action == 'resize':
                w, h = data.get('width', 0), data.get('height', 0)
                if w > 0 and h > 0:
                    self.capture.info.width = w
                    self.capture.info.height = h
        except Exception as e:
            logger.error(f"Error handling control message: {e}")
    
    async def close(self):
        self.is_running = False
        if self.pc:
            await self.pc.close()


class RemoteVideoTrack:
    """自定义WebRTC视频轨道"""
    
    def __init__(self, host: RemoteDesktopHost):
        self.host = host
        self._queue = asyncio.Queue()
        self._running = True
        self._capture_task = None
        self.kind = 'video'
    
    async def recv(self):
        return await self._queue.get()
    
    def start_capturing(self):
        self._capture_task = asyncio.create_task(self._capture_loop())
    
    async def _capture_loop(self):
        import cv2
        import numpy as np
        
        while self._running:
            try:
                jpeg_data, _ = self.host.capture.capture()
                numpy_array = np.frombuffer(jpeg_data, dtype=np.uint8)
                frame = cv2.imdecode(numpy_array, cv2.IMREAD_COLOR)
                
                if frame is not None:
                    from aiortc.rtccodecs import VideoFrame
                    timestamp = time.time()
                    frame_obj = VideoFrame(
                        width=frame.shape[1],
                        height=frame.shape[0],
                        y_buffer=frame[:, :, 0].tobytes(),
                        u_buffer=frame[:, :, 1].tobytes(),
                        v_buffer=frame[:, :, 2].tobytes(),
                        timestamp=timestamp * 1_000_000_000
                    )
                    await self._queue.put(frame_obj)
                
                await asyncio.sleep(0.033)
            except Exception as e:
                logger.error(f"Capture error: {e}")
                await asyncio.sleep(0.1)
    
    def stop(self):
        self._running = False


if __name__ == "__main__":
    print("测试导入...")
    capture = ScreenCapture()
    print(f"屏幕信息: {capture.get_info()}")
    
    input_sim = InputSimulator()
    print(f"屏幕尺寸: {input_sim.screen_info}")
    
    print("✓ 所有模块导入成功")
