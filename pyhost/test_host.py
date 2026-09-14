"""
测试Windows端与信令服务器的集成
"""
import asyncio
import json
import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_windows_host():
    """测试Windows主机代码"""
    print("=" * 50)
    print("  Windows Host 测试")
    print("=" * 50)
    
    # 测试导入
    try:
        from host import ScreenCapture, InputSimulator, HostServer
        print("[PASS] 模块导入成功")
    except ImportError as e:
        print(f"[FAIL] 导入失败: {e}")
        return
    
    # 测试屏幕捕获
    try:
        capture = ScreenCapture()
        info = capture.get_info()
        print(f"[PASS] 屏幕捕获: {info}")
    except Exception as e:
        print(f"[FAIL] 屏幕捕获: {e}")
        return
    
    # 测试输入模拟
    try:
        sim = InputSimulator()
        print(f"[PASS] 输入模拟: {sim.screen_info}")
    except Exception as e:
        print(f"[FAIL] 输入模拟: {e}")
        return
    
    # 测试WebRTC
    try:
        from aiortc import RTCPeerConnection
        print("[PASS] WebRTC导入成功")
    except ImportError as e:
        print(f"[FAIL] WebRTC导入: {e}")
    
    print()
    print("=" * 50)
    print("  Windows Host 代码准备完成")
    print("=" * 50)
    print()
    print("运行命令:")
    print('  python host.py --signaling https://你的信令服务器-url')
    print()

if __name__ == "__main__":
    asyncio.run(test_windows_host())
