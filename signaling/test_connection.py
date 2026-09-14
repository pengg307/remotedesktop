#!/usr/bin/env python3
"""
快速测试脚本 - 获取Token和测试连接
"""
import requests
import sys
import webbrowser
from datetime import datetime

BASE_URL = "http://localhost:8000"

def get_token():
    """获取新的Token"""
    try:
        response = requests.post(f"{BASE_URL}/api/token", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"❌ 获取Token失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        print("请确认信令服务器正在运行")
        return None

def test_connection():
    """测试连接"""
    print()
    print("=" * 50)
    print("  RemoteDesktop 信令服务器测试")
    print("=" * 50)
    print()
    
    # 获取Token
    print("📡 正在获取Token...")
    token_data = get_token()
    
    if not token_data:
        print()
        print("⚠️  无法获取Token，请检查:")
        print("   1. 信令服务器是否运行: http://localhost:8000")
        print("   2. 防火墙是否阻止连接")
        print()
        return
    
    token = token_data.get("token")
    room_id = token_data.get("room_id")
    expires = token_data.get("expires_in_minutes")
    
    print()
    print("✅ Token获取成功!")
    print()
    print("=" * 50)
    print("  连接信息")
    print("=" * 50)
    print()
    print(f"  📱 Token: {token}")
    print(f"  🏠 RoomID: {room_id}")
    print(f"  ⏰ 过期时间: {expires}分钟")
    print()
    print("=" * 50)
    print("  访问方式")
    print("=" * 50)
    print()
    print("  1️⃣  局域网访问（手机连WiFi）:")
    print(f"     服务器: http://192.168.1.3:8000")
    print()
    print("  2️⃣  公网访问（手机用SIM卡）:")
    print("     需要ngrok隧道")
    print("     运行: 启动ngrok.bat")
    print()
    print("=" * 50)
    print("  下一步操作")
    print("=" * 50)
    print()
    print("  A. 测试局域网连接:")
    print("     1. 手机连接WiFi")
    print("     2. Android输入:")
    print(f"        服务器: http://192.168.1.3:8000")
    print(f"        Token: {token}")
    print()
    print("  B. 配置ngrok公网访问:")
    print("     1. 双击运行: 启动ngrok.bat")
    print("     2. 记录显示的公网URL")
    print("     3. Android使用该URL连接")
    print()
    print("  C. 再次获取Token:")
    print(f"     运行: python test_connection.py")
    print()
    print("=" * 50)

if __name__ == "__main__":
    test_connection()
