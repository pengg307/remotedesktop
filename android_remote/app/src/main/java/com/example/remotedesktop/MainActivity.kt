package com.example.remotedesktop

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.util.Log
import android.view.MotionEvent
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.widget.*
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import org.json.JSONObject
import org.webrtc.*

class MainActivity : AppCompatActivity() {

    companion object {
        private const val TAG = "RemoteDesk"
        private const val PERMISSION_REQUEST_CODE = 100
    }

    private lateinit var serverEditText: EditText
    private lateinit var tokenEditText: EditText
    private lateinit var connectButton: Button
    private lateinit var statusText: TextView
    private lateinit var videoView: SurfaceViewRenderer

    private var peerConnection: PeerConnection? = null
    private var signalingClient: SignalingClient? = null
    private var peerConnectionFactory: PeerConnectionFactory? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
        setContentView(R.layout.activity_main)

        serverEditText = findViewById(R.id.serverEditText)
        tokenEditText = findViewById(R.id.tokenEditText)
        connectButton = findViewById(R.id.connectButton)
        statusText = findViewById(R.id.statusText)
        videoView = findViewById(R.id.videoView)

        videoView.init(null, null)
        videoView.setScalingType(RendererCommon.ScalingType.SCALE_ASPECT_FILL)

        val touchOverlay = View(this).apply {
            setBackgroundColor(Color.TRANSPARENT)
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT
            )
            isClickable = true
            isFocusable = true
            setOnTouchListener { _, event ->
                handleTouchEvent(event)
                true
            }
        }
        findViewById<ViewGroup>(android.R.id.content).addView(touchOverlay)

        val prefs = getSharedPreferences("settings", MODE_PRIVATE)
        val savedUrl = prefs.getString("signaling_url", "")
        if (!savedUrl.isNullOrEmpty()) {
            serverEditText.setText(savedUrl)
        }

        connectButton.setOnClickListener {
            val url = serverEditText.text.toString().trim()
            val token = tokenEditText.text.toString().trim()

            if (url.isEmpty() || token.isEmpty()) {
                showStatus("请输入服务器地址和Token", false)
                return@setOnClickListener
            }
            if (!url.startsWith("http")) {
                showStatus("服务器地址格式错误", false)
                return@setOnClickListener
            }

            prefs.edit().putString("signaling_url", url).apply()

            if (signalingClient == null || !signalingClient!!.isConnected) {
                connectToServer(url, token)
            } else {
                disconnect()
            }
        }

        requestPermissions()
    }

    private fun connectToServer(url: String, token: String) {
        showStatus("正在连接...", false)
        connectButton.isEnabled = false
        connectButton.text = "连接中..."

        signalingClient = SignalingClient(this, url, token)

        signalingClient?.setCallback(object : SignalingClient.Callback {
            override fun onJoined(roomId: String) {
                Log.d(TAG, "已加入房间: $roomId")
                runOnUiThread { showStatus("已连接，等待屏幕共享...", true) }
            }

            override fun onSdpOffer(offer: String) {
                Log.d(TAG, "收到SDP Offer")
                runOnUiThread { showStatus("开始建立视频连接...", true) }
                handleSdpOffer(offer)
            }

            override fun onIceCandidate(candidate: IceCandidate) {
                Log.d(TAG, "收到ICE候选")
                signalingClient?.sendIceCandidate(candidate)
            }

            override fun onConnectionStateChanged(state: String) {
                Log.d(TAG, "连接状态: $state")
                runOnUiThread {
                    when (state) {
                        "connected" -> {
                            showStatus("已连接", true)
                            connectButton.isEnabled = true
                            connectButton.text = "断开"
                        }
                        "disconnected", "closed" -> {
                            showStatus("连接已断开", false)
                            connectButton.isEnabled = true
                            connectButton.text = "连接"
                        }
                        else -> showStatus(state, false)
                    }
                }
            }

            override fun onError(message: String) {
                Log.e(TAG, "错误: $message")
                runOnUiThread {
                    showStatus("错误: $message", false)
                    connectButton.isEnabled = true
                    connectButton.text = "连接"
                }
            }
        })

        signalingClient?.start()
    }

    private fun handleSdpOffer(offer: String) {
        if (peerConnectionFactory == null) {
            peerConnectionFactory = PeerConnectionFactory.builder()
                .createPeerConnectionFactory()
        }

        val rtcConfig = PeerConnection.RTCConfiguration(emptyList())
        rtcConfig.iceServers = listOf(
            PeerConnection.IceServer.builder("stun:stun.l.google.com:19302").createIceServer(),
            PeerConnection.IceServer.builder("stun:stun1.l.google.com:19302").createIceServer()
        )

        peerConnection = peerConnectionFactory?.createPeerConnection(rtcConfig, object : PeerConnection.Observer {
            override fun onSignalingChange(state: PeerConnection.SignalingState) {
                Log.d(TAG, "信令状态: $state")
            }

            override fun onIceConnectionChange(state: PeerConnection.IceConnectionState) {
                Log.d(TAG, "ICE连接状态: $state")
                if (state == PeerConnection.IceConnectionState.CONNECTED) {
                    runOnUiThread { showStatus("视频连接成功!", true) }
                }
            }

            override fun onIceGatheringChange(state: PeerConnection.IceGatheringState) {
                Log.d(TAG, "ICE收集状态: $state")
            }

            override fun onIceCandidate(candidate: IceCandidate) {
                signalingClient?.sendIceCandidate(candidate)
            }

            override fun onIceCandidatesRemoved(candidates: Array<out IceCandidate>) {}

            override fun onAddTrack(track: MediaStreamTrack, streams: Array<MediaStream>) {
                Log.d(TAG, "添加轨道: ${track.kind}")
                if (track.kind == "video") {
                    track.setEnabled(true)
                    videoView.setMirror(false)
                    track.addSink(videoView)
                }
            }

            override fun onRemoveTrack(track: MediaStreamTrack) {
                Log.d(TAG, "移除轨道")
            }

            override fun onRemoveStream(stream: MediaStream) {}
            override fun onDataChannel(channel: DataChannel) {}
            override fun onRenegotiationNeeded() {}
            override fun onIceConnectionReceivingChange(receiving: Boolean) {}
        })

        val sdp = SessionDescription(SessionDescription.Type.OFFER, offer)
        peerConnection?.setRemoteDescription(object : SdpObserver {
            override fun onCreateSuccess() {}
            override fun onSetSuccess() {
                Log.d(TAG, "设置远程描述成功")
                peerConnection?.createAnswer(object : SdpObserver {
                    override fun onCreateSuccess(sdp: SessionDescription) {
                        Log.d(TAG, "创建Answer成功")
                        signalingClient?.sendSdpAnswer(sdp.description)
                        peerConnection?.setLocalDescription(this, sdp)
                    }
                    override fun onSetSuccess() {}
                    override fun onCreateFailure(error: String?) {
                        Log.e(TAG, "创建Answer失败: $error")
                    }
                    override fun onSetFailure(error: String?) {
                        Log.e(TAG, "设置Answer失败: $error")
                    }
                }, MediaConstraints())
            }
            override fun onCreateFailure(error: String?) {
                Log.e(TAG, "创建Offer失败: $error")
            }
            override fun onSetFailure(error: String?) {
                Log.e(TAG, "设置远程描述失败: $error")
            }
        }, sdp)
    }

    private var lastTouchX = 0f
    private var lastTouchY = 0f

    private fun handleTouchEvent(event: MotionEvent): Boolean {
        if (signalingClient == null) return false

        when (event.action and MotionEvent.ACTION_MASK) {
            MotionEvent.ACTION_DOWN, MotionEvent.ACTION_POINTER_DOWN -> {
                val (x, y) = scaleCoordinates(event.x, event.y)
                sendInputEvent("mouse_move", x, y)
            }
            MotionEvent.ACTION_MOVE -> {
                val (x, y) = scaleCoordinates(event.x, event.y)
                sendInputEvent("mouse_move", x, y)
                lastTouchX = x
                lastTouchY = y
            }
            MotionEvent.ACTION_UP, MotionEvent.ACTION_POINTER_UP -> {
                val (x, y) = scaleCoordinates(lastTouchX, lastTouchY)
                sendInputEvent("mouse_click", x, y)
            }
        }
        return true
    }

    private fun scaleCoordinates(x: Float, y: Float): Pair<Float, Float> {
        val screenWidth = resources.displayMetrics.widthPixels
        val screenHeight = resources.displayMetrics.heightPixels
        return Pair(
            (x / screenWidth * 100).toFloat(),
            (y / screenHeight * 100).toFloat()
        )
    }

    private fun sendInputEvent(action: String, x: Float, y: Float) {
        try {
            val msg = """{"type":"input","data":{"action":"$action","x":$x,"y":$y}}"""
            signalingClient?.sendInput(msg)
            Log.d(TAG, "发送输入事件: $action at ($x, $y)")
        } catch (e: Exception) {
            Log.e(TAG, "发送输入失败: ${e.message}")
        }
    }

    private fun disconnect() {
        Log.d(TAG, "断开连接")
        peerConnection?.dispose()
        peerConnection = null
        signalingClient?.stop()
        signalingClient = null
        videoView.release()
        showStatus("已断开", false)
        connectButton.isEnabled = true
        connectButton.text = "连接"
    }

    private fun requestPermissions() {
        val permissions = listOf(
            Manifest.permission.INTERNET,
            Manifest.permission.RECORD_AUDIO
        )
        val notGranted = permissions.filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (notGranted.isNotEmpty()) {
            ActivityCompat.requestPermissions(
                this,
                notGranted.toTypedArray(),
                PERMISSION_REQUEST_CODE
            )
        }
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PERMISSION_REQUEST_CODE) {
            val allGranted = grantResults.all { it == PackageManager.PERMISSION_GRANTED }
            if (!allGranted) {
                showStatus("需要网络权限才能运行", false)
            }
        }
    }

    private fun showStatus(message: String, isSuccess: Boolean) {
        statusText.text = message
        statusText.setTextColor(
            ContextCompat.getColor(
                this,
                if (isSuccess) android.R.color.holo_green_dark
                else android.R.color.holo_red_dark
            )
        )
    }

    override fun onDestroy() {
        super.onDestroy()
        disconnect()
    }
}

