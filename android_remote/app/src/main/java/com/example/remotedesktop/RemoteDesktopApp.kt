package com.example.remotedesktop

import android.app.Application
import org.webrtc.PeerConnectionFactory

class RemoteDesktopApp : Application() {
    
    override fun onCreate() {
        super.onCreate()
        
        // 初始化WebRTC
        val options = PeerConnectionFactory.InitializationOptions.builder()
            .createInitializationOptions()
        PeerConnectionFactory.initialize(options)
    }
}
