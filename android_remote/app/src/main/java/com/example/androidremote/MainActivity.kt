package com.example.androidremote

import android.content.pm.PackageManager
import android.os.Bundle
import android.view.SurfaceView
import android.view.View
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import org.webrtc.*

class MainActivity : AppCompatActivity() {
    
    private lateinit var tokenEditText: EditText
    private lateinit var serverEditText: EditText
    private lateinit var connectButton: Button
    private lateinit var statusText: TextView
    private lateinit var videoView: SurfaceViewRenderer
    
    private var peerConnection: PeerConnection? = null
    private var localStream: MediaStream? = null
    private var isConnected = false
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        tokenEditText = findViewById(R.id.tokenEditText)
        serverEditText = findViewById(R.id.serverEditText)
        connectButton = findViewById(R.id.connectButton)
        statusText = findViewById(R.id.statusText)
        videoView = findViewById(R.id.videoView)
        
        videoView.init(EglBase.create().eglBaseContext, null)
        
        connectButton.setOnClickListener {
            if (isConnected) {
                disconnect()
            } else {
                connect()
            }
        }
        
        checkPermissions()
    }
    
    private fun checkPermissions() {
        val permissions = arrayOf(
            android.Manifest.permission.CAMERA,
            android.Manifest.permission.RECORD_AUDIO
        )
        val notGranted = permissions.filter { 
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED 
        }
        if (notGranted.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, notGranted.toTypedArray(), 100)
        }
    }
    
    private fun connect() {
        val token = tokenEditText.text.toString().trim()
        val serverUrl = serverEditText.text.toString().trim()
        
        if (token.isEmpty() || serverUrl.isEmpty()) {
            statusText.text = "请输入Token和服务器地址"
            statusText.setTextColor(resources.getColor(android.R.color.holo_red_dark))
            return
        }
        
        statusText.text = "连接中..."
        statusText.setTextColor(resources.getColor(android.R.color.holo_blue_dark))
        
        // TODO: 实现信令服务器连接和WebRTC逻辑
        // 这里简化为模拟连接
        Toast.makeText(this, "功能开发中...", Toast.LENGTH_SHORT).show()
    }
    
    private fun disconnect() {
        peerConnection?.close()
        peerConnection = null
        localStream?.let { 
            it.tracks.forEach { track -> track.stop() }
            applicationContext.stopMediaProjection()
        }
        localStream = null
        isConnected = false
        connectButton.text = "连接"
        statusText.text = "已断开连接"
        statusText.setTextColor(resources.getColor(android.R.color.darker_gray))
    }
    
    override fun onDestroy() {
        super.onDestroy()
        if (isConnected) disconnect()
    }
}

// 扩展函数用于停止媒体投影
fun Context.stopMediaProjection() {}
