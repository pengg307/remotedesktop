# Remote Desktop WebRTC 远程桌面 - 完整架构文档

## 系统架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Remote Desktop System                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐         WebSocket         ┌──────────────────────┐   │
│  │              │◄─────────────────────────►│                      │   │
│  │  Android     │                           │  Cloud Signaling     │   │
│  │  (Client)    │         WebSocket         │  Server (ECS)        │   │
│  │              │◄─────────────────────────►│  :8000               │   │
│  └──────┬───────┘                           └──────────┬───────────┘   │
│         │                                                │              │
│         │  WebRTC DataChannel (视频流 + 控制)             │              │
│         │  P2P直连，不经过云端                             │              │
│         ▼                                                ▼              │
│  ┌──────────────┐                           ┌──────────────────────┐   │
│  │              │                           │                      │   │
│  │  Windows     │◄═══════════════════════════►│  pyhost (Windows)    │   │
│  │  App         │       WebRTC + 输入模拟     │  :9000 (内网)        │   │
│  │  (Viewer)    │                           │                      │   │
│  └──────────────┘                           └──────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 三大组件

### 1. 云端信令服务器 (Signaling Server)
- **位置**: 云端ECS (腾讯云/阿里云)
- **端口**: 8000
- **技术栈**: FastAPI + WebSocket + asyncio
- **职责**:
  - 生成6位Token (排除0/O/1/I/l)
  - 房间管理 (30分钟过期)
  - SDP Offer/Answer交换
  - ICE候选转发
  - 状态同步 (connecting/connected/closed)
- **依赖**: Python 3.9+, fastapi, uvicorn, websockets
- **状态**: ✅ 已完成，测试通过

### 2. Windows端主机 (pyhost)
- **位置**: 用户Windows电脑
- **端口**: 9000 (内网)
- **技术栈**: Python + aiortc (WebRTC) + mss (屏幕捕获) + ctypes (输入模拟)
- **职责**:
  - 屏幕捕获 (mss → JPEG)
  - WebRTC媒体流 (VP8/H264)
  - 输入模拟 (鼠标/键盘)
  - 连接云端信令服务器
  - Token认证
- **依赖**: Python 3.9+, aiortc, mss, pillow, pyautogui
- **状态**: 🔄 待修改 (接入云端信令)

### 3. Android端查看器 (app_remote)
- **位置**: Android手机
- **技术栈**: Kotlin + WebRTC Android SDK
- **职责**:
  - 连接云端信令服务器
  - 输入事件采集 (触摸/滑动/按键)
  - WebRTC视频解码显示
  - Token输入/连接
- **依赖**: Android SDK, WebRTC Android SDK
- **状态**: 🔄 待开发

---

## 连接流程 (完整握手)

```
Step 1: Android请求Token
  Android → POST /api/token → 云端信令服务器
  云端返回: {room_id, token, stun_servers}

Step 2: Windows请求Token
  Windows → POST /api/token → 云端信令服务器
  云端返回: {room_id, token, stun_servers}

Step 3: 双方连接WebSocket
  Android → ws://云服务器:8000/ws/{room_id}?role=client
  Windows → ws://云服务器:8000/ws/{room_id}?role=host

Step 4: 交换Join Ack
  双方收到: {type: "join_ack", role: "...", stun_servers: [...]}

Step 5: WebRTC握手 (通过云端转发)
  Windows → sdp_offer → 云端 → Android
  Android → sdp_answer → 云端 → Windows

Step 6: ICE候选交换 (通过云端转发)
  Windows ↔ ICE候选 ↔ 云端 ↔ ICE候选 ↔ Android

Step 7: 建立P2P连接
  双方尝试STUN穿透
  如果失败 → 回退到TURN中继 (可选)

Step 8: 开始传输
  视频流: Android ← WebRTC ← Windows屏幕
  控制流: Android → WebRTC → Windows输入模拟
```

---

## 信令协议格式

所有WebSocket消息统一格式：
```json
{
  "type": "join_ack|sdp_offer|sdp_answer|ice_candidate|connecting|connected|closed|error",
  "data": {...}
}
```

