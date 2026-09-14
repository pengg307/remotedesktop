# 信令服务器状态

## 运行状态
- 服务: ✅ 运行中
- 端口: 8000
- 局域网地址: http://192.168.1.3:8000
- 公网地址: ❌ 未配置

## 已生成Token
```
Token: 485Q7V
RoomID: ed4f18c4a3831545
过期时间: 30分钟
```

## API测试
```bash
curl -X POST http://localhost:8000/api/token
# 返回: {"token":"XXXXXX","room_id":"...","expires_in_minutes":30}
```

## 下一步
1. 配置ngrok实现公网访问
2. 或先用WiFi测试局域网连接
