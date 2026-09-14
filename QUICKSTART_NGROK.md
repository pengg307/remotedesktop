# 快速开始 - ngrok公网访问

## 步骤1: 注册ngrok账号
1. 打开浏览器访问: https://dashboard.ngrok.com/signup
2. 填写邮箱和密码注册
3. 验证邮箱

## 步骤2: 获取Auth Token
1. 登录后点击 "Getting Started"
2. 找到 "Authtoken" 部分
3. 点击 "Look for an authtoken?"
4. 复制token: `2xYz1234abcDEFghIJKlmno...`

## 步骤3: 下载ngrok
1. 访问: https://ngrok.com/download
2. 选择 "Windows 64-bit"
3. 下载后解压到: `E:\ngrok`

## 步骤4: 配置ngrok
1. 打开CMD或PowerShell
2. 运行以下命令:

```powershell
cd E:\ngrok
ngrok config add-authtoken YOUR_TOKEN_HERE
```

## 步骤5: 启动隧道
```powershell
cd E:\ngrok
ngrok http 8000
```

你会看到类似输出:
```
Forwarding  https://abc123.ngrok.io -> http://localhost:8000
```

## 步骤6: 记录URL
复制显示的URL，例如: `https://abc123.ngrok.io`

## 步骤7: Android连接
在Android应用中设置:
- 信令服务器: `https://abc123.ngrok.io`
- Token: (从API获取)

## 验证连接
```bash
# 测试公网访问
curl -X POST https://abc123.ngrok.io/api/token
```