class SignalingClient(
    private val context: android.content.Context,
    private val signalingUrl: String,
    private val token: String
) {
    interface Callback {
        fun onJoined(roomId: String)
        fun onSdpOffer(offer: String)
        fun onIceCandidate(candidate: IceCandidate)
        fun onConnectionStateChanged(state: String)
        fun onError(message: String)
    }

    private var callback: Callback? = null
    private var ws: okhttp3.WebSocket? = null
    private var roomId: String? = null
    private var isConnecting = false

    private val client = okhttp3.OkHttpClient.Builder()
        .connectTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
        .readTimeout(30, java.util.concurrent.TimeUnit.SECONDS)
        .build()

    fun setCallback(cb: Callback) { callback = cb }
    fun isConnected() = ws != null && isConnecting

    fun start() {
        Log.i(TAG, "启动信令连接到: $signalingUrl")
        connect()
    }

    private fun connect() {
        isConnecting = true
        val tokenUrl = "$signalingUrl/api/token"
        val tokenRequest = okhttp3.Request.Builder()
            .url(tokenUrl)
            .post(okhttp3.RequestBody.create(null, ""))
            .build()

        client.newCall(tokenRequest).enqueue(object : okhttp3.Callback {
            override fun onResponse(call: okhttp3.Call, response: okhttp3.Response) {
                response.use {
                    if (!it.isSuccessful) {
                        callback?.onError("获取Token失败: ${it.code}")
                        return
                    }
                    val body = it.body?.string()
                    try {
                        val json = JSONObject(body ?: "{}")
                        roomId = json.getString("room_id")
                        Log.i(TAG, "获取到房间: $roomId")
                        connectWebSocket()
                    } catch (e: Exception) {
                        callback?.onError("解析响应失败: ${e.message}")
                    }
                }
            }

            override fun onFailure(call: okhttp3.Call, e: java.io.IOException) {
                callback?.onError("网络错误: ${e.message}")
            }
        })
    }

    private fun connectWebSocket() {
        val wsUrl = "$signalingUrl/ws/$roomId?role=client"
        Log.i(TAG, "连接WebSocket: $wsUrl")

        val wsRequest = okhttp3.Request.Builder()
            .url(wsUrl)
            .build()

        ws = client.newWebSocket(wsRequest, object : okhttp3.WebSocketListener() {
            override fun onOpen(websocket: okhttp3.WebSocket, response: okhttp3.Response) {
                Log.i(TAG, "WebSocket已打开")
                callback?.onConnectionStateChanged("connected")
            }

            override fun onMessage(websocket: okhttp3.WebSocket, text: String) {
                Log.d(TAG, "收到消息: $text")
                try {
                    val msg = JSONObject(text)
                    when (msg.getString("type")) {
                        "join_ack" -> {
                            Log.i(TAG, "加入成功: ${msg.getJSONObject("data")}")
                            callback?.onJoined(roomId ?: "")
                        }
                        "sdp_offer" -> {
                            val sdp = msg.getJSONObject("data").getString("sdp")
                            callback?.onSdpOffer(sdp)
                        }
                        "ice_candidate" -> {
                            val data = msg.getJSONObject("data")
                            val candidate = IceCandidate(
                                data.getString("sdpMid"),
                                data.getInt("sdpMLineIndex"),
                                data.getString("candidate")
                            )
                            callback?.onIceCandidate(candidate)
                        }
                        "error" -> {
                            callback?.onError(msg.getString("message"))
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "解析消息失败: ${e.message}")
                }
            }

            override fun onClosing(websocket: okhttp3.WebSocket, code: Int, reason: String) {
                Log.i(TAG, "WebSocket关闭: $reason")
                websocket.close(code, null)
                callback?.onConnectionStateChanged("disconnected")
            }

            override fun onFailure(websocket: okhttp3.WebSocket, t: Throwable, response: okhttp3.Response) {
                Log.e(TAG, "WebSocket错误: ${t.message}")
                callback?.onError(t.message ?: "连接失败")
            }
        })
    }

    fun sendSdpOffer(offer: String) {
        val msg = """{"type":"sdp_offer","data":{"sdp":"$offer"}}"""
        send(msg)
    }

    fun sendSdpAnswer(answer: String) {
        val msg = """{"type":"sdp_answer","data":{"sdp":"$answer"}}"""
        send(msg)
    }

    fun sendIceCandidate(candidate: IceCandidate) {
        val msg = """{"type":"ice_candidate","data":{"candidate":"${candidate.sdp}","sdpMid":"${candidate.sdpMid}","sdpMLineIndex":${candidate.sdpMLineIndex}}"""
        send(msg)
    }

    fun sendInput(message: String) {
        send(message)
    }

    private fun send(message: String) {
        ws?.send(message)
    }

    fun stop() {
        isConnecting = false
        ws?.close(1000, "User disconnect")
        ws = null
    }
}
