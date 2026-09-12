import 'package:flutter/material.dart';
import 'package:flutter_webrtc/flutter_webrtc.dart';
import 'package:http/http as http';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'dart:convert';

void main() {
  runApp(const RemoteDesktopApp());
}

class RemoteDesktopApp extends StatelessWidget {
  const RemoteDesktopApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: '远程桌面',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
        useMaterial3: true,
      ),
      home: const ConnectPage(),
    );
  }
}

// 连接页面
class ConnectPage extends StatefulWidget {
  const ConnectPage({super.key});

  @override
  State<ConnectPage> createState() => _ConnectPageState();
}

class _ConnectPageState extends State<ConnectPage> {
  final TextEditingController _tokenController = TextEditingController();
  final TextEditingController _serverUrlController = TextEditingController(
    text: 'ws://localhost:8000'
  );
  bool _connecting = false;
  String _error = '';

  Future<void> _connect() async {
    final token = _tokenController.text.trim().toUpperCase();
    if (token.length != 6) {
      setState(() => _error = '请输入6位Token');
      return;
    }

    setState(() {
      _connecting = true;
      _error = '';
    });

    try {
      // 向信令服务器请求连接
      final serverUrl = _serverUrlController.text.trim();
      final response = await http.post(
        Uri.parse('$serverUrl/api/join'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'token': token}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (mounted) {
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (_) => DesktopPage(
                token: token,
                roomData: data,
                serverUrl: serverUrl,
              ),
            ),
          );
        }
      } else {
        setState(() => _error = '连接失败: ${response.statusCode}');
      }
    } catch (e) {
      setState(() => _error = '网络错误: $e');
    } finally {
      if (mounted) {
        setState(() => _connecting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('远程桌面控制')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Icon(Icons.computer, size: 80, color: Colors.blue),
            const SizedBox(height: 24),
            const Text(
              '输入Windows端显示的6位Token',
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 18),
            ),
            const SizedBox(height: 32),
            TextField(
              controller: _tokenController,
              keyboardType: TextInputType.text,
              textCapitalization: TextCapitalization.characters,
              decoration: const InputDecoration(
                labelText: 'Token',
                hintText: '例如: ABCD12',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.key),
              ),
              style: const TextStyle(
                fontSize: 24,
                letterSpacing: 8,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _serverUrlController,
              decoration: const InputDecoration(
                labelText: '信令服务器地址',
                hintText: 'ws://192.168.1.100:8000',
                border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.cloud),
              ),
            ),
            if (_error.isNotEmpty) ...[
              const SizedBox(height: 16),
              Text(_error, style: const TextStyle(color: Colors.red)),
            ],
            const SizedBox(height: 32),
            ElevatedButton(
              onPressed: _connecting ? null : _connect,
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
              child: _connecting
                  ? const SizedBox(
                      height: 24,
                      width: 24,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('连接', style: TextStyle(fontSize: 18)),
            ),
          ],
        ),
      ),
    );
  }
}

// 桌面控制页面
class DesktopPage extends StatefulWidget {
  final String token;
  final Map<String, dynamic> roomData;
  final String serverUrl;

  const DesktopPage({
    super.key,
    required this.token,
    required this.roomData,
    required this.serverUrl,
  });

  @override
  State<DesktopPage> createState() => _DesktopPageState();
}

class _DesktopPageState extends State<DesktopPage> {
  late final RTCPeerConnection _pc;
  late final MediaStream _localStream;
  RTCVideoRenderer _remoteRenderer = RTCVideoRenderer();
  bool _isConnected = false;
  bool _isMuted = false;
  
  // 触摸控制状态
  DateTime? _touchStartTime;
  bool _isLongPress = false;

  @override
  void initState() {
    super.initState();
    _initWebRTC();
  }

  Future<void> _initWebRTC() async {
    try {
      // 创建PeerConnection
      _pc = await createPeerConnection({
        'iceServers': [
          {'urls': 'stun:stun.l.google.com:19302'},
          {'urls': 'stun:stun1.l.google.com:19302'},
        ]
      });

      // 获取本地摄像头/屏幕流（用于音视频）
      _localStream = await navigator.mediaDevices.getUserMedia({
        'video': false,
        'audio': false,
      });

      // 添加本地轨道
      _localStream.getTracks().forEach((track) {
        _pc.addTrack(track, _localStream);
      });

      // 监听数据通道（用于控制）
      _pc.onDataChannel = (RTCDataChannel channel) {
        channel.onMessage = _onMessage;
      };

      // 监听远程视频流
      _pc.onTrack = (RTCTransceiver event) {
        if (event.track.kind == 'video') {
          _remoteRenderer.srcObject = event.streams[0];
          setState(() => _isConnected = true);
        }
      };

      // 创建信令WebSocket连接
      await _setupSignaling();
      
    } catch (e) {
      debugPrint('WebRTC初始化错误: $e');
    }
  }

