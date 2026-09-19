"""
Windows远程桌面服务 - 主入口
启动命令: uv run python main.py
"""
import argparse
import asyncio
import json
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from host import RemoteDesktopHost

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("pyhost_main")


async def main(token: str = None):
    """主函数"""
    logger.info("Starting Remote Desktop Host (Local Signaling Mode)")
    
    host = RemoteDesktopHost(token)
    
    # 启动信令服务器
    await host.start_signaling()
    
    # 显示连接信息
    print("\n" + "="*50)
    print("远程桌面主机已启动")
    print("="*50)
    print(f"信令地址: {host.signaling_url}")
    print(f"Token: {host.token}")
    print(f"房间ID: {host.room_id}")
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
        
        # 启动视频捕获
        if host.video_track:
            host.video_track.start_capturing = True
        
        host.is_running = True
        
        # 持续运行
        while host.is_running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await host.close()
        logger.info("Host stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Windows Remote Desktop Host")
    parser.add_argument("--token", help="指定Token（可选，默认随机生成）")
    
    args = parser.parse_args()
    asyncio.run(main(args.token))
