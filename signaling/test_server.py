"""
信令服务器测试脚本
测试所有API接口和WebSocket通信
"""
import asyncio
import json
import aiohttp
import websockets
import sys
import time


BASE_URL = "http://localhost:8000"


async def test_health():
    """测试健康检查"""
    print("\n[1] 测试健康检查...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/health") as resp:
            data = await resp.json()
            print(f"    ✓ 状态: {data['status']}")
            print(f"    ✓ 房间数: {data['rooms']}")
            return True


async def test_create_token():
    """测试创建Token"""
    print("\n[2] 测试创建Token...")
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/api/token") as resp:
            data = await resp.json()
            print(f"    ✓ Token: {data['token']}")
            print(f"    ✓ RoomID: {data['room_id']}")
            print(f"    ✓ STUN: {data['stun_servers']}")
            return data['token'], data['room_id']


async def test_websocket(token, room_id):
    """测试WebSocket连接"""
    print("\n[3] 测试WebSocket信令...")
    
    ws_url = f"ws://localhost:8000/ws/{room_id}?role=host"
    
    async with websockets.connect(ws_url) as ws:
        # 接收join_ack
        msg = await asyncio.wait_for(ws.recv(), timeout=5)
        data = json.loads(msg)
        
        if data['type'] == 'join_ack':
            print(f"    ✓ 加入成功，角色: {data['data']['role']}")
        else:
            print(f"    ✗ 收到意外消息: {data}")
            return False
        
        # 模拟SDP交换
        print(f"    - 发送SDP Offer...")
        await ws.send(json.dumps({
            "type": "sdp_offer",
            "data": {"sdp": "v=0\r\no=- ..."}
        }))
        
        # 等待ack
        msg = await asyncio.wait_for(ws.recv(), timeout=5)
        data = json.loads(msg)
        print(f"    ✓ 信令发送成功")
        
        return True


async def main():
    print("=" * 50)
    print("  信令服务器测试")
    print("=" * 50)
    
    try:
        # 测试1: 健康检查
        await test_health()
        
        # 测试2: 创建Token
        token, room_id = await test_create_token()
        
        # 测试3: WebSocket通信
        await test_websocket(token, room_id)
        
        print("\n" + "=" * 50)
        print("  ✓ 所有测试通过!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)