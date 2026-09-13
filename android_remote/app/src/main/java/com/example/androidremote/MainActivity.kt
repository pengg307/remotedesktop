package com.example.androidremote

import android.os.Bundle
import android.widget.*
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    
    private lateinit var tokenEditText: EditText
    private lateinit var serverEditText: EditText
    private lateinit var connectButton: Button
    private lateinit var statusText: TextView
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        tokenEditText = findViewById(R.id.tokenEditText)
        serverEditText = findViewById(R.id.serverEditText)
        connectButton = findViewById(R.id.connectButton)
        statusText = findViewById(R.id.statusText)
        
        connectButton.setOnClickListener {
            val token = tokenEditText.text.toString().trim()
            val server = serverEditText.text.toString().trim()
            
            if (token.isEmpty() || server.isEmpty()) {
                statusText.text = "请输入Token和服务器地址"
                statusText.setTextColor(resources.getColor(android.R.color.holo_red_dark))
            } else {
                statusText.text = "连接功能开发中..."
                statusText.setTextColor(resources.getColor(android.R.color.holo_blue_dark))
                Toast.makeText(this, "Token: $token\nServer: $server", Toast.LENGTH_LONG).show()
            }
        }
    }
}
