"""
Windows远程桌面服务 - 主入口
启动命令: uv run python main.py --token ABCD12
"""
import argparse
import asyncio
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


async def main(token: str, room_id: str = None):
    """主函数"""
    logger.info(f"Starting Remote Desktop Host")
    logger.info(f"Token: {token}")
    
    host = RemoteDesktopHost(token, room_id or "default")
    
    try:
        logger.info("Creating WebRTC offer...")
        offer_sdp = await host.create_offer()
        
        offer_path = os.path.join(os.path.dirname(__file__), f"offer_{token}.json")
        with open(offer_path, 'w') as f:
            f.write(offer_sdp)
        
        logger.info(f"Offer saved to {offer_path}")
        logger.info(f"Waiting for client to connect...")
        logger.info(f"Use this token on Android app: {token}")
        
        answer_path = os.path.join(os.path.dirname(__file__), f"answer_{token}.json")
        
        while not os.path.exists(answer_path):
            await asyncio.sleep(0.5)
        
        with open(answer_path, 'r') as f:
            answer_sdp = f.read()
        
        await host.set_answer(answer_sdp)
        logger.info("WebRTC connection established!")
        
        if host.video_track:
            host.video_track.start_capturing()
        
        host.is_running = True
        
        while host.is_running:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await host.close()
        logger.info("Host stopped.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Windows Remote Desktop Host")
    parser.add_argument("--token", required=True, help="连接Token（6位）")
    parser.add_argument("--room", help="房间ID（可选）")
    
    args = parser.parse_args()
    
    asyncio.run(main(args.token, args.room))
