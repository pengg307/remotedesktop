"""
信令服务器 - 云端集成版
Windows端连接云端信令服务器的示例
"""
import asyncio
import json
import websockets
import sys


class SignalingClient:
    """连接到云端信令服务器的客户端"""
    
    def __init__(self, server_url: str, room_id: str, role: str):
        self.server_url = server_url  # ws://服务器IP:8000
        self.room_id = room_id
        self.role = role  # host 或 client
        self.ws = None
        self.connected = False
        
    async def connect(self):
        """连接到信令服务器"""
        url = f"{self.server_url}/ws/{self.room_id}?role={self.role}"
        print(f"[*] 连接到: {url}")
        
        self.ws = await websockets.connect(url)
        self.connected = True
        print(f"[+] 已连接，角色: {self.role}")
        
    async def send_sdp_offer(self, sdp: str):
        """发送SDP Offer"""
        msg = json.dumps({
            "type": "sdp_offer",
            "data": {"sdp": sdp}
        })
        await self.ws.send(msg)
        print(f"[→] 发送SDP Offer")
        
    async def send_sdp_answer(self, sdp: str):
        """发送SDP Answer"""
        msg = json.dumps({
            "type": "sdp_answer",
            "data": {"sdp": sdp}
        })
        await self.ws.send(msg)
        print(f"[→] 发送SDP Answer")
        
    async def send_ice_candidate(self, candidate: dict):
        """发送ICE候选"""
        msg = json.dumps({
            "type": "ice_candidate",
            "data": candidate
        })
        await self.ws.send(msg)
        
    async def notify_connecting(self):
        """通知开始建立连接"""
        msg = json.dumps({"type": "connecting", "data": {}})
        await self.ws.send(msg)
        
    async def close(self):
        """断开连接"""
        self.connected = False
        if self.ws:
            await self.ws.close()
            
    async def receive_messages(self):
        """接收信令消息"""
        while self.connected:
            try:
                msg = await asyncio.wait_for(self.ws.recv(), timeout=30)
                data = json.loads(msg)
                print(f"[←] 收到: {data['type']}")
                yield data
            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosed:
                print("[!] 连接已关闭")
                self.connected = False
                break


async def main():
    """测试连接"""
    if len(sys.argv) < 4:
        print("用法: python client_signaling.py <server_url> <room_id> <role>")
        print("示例: python client_signaling.py ws://1.2.3.4:8000 abc123 host")
        return
    
    server_url = sys.argv[1]
    room_id = sys.argv[2]
    role = sys.argv[3]
    
    client = SignalingClient(server_url, room_id, role)
    
    try:
        await client.connect()
        
        # 接收消息
        async for msg in client.receive_messages():
            msg_type = msg['type']
            data = msg['data']
            
            if msg_type == 'join_ack':
                print(f"[+] 加入成功，对方角色: {data.get('role')}")
            elif msg_type == 'sdp_offer':
                print(f"[+] 收到SDP Offer")
            elif msg_type == 'sdp_answer':
                print(f"[+] 收到SDP Answer")
            elif msg_type == 'ice_candidate':
                print(f"[+] 收到ICE候选")
            elif msg_type == 'connecting':
                print(f"[+] 对方正在连接...")
            elif msg_type == 'closed':
                print(f"[!] 对方已断开")
                break
                
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())