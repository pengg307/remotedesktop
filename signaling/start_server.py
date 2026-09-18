"""
Render部署入口
自动读取PORT环境变量
"""
import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import app, Config

# Render会设置PORT环境变量
port = int(os.getenv("PORT", "8000"))
host = os.getenv("HOST", "0.0.0.0")

print(f"[*] Starting on {host}:{port}")
print(f"[*] Environment: {'production' if port != 8000 else 'local'}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=host, port=port)
