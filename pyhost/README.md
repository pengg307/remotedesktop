# Windows 远程桌面主机

## 功能
- 屏幕捕获 (mss + JPEG压缩)
- WebRTC视频流 (aiortc)
- 输入模拟 (ctypes)
- 云端信令服务器集成

## 安装
```bash
pip install -r requirements.txt
```

## 运行
```bash
python host.py --signaling https://你的信令服务器-url
```

## 测试
```bash
# 测试屏幕捕获
python -c "from host import ScreenCapture; c = ScreenCapture(); print(c.get_info())"

# 测试输入模拟
python -c "from host import InputSimulator; i = InputSimulator(); print(i.screen_info)"
```