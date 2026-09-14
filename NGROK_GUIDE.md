# ngrok 内网穿透配置指南

## 什么是ngrok？
ngrok是一个内网穿透工具，可以让局域网内的服务暴露到公网，无需公网IP或路由器配置。

## 为什么需要ngrok？
- 手机用SIM卡网络，电脑在局域网
- 两者不在同一网络，无法直接访问
- ngrok创建一个公网URL，手机可以通过这个URL访问电脑服务

## 安装步骤

### 1. 下载ngrok
**方式A: 官方网站下载**
- 访问: https://ngrok.com/download
- 选择 Windows 版本
- 解压到任意目录（如 `C:\ngrok`）

**方式B: 使用包管理器**
```powershell
# Chocolatey
choco install ngrok

# Scoop
scoop install ngrok
```

### 2. 注册并获取认证令牌
```
1. 访问: https://dashboard.ngrok.com/signup
2. 注册免费账号
3. 登录后获取 Auth Token
4. 运行: ngrok config add-authtoken <你的token>
```

### 3. 启动隧道
```powershell
cd C:\ngrok
ngrok http 8000
```

### 4. 获取公网URL
启动后会显示类似：
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

### 5. Android连接配置
在Android应用中设置：
- 信令服务器: `https://abc123.ngrok.io`
- Token: (从服务器获取)

## 使用方法

### 启动ngrok（双击运行）
```
E:\aiprojects\RemoteDesktop\start_ngrok.bat
```

### 获取Token
```bash
curl -X POST http://localhost:8000/api/token
# 返回: {"token":"XXXXXX","room_id":"...","expires_in_minutes":30}
```

### 测试连接
```
1. 保持ngrok运行
2. 在Android应用中输入:
   - 服务器: https://xxxx.ngrok.io
   - Token: XXXXXX
3. 点击连接
```

## 注意事项

### 免费限制
- 每分钟连接数有限制
- URL会随机变化（重启后不同）
- 需要手动注册获取固定子域名

### 替代方案
如果ngrok不方便，可以：
1. Cloudflare Tunnel (免费)
2. Frp (开源，需要VPS)
3. 路由器端口转发

## 常见问题

### Q: ngrok连接失败？
A: 检查:
- 信令服务器是否运行
- ngrok是否已认证
- 防火墙是否阻止

### Q: Android连接不上？
A: 检查:
- ngrok URL是否正确
- Token是否过期
- 网络是否通畅

### Q: 想要固定URL？
A: 升级ngrok到付费计划，或注册免费账号获取固定子域名
