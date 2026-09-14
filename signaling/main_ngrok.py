#!/usr/bin/env python3
"""
Remote Desktop Signaling Server with ngrok tunnel
自动启动信令服务器并建立ngrok公网隧道
"""
import os
import sys
import time
import threading
from pathlib import Path

# 配置
SIGNALE_PORT = 8000
NGROK_TOKEN = os.getenv("NGROK_AUTH_TOKEN", "")

def check_ngrok_token():
    """检查ngrok token"""
    if not NGROK_TOKEN:
        print("=" * 50)
        print("  请先配置ngrok Auth Token")
        print("=" * 50)
        print()
        print("  步骤1: 注册账号")
        print("  访问: https://dashboard.ngrok.com/signup")
        print()
        print("  步骤2: 获取Token")
        print("  登录后点击 'Getting Started' -> 'Authtoken'")
        print("  复制token值")
        print()
        print("  步骤3: 设置环境变量")
        print(f"  Windows CMD:  set NGROK_AUTH_TOKEN=YOUR_TOKEN")
        print(f"  Windows PS:   $env:NGROK_AUTH_TOKEN='YOUR_TOKEN'")
        print(f"  Linux/Mac:    export NGROK_AUTH_TOKEN='YOUR_TOKEN'")
        print()
        print("  或者直接在命令行中运行:")
        print(f"  NGROK_AUTH_TOKEN=YOUR_TOKEN python main_ngrok.py")
        print()
        print("=" * 50)
        return False
    return True

def start_signal_server(port: int):
    """启动信令服务器"""
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    import secrets
    import string
    from datetime import datetime, timedelta
    
    app = FastAPI(title="RemoteDesktop Signaling Server")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    rooms = {}
    token_to_room = {}
    
    class TokenResponse(BaseModel):
        token: str
        room_id: str
        expires_in_minutes: int
    
    @app.post("/api/token", response_model=TokenResponse)
    async def create_token():
        # 生成唯一token
        attempts = 0
        while attempts < 100:
            token = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            if token not in token_to_room:
                break
            attempts += 1
        
        room_id = secrets.token_hex(8)
        
        rooms[room_id] = {
            "token": token,
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(minutes=30)).isoformat(),
            "host_connected": False,
            "client_connected": False,
        }
        token_to_room[token] = room_id
        
        print(f"📱 新连接Token: {token}")
        print(f"🏠 RoomID: {room_id}")
        print(f"⏰ 过期时间: 30分钟")
        print()
        
        return {
            "token": token,
            "room_id": room_id,
            "expires_in_minutes": 30
        }
    
    @app.get("/api/room/{room_id}")
    async def get_room_status(room_id: str):
        if room_id not in rooms:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail="Room not found")
        return rooms[room_id]
    
    @app.get("/api/status")
    async def get_status():
        return {
            "servers_running": True,
            "signal_port": port,
            "rooms": len(rooms),
            "ngrok_tunnel": None  # Will be set later
        }
    
    @app.on_event("shutdown")
    async def shutdown():
        print("🛑 正在关闭服务...")
    
    # 运行服务器
    print(f"🚀 启动信令服务器...")
    print(f"📍 局域网地址: http://localhost:{port}")
    print(f"📍 局域网地址: http://192.168.1.3:{port}")
    print()
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")

def start_ngrok_tunnel(port: int, token: str):
    """启动ngrok隧道"""
    from pyngrok import ngrok
    
    try:
        # 配置ngrok
        ngrok.set_auth_token(token)
        
        # 创建隧道
        print("🔄 正在建立ngrok隧道...")
        public_url = ngrok.connect(port, bind_tls=True)
        
        print()
        print("=" * 50)
        print("  ✅ ngrok隧道已建立!")
        print("=" * 50)
        print()
        print(f"  🌐 公网URL: {public_url}")
        print(f"  📱 手机连接时使用此URL")
        print()
        print("=" * 50)
        print("  Android连接配置:")
        print("=" * 50)
        print(f"  信令服务器: {public_url}")
        print(f"  Token: (从API获取)")
        print()
        
        # 保持隧道运行
        print("💡 按 Ctrl+C 停止隧道")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("🛑 正在关闭隧道...")
            ngrok.kill()
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ ngrok隧道启动失败: {e}")
        print()
        print("请检查:")
        print("1. ngrok Auth Token是否正确")
        print("2. 网络连接是否正常")
        print("3. 防火墙是否允许")
        return None
    
    return public_url

def main():
    """主函数"""
    print()
    print("=" * 50)
    print("  RemoteDesktop 信令服务器 + ngrok隧道")
    print("=" * 50)
    print()
    
    # 检查ngrok token
    if not check_ngrok_token():
        print()
        print("💡 如果暂时不需要ngrok，可以只运行局域网版本")
        print("   运行: uv run python main.py")
        return 1
    
    # 分离ngrok token
    ngrok_token = NGROK_TOKEN
    
    # 启动ngrok隧道
    tunnel_thread = threading.Thread(
        target=start_ngrok_tunnel,
        args=(SIGNALE_PORT, ngrok_token),
        daemon=True
    )
    tunnel_thread.start()
    
    # 等待隧道建立
    time.sleep(2)
    
    # 启动信令服务器
    start_signal_server(SIGNALE_PORT)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