  Future<void> _setupSignaling() async {
    final channel = WebSocketChannel.connect(
      Uri.parse('${widget.serverUrl}/ws/${widget.roomData['room_id']}'),
    );
    
    channel.stream.listen((message) {
      final data = jsonDecode(message);
      if (data['type'] == 'answer') {
        _pc.setRemoteDescription(
          RTCSessionDescription(data['sdp'], 'answer')
        );
      }
    });
  }

  void _onMessage(RTCDataChannelMessage message) {
    // 处理来自Windows的控制确认
    final data = jsonDecode(message.text);
    debugPrint('收到消息: $data');
  }

  // 触摸事件处理
  void _onPanStart(DragStartDetails details) {
    _touchStartTime = DateTime.now();
    _isLongPress = false;
    _sendTouchEvent('touch_start', details.localPosition);
  }

  void _onPanUpdate(DragUpdateDetails details) {
    if (_isLongPress) return;
    
    final now = DateTime.now();
    final duration = now.difference(_touchStartTime!);
    
    // 长按检测
    if (duration.inMilliseconds > 500) {
      _isLongPress = true;
      _sendMouseAction('right_click');
    } else {
      _sendMouseMove(details.localPosition);
    }
  }

  void _onPanEnd(DragEndDetails details) {
    if (!_isLongPress) {
      _sendMouseAction('left_click');
    }
    _isLongPress = false;
  }

  void _sendTouchEvent(String type, Offset position) {
    // TODO: 通过数据通道发送触摸事件
  }

  void _sendMouseMove(Offset position) {
    // 将触摸坐标转换为屏幕坐标
    final screenWidth = MediaQuery.of(context).size.width;
    final screenHeight = MediaQuery.of(context).size.height;
    
    // TODO: 发送鼠标移动事件
  }

  void _sendMouseAction(String action) {
    // TODO: 发送鼠标点击/滚动事件
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('连接中: ${widget.token}'),
        actions: [
          IconButton(
            icon: Icon(_isMuted ? Icons.mic_off : Icons.mic),
            onPressed: () => setState(() => _isMuted = !_isMuted),
          ),
          IconButton(
            icon: const Icon(Icons.stop),
            onPressed: () => _disconnect(),
          ),
        ],
      ),
      body: Stack(
        children: [
          // 远程桌面视频显示
          _isConnected
              ? RTCVideoView(
                  _remoteRenderer,
                  objectFit: RTCVideoViewObjectFit.RTCVideoViewObjectFitContain,
                  mirror: false,
                )
              : const Center(child: CircularProgressIndicator()),
          
          // 触摸控制层
          Positioned.fill(
            child: GestureDetector(
              onPanStart: _onPanStart,
              onPanUpdate: _onPanUpdate,
              onPanEnd: _onPanEnd,
              child: Container(),
            ),
          ),
          
          // 底部控制栏
          Positioned(
            bottom: 0,
            left: 0,
            right: 0,
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                  colors: [Colors.black54, Colors.transparent],
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _ControlButton(icon: Icons.keyboard, label: '键盘', onTap: _showKeyboard),
                  _ControlButton(icon: Icons.mouse, label: '鼠标', onTap: () {}),
                  _ControlButton(icon: Icons.scrollable, label: '滚动', onTap: () {}),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _showKeyboard() {
    // TODO: 显示虚拟键盘
  }

  Future<void> _disconnect() async {
    await _pc.close();
    await _remoteRenderer.dispose();
    if (mounted) {
      Navigator.popUntil(context, (route) => route.isFirst);
    }
  }

  @override
  void dispose() {
    _remoteRenderer.dispose();
    _pc.close();
    super.dispose();
  }
}

class _ControlButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _ControlButton({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        IconButton(
          icon: Icon(icon, color: Colors.white, size: 32),
          onPressed: onTap,
        ),
        Text(label, style: const TextStyle(color: Colors.white, fontSize: 12)),
      ],
    );
  }
}
