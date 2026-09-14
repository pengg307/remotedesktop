"""
云端信令服务器 - 简化启动入口
环境变量的配置方式：
  SIGN_PORT=8000 SIGN_HOST=0.0.0.0 python server.py
"""
import os
import sys

# 从环境变量读取配置
os.environ.setdefault("SIGN_HOST", "0.0.0.0")
os.environ.setdefault("SIGN_PORT", "8000")
os.environ.setdefault("TOKEN_LENGTH", "6")
os.environ.setdefault("ROOM_EXPIRE", "30")
os.environ.setdefault("MAX_ROOMS", "100")

# 导入并启动
from server import app, main

if __name__ == "__main__":
    main()
