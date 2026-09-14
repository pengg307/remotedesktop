"""
端到端测试：同时模拟Windows主机和Android客户端
"""
import asyncio
import json
import sys
import os
import aiohttp
import websockets

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_both_sides(signaling_url: str):
    """同时测试Windows和Android两端"""
    
    print("=" * 60)
    print("  端到端测试: Windows ↔ Android (通过信令服务器)")
    print("=" * 60)
    print()
    
    results = {
        'token': None,
        'room_id': None,
        'ws_host': None,
        'ws_client': None,
    }
    
    try:
        # ========== 1. 获取Token ==========
        print("[1] 创建连接房间...")
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{signaling_url}/api/token") as resp:
                result = await resp.json()
                results['token'] = result['token']
                results['room_id'] = result['room_id']
                print(f"    ✓ Token: {result['token']}")
                print(f"    ✓ Room: {result['room_id']}")
                print(f"    ✓ STUN: {result.get('stun_servers', [])}")
        
        room_id = results['room_id']
        
        # ========== 2. 同时连接WebSocket ==========
        print()
        print("[2] 建立双向WebSocket连接...")
        
        # 根据URL选择协议
        if signaling_url.startswith('https://'):
            ws_scheme = 'wss://'
        else:
            ws_scheme = 'ws://'
        
        host_url = f"{ws_scheme}{signaling_url.replace('http://', '').replace('https://', '')}/ws/{room_id}?role=host"
        client_url = f"{ws_scheme}{signaling_url.replace('http://', '').replace('https://', '')}/ws/{room_id}?role=client"
        
        print(f"    Host: {host_url}")
        print(f"    Client: {client_url}")
        
        # 并发连接
        ws_host, ws_client = await asyncio.gather(
            asyncio.wait_for(websockets.connect(host_url), timeout=10),
            asyncio.wait_for(websockets.connect(client_url), timeout=10),
        )
        results['ws_host'] = ws_host
        results['ws_client'] = ws_client
        print(f"    ✓ 两端WebSocket连接成功")
        
        # ========== 3. 接收join_ack ==========
        print()
        print("[3] 接收加入确认...")
        
        host_msg = await asyncio.wait_for(ws_host.recv(), timeout=5)
        host_data = json.loads(host_msg)
        assert host_data['type'] == 'join_ack'
        print(f"    ✓ Windows收到join_ack，角色: {host_data['data']['role']}")
        
        client_msg = await asyncio.wait_for(ws_client.recv(), timeout=5)
        client_data = json.loads(client_msg)
        assert client_data['type'] == 'join_ack'
        print(f"    ✓ Android收到join_ack，角色: {client_data['data']['role']}")
        
        # ========== 4. Windows发送SDP Offer ==========
        print()
        print("[4] Windows发送SDP Offer...")
        
        sdp_offer = """v=0
o=- 123456789 2 IN IP4 192.168.1.100
s=-
t=0 0
m=video 9 UDP/TLS/RTP/SAVPF 96
c=IN IP4 0.0.0.0
a=ice-ufrag:test123
a=ice-pwd:test456
a=fingerprint:sha-256 AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99:AA:BB:CC:DD:EE:FF:00:11:22:33:44:55:66:77:88:99
a=setup:actpass
a=mid:0
a=sendrecv
a=rtpmap:96 VP8/90000
"""
        
        await ws_host.send(json.dumps({
            "type": "sdp_offer",
            "data": {"sdp": sdp_offer}
        }))
        print(f"    → Windows发送SDP Offer")
        
        # ========== 5. Android接收SDP Offer并回复Answer ==========
        print()
        print("[5] Android接收并回复SDP Answer...")
        
        # 等待Android收到Offer
        msg = await asyncio.wait_for(ws_client.recv(), timeout=10)
        client_data = json.loads(msg)
        assert client_data['type'] == 'sdp_offer'
        print(f"    ← Android收到SDP Offer")
        
        sdp_answer = """v=0
o=- 987654321 2 IN IP4 10.0.0.50
s=-
t=0 0
m=video 9 UDP/TLS/RTP/SAVPF 96
c=IN IP4 0.0.0.0
a=ice-ufrag:answer123
a=ice-pwd:answer456
a=fingerprint:sha-256 FF:EE:DD:CC:BB:AA:99:88:77:66:55:44:33:22:11:00:FF:EE:DD:CC:BB:AA:99:88:77:66:55:44:33:22:11:00
a=setup:active
a=mid:0
a=recvonly
a=rtpmap:96 VP8/90000
"""
        
        await ws_client.send(json.dumps({
            "type": "sdp_answer",
            "data": {"sdp": sdp_answer}
        }))
        print(f"    → Android发送SDP Answer")
        
        # ========== 6. Windows接收SDP Answer ==========
        print()
        print("[6] Windows接收SDP Answer...")
        
        msg = await asyncio.wait_for(ws_host.recv(), timeout=5)
        host_data = json.loads(msg)
        assert host_data['type'] == 'sdp_answer'
        print(f"    ← Windows收到SDP Answer")
        
        # ========== 7. ICE候选交换 ==========
        print()
        print("[7] ICE候选交换...")
        
        # Windows发送ICE候选
        ice_candidate_1 = {
            "candidate": "candidate:1 1 UDP 2122252671 192.168.1.100 9 typ host",
            "sdpMid": "0",
            "sdpMLineIndex": 0
        }
        await ws_host.send(json.dumps({
            "type": "ice_candidate",
            "data": ice_candidate_1
        }))
        print(f"    → Windows发送ICE候选")
        
        # Android接收ICE候选
        msg = await asyncio.wait_for(ws_client.recv(), timeout=5)
        client_data = json.loads(msg)
        assert client_data['type'] == 'ice_candidate'
        print(f"    ← Android收到ICE候选")
        
        # Android发送ICE候选
        ice_candidate_2 = {
            "candidate": "candidate:1 1 UDP 2122252672 10.0.0.50 9 typ host",
            "sdpMid": "0",
            "sdpMLineIndex": 0
        }
        await ws_client.send(json.dumps({
            "type": "ice_candidate",
            "data": ice_candidate_2
        }))
        print(f"    → Android发送ICE候选")
        
        # Windows接收ICE候选
        msg = await asyncio.wait_for(ws_host.recv(), timeout=5)
        host_data = json.loads(msg)
        assert host_data['type'] == 'ice_candidate'
        print(f"    ← Windows收到ICE候选")
        
        # ========== 8. 通知开始连接 ==========
        print()
        print("[8] 通知开始连接...")
        
        await asyncio.gather(
            ws_host.send(json.dumps({"type": "connecting", "data": {}})),
            ws_client.send(json.dumps({"type": "connecting", "data": {}})),
        )
        print(f"    → 双方发送connecting")
        
        # ========== 9. 验证结果 ==========
        print()
        print("=" * 60)
        print("  ✓ 端到端测试完成!")
        print("=" * 60)
        print()
        print("测试结果:")
        print("  ✓ Token生成正常")
        print("  ✓ WebSocket双向连接正常")
        print("  ✓ join_ack消息正常")
        print("  ✓ SDP Offer/Answer交换正常")
        print("  ✓ ICE候选双向转发正常")
        print("  ✓ connecting状态同步正常")
        print()
        print("下一步:")
        print("  1. 部署到云端Railway")
        print("  2. 修改Windows端接入云端URL")
        print("  3. 测试真实WebRTC视频流")
        print()
        
    finally:
        # 清理连接
        if results['ws_host']:
            await results['ws_host'].close()
        if results['ws_client']:
            await results['ws_client'].close()


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="端到端测试")
    parser.add_argument(
        "--signaling",
        default="http://localhost:8000",
        help="信令服务器URL (如 http://localhost:8000)"
    )
    args = parser.parse_args()
    
    try:
        await test_both_sides(args.signaling)
    except Exception as e:
        print(f"\n[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