### 消息类型

| 类型 | 发送方 | 接收方 | 说明 |
|------|--------|--------|------|
| `join_ack` | 服务器 | 客户端 | 加入成功，含token和STUN配置 |
| `sdp_offer` | Windows | Android | WebRTC会话描述 |
| `sdp_answer` | Android | Windows | WebRTC会话描述 |
| `ice_candidate` | 双向 | 对方 | ICE候选 (NAT穿透信息) |
| `connecting` | 双向 | 对方 | 开始建立直连 |
| `connected` | 服务器 | 双方 | 直连成功 |
| `closed` | 任意 | 对方 | 连接关闭 |
| `error` | 服务器 | 客户端 | 错误信息 |

---

## STUN/TURN配置

### STUN (免费，Google)
```
stun:stun.l.google.com:19302
stun:stun1.l.google.com:19302
```
大多数情况足够穿透NAT。

### TURN (可选，当STUN失败时)
```
turn:你的服务器:3478?transport=tcp
turn用户名: turn密码
```
TURN需要自建或租用 (如twilio, cloudflare), 带宽成本高。

---

## API接口

### REST API
```
GET  /api/health          # 健康检查
POST /api/token           # 创建房间，返回token+room_id
GET  /api/room/{room_id}  # 查询房间状态
POST /api/cleanup         # 清理过期房间
```

### WebSocket
```
ws://服务器IP:8000/ws/{room_id}?role=host|client
```

---

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `SIGN_HOST` | 0.0.0.0 | 监听地址 |
| `SIGN_PORT` | 8000 | 监听端口 |
| `TOKEN_LENGTH` | 6 | Token长度 |
| `ROOM_EXPIRE` | 30 | 房间过期时间(分钟) |
| `MAX_ROOMS` | 100 | 最大房间数 |

---

## 文件结构

```
E:/aiprojects/RemoteDesktop/
├── signaling/                    # 云端信令服务器
│   ├── server.py                # 主程序 (391行)
│   ├── start_server.py          # 启动入口
│   ├── requirements.txt         # Python依赖
│   ├── pyproject.toml           # UV配置
│   ├── DEPLOY.md                # 部署文档
│   ├── test_e2e.py              # 端到端测试
│   ├── start.sh                 # Linux启动脚本
│   └── start.bat                # Windows启动脚本
│
├── pyhost/                       # Windows端
│   ├── host.py                  # WebRTC核心 (318行)
│   ├── main.py                  # 启动入口 (75行)
│   ├── signaling_client.py      # 信令客户端 (待完善)
│   └── requirements.txt
│
└── android_remote/               # Android端 (待开发)
    ├── app/
    │   └── src/main/java/...
    └── build.gradle
```

---

## 下一步工作

### 阶段1: 部署云端 (当前)
- [ ] 用户在ECS上部署 `signaling/` 服务
- [ ] 验证API和WebSocket连通性

### 阶段2: 修改Windows端 (我负责)
- [ ] 修改 `pyhost/host.py` 接入云端信令
- [ ] 实现Token认证流程
- [ ] 实现SDP/ICE交换逻辑
- [ ] 本地测试

### 阶段3: 开发Android端 (我负责)
- [ ] 集成WebRTC Android SDK
- [ ] 实现信令客户端
- [ ] 视频渲染 + 触摸控制
- [ ] 测试联调

### 阶段4: 端到端联调
- [ ] Android → Windows 远程桌面
- [ ] 延迟优化
- [ ] 网络异常处理

---

## 测试记录

```
============================================================
  ALL TESTS PASSED!
  Signaling server architecture is ready for cloud deployment
============================================================

[PASS] Health check
[PASS] Token: L29TB7, Room: 21a69f2fb6b60979
[PASS] STUN: ['stun:stun.l.google.com:19302', 'stun:stun1.l.google.com:19302']
[HOST] Results: ['join_ack', 'sdp_answer', 'ice_candidate_received', 'connecting_sent']
[CLIENT] Results: ['join_ack', 'sdp_offer_received', 'ice_candidate_received', 'connecting_sent']
```
