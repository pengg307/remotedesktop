package com.example.remotedesktop

import android.app.Application
import org.webrtc.PeerConnectionFactory

class RemoteDesktopApp : Application() {

    override fun onCreate() {
        super.onCreate()

        val options = PeerConnectionFactory.InitializationOptions.builder()
            .setEnableInternalTracer(true)
            .createInitializationOptions()
        PeerConnectionFactory.initialize(options)
    }
}
