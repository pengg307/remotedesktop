import 'package:flutter/material.dart';
import 'package:http/http as http';
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
      theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue), useMaterial3: true),
      home: const ConnectPage(),
    );
  }
}

class ConnectPage extends StatefulWidget {
  const ConnectPage({super.key});
  
  @override
  State<ConnectPage> createState() => _ConnectPageState();
}

class _ConnectPageState extends State<ConnectPage> {
  final TextEditingController _tokenController = TextEditingController();
  final TextEditingController _serverUrlController = TextEditingController(text: 'http://192.168.1.100:8000');
  bool _connecting = false;
  String _error = '';

  Future<void> _connect() async {
    final token = _tokenController.text.trim().toUpperCase();
    if (token.length != 6) {
      setState(() => _error = '请输入6位Token');
      return;
    }
    setState(() { _connecting = true; _error = ''; });
    try {
      final serverUrl = _serverUrlController.text.trim().replaceAll(RegExp(r'/+$'), '');
      final response = await http.post(
        Uri.parse('$serverUrl/api/token'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'token': token}),
      );
      if (response.statusCode == 200) {
        if (mounted) {
          Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const DesktopPage()));
        }
      } else {
        setState(() => _error = '连接失败: ${response.statusCode}');
      }
    } catch (e) {
      setState(() => _error = '网络错误: $e');
    } finally {
      if (mounted) setState(() => _connecting = false);
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
            const Text('输入Windows端显示的6位Token', textAlign: TextAlign.center, style: TextStyle(fontSize: 18)),
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
              style: const TextStyle(fontSize: 24, letterSpacing: 8, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _serverUrlController,
              decoration: const InputDecoration(
                labelText: '信令服务器地址',
                hintText: 'http://192.168.1.100:8000',
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
              style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 16)),
              child: _connecting 
                ? const SizedBox(height: 24, width: 24, child: CircularProgressIndicator(strokeWidth: 2)) 
                : const Text('连接', style: TextStyle(fontSize: 18)),
            ),
          ],
        ),
      ),
    );
  }
}

class DesktopPage extends StatelessWidget {
  const DesktopPage({super.key});
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('连接中...')),
      body: const Center(child: CircularProgressIndicator()),
    );
  }
}
