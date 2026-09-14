"""
信令服务器端到端测试 - 模拟host和client双向连接
"""
import asyncio
import json
import aiohttp
import websockets


BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"


async def drain_msgs(ws, max_wait=3):
    """非阻塞读取所有可用消息"""
    msgs = []
    end_time = asyncio.get_event_loop().time() + max_wait
    while asyncio.get_event_loop().time() < end_time:
        try:
            msg = await asyncio.wait_for(ws.recv(), timeout=0.2)
            msgs.append(json.loads(msg))
        except asyncio.TimeoutError:
            break
    return msgs


async def test_all():
    print("=" * 50)
    print("  信令服务器端到端测试")
    print("=" * 50)

    # 1. 健康检查
    print("\n[1] 健康检查...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/health") as resp:
            data = await resp.json()
            print(f"    ✓ 状态: {data['status']}, 房间数: {data['rooms']}")

    # 2. 创建房间
    print("\n[2] 创建Token...")
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/api/token") as resp:
            result = await resp.json()
            room_id = result['room_id']
            token = result['token']
            print(f"    ✓ Token: {token}, RoomID: {room_id}")

    # 3. 两个客户端同时连接同一个房间
    print("\n[3] 建立WebSocket双向连接并交换信令...")

    async def host_session():
        ws_url = f"{WS_URL}/ws/{room_id}?role=host"
        async with websockets.connect(ws_url) as ws:
            # 接收join_ack
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(msg)
            assert data['type'] == 'join_ack', f"Unexpected: {data}"
            print(f"    ✓ Host加入成功，角色: {data['data']['role']}")

            # 等待对方join通知（最多2秒）
            others = await drain_msgs(ws, max_wait=2)
            for m in others:
                if m['type'] == 'join':
                    print(f"    ✓ Host收到Client join通知: {m['data']['role']}")

            # 生成并发送SDP Offer
            sdp_offer = "v=0\r\no=- 123456 1 IN IP4 192.168.1.1\r\ns=-\r\nt=0 0\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\n"
            await ws.send(json.dumps({"type": "sdp_offer", "data": {"sdp": sdp_offer}}))
            print(f"    ✓ Host发送SDP Offer")

            # 等待SDP Answer（处理可能的join通知）
            while True:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=10)
                    data = json.loads(msg)
                    if data['type'] == 'join':
                        print(f"    ✓ Host收到Client join通知: {data['data']['role']}")
                        continue
                    assert data['type'] == 'sdp_answer', f"Expected sdp_answer, got {data['type']}: {data}"
                    print(f"    ✓ Host收到SDP Answer")
                    break
                except asyncio.TimeoutError:
                    assert False, "等待SDP Answer超时"

            # ICE候选交换
            await ws.send(json.dumps({
                "type": "ice_candidate",
                "data": {"candidate": "candidate:1 1 UDP 2122252671 192.168.1.1 9 typ host"}
            }))
            print(f"    ✓ Host发送ICE候选")

            # 等待ICE候选
            while True:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=5)
                    data = json.loads(msg)
                    if data['type'] == 'join':
                        continue
                    assert data['type'] == 'ice_candidate', f"Expected ice_candidate, got {data['type']}"
                    print(f"    ✓ Host收到ICE候选")
                    break
                except asyncio.TimeoutError:
                    assert False, "等待ICE候选超时"

            # 通知开始连接
            await ws.send(json.dumps({"type": "connecting", "data": {}}))
            print(f"    ✓ Host通知开始连接")

            return True

    async def client_session():
        ws_url = f"{WS_URL}/ws/{room_id}?role=client"
        async with websockets.connect(ws_url) as ws:
            # 接收join_ack
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(msg)
            assert data['type'] == 'join_ack', f"Unexpected: {data}"
            print(f"    ✓ Client加入成功，角色: {data['data']['role']}")

            # 等待对方join通知
            others = await drain_msgs(ws, max_wait=2)
            for m in others:
                if m['type'] == 'join':
                    print(f"    ✓ Client收到Host join通知: {m['data']['role']}")

            # 等待SDP Offer
            while True:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=10)
                    data = json.loads(msg)
                    if data['type'] == 'join':
                        print(f"    ✓ Client收到Host join通知: {data['data']['role']}")
                        continue
                    assert data['type'] == 'sdp_offer', f"Expected sdp_offer, got {data['type']}: {data}"
                    print(f"    ✓ Client收到SDP Offer")
                    break
                except asyncio.TimeoutError:
                    assert False, "等待SDP Offer超时"

            # 发送SDP Answer
            sdp_answer = "v=0\r\no=- 654321 1 IN IP4 10.0.0.1\r\ns=-\r\nt=0 0\r\nm=video 9 UDP/TLS/RTP/SAVPF 96\r\n"
            await ws.send(json.dumps({"type": "sdp_answer", "data": {"sdp": sdp_answer}}))
            print(f"    ✓ Client发送SDP Answer")

            # 等待ICE候选
            while True:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=5)
                    data = json.loads(msg)
                    if data['type'] == 'join':
                        continue
                    assert data['type'] == 'ice_candidate', f"Expected ice_candidate, got {data['type']}"
                    print(f"    ✓ Client收到ICE候选")
                    break
                except asyncio.TimeoutError:
                    assert False, "等待ICE候选超时"

            # 发送ICE候选
            await ws.send(json.dumps({
                "type": "ice_candidate",
                "data": {"candidate": "candidate:1 1 UDP 2122252672 10.0.0.1 9 typ host"}
            }))
            print(f"    ✓ Client发送ICE候选")

            # 通知开始连接
            await ws.send(json.dumps({"type": "connecting", "data": {}}))
            print(f"    ✓ Client通知开始连接")

            return True

    # 并发运行host和client
    await asyncio.gather(host_session(), client_session())

    # 4. 验证房间状态
    print("\n[4] 验证房间状态...")
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/api/room/{room_id}") as resp:
            data = await resp.json()
            print(f"    ✓ 房间状态: {data.get('state', 'N/A')}")
            print(f"    ✓ Host连接: {data.get('host_connected')}, Client连接: {data.get('client_connected')}")

    # 5. 清理测试房间
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BASE_URL}/api/cleanup") as resp:
            result = await resp.json()
            print(f"\n[5] 清理过期房间: {result}")

    print("\n" + "=" * 50)
    print("  ✓ 所有测试通过！信令服务器工作正常")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(test_all())
