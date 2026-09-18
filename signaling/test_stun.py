"""
WebRTC STUN穿透测试
验证两端能否通过STUN建立P2P连接
"""
import asyncio
import socket
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_stun_sync():
    """测试STUN服务器可达性（同步版本）"""
    stun_servers = [
        ("stun.l.google.com", 19302),
        ("stun1.l.google.com", 19302),
        ("stun.voip.blackberry.com", 3478),
    ]

    logger.info("=" * 60)
    logger.info("  STUN穿透测试")
    logger.info("=" * 60)
    logger.info("")

    results = {}

    for host, port in stun_servers:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3.0)

            # 发送STUN binding request
            stun_request = bytes([0x00, 0x01, 0x00, 0x00])
            sock.sendto(stun_request, (host, port))

            try:
                data, addr = sock.recvfrom(1024)
                results[(host, port)] = "OK"
                logger.info(f"✅ {host}:{port} - STUN响应正常")
            except socket.timeout:
                results[(host, port)] = "TIMEOUT"
                logger.warning(f"⚠️ {host}:{port} - STUN无响应")

            sock.close()
        except Exception as e:
            results[(host, port)] = f"ERROR: {e}"
            logger.error(f"❌ {host}:{port} - {e}")

    logger.info("")
    logger.info("测试结果汇总:")
    reachable = sum(1 for v in results.values() if v == "OK")
    logger.info(f"  可达STUN服务器: {reachable}/{len(stun_servers)}")

    if reachable == 0:
        logger.warning("")
        logger.warning("⚠️ 所有STUN服务器都无法访问！")
        logger.warning("可能原因:")
        logger.warning("  1. 防火墙拦截了UDP 19302端口")
        logger.warning("  2. 运营商封锁了STUN服务")
        logger.warning("  3. 需要配置代理或TURN中继")
        logger.warning("")
        logger.warning("建议:")
        logger.warning("  - 检查防火墙设置")
        logger.warning("  - 尝试使用TURN中继服务器")
        logger.warning("  - 或使用ngrok/Cloudflare Tunnel暴露本地服务")

    return results


async def main():
    """主函数"""
    await asyncio.get_event_loop().run_in_executor(None, test_stun_sync)

    logger.info("")
    logger.info("=" * 60)
    logger.info("  测试完成")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
