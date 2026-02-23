/**
 * NetworkBridge.kt
 * HTTP/WebSocket connection to Pi 5 brain
 */
package com.aocros.bridge.network

import okhttp3.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import java.util.concurrent.TimeUnit

class NetworkBridge(private val piEndpoint: String = "http://192.168.1.100:5000") {
    private val client = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()
    
    private var ws: WebSocket? = null
    
    suspend fun sendSensorData(type: String, data: ByteArray): Result<String> {
        val request = Request.Builder()
            .url("$piEndpoint/sensor/$type")
            .post(RequestBody.create(MediaType.parse("application/octet-stream"), data))
            .build()
            
        return try {
            val response = client.newCall(request).execute()
            if (response.isSuccessful) {
                Result.success(response.body()?.string() ?: "")
            } else {
                Result.failure(Exception("HTTP ${response.code()}"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    fun connectWebSocket(): Flow<String> = flow {
        val request = Request.Builder()
            .url("$piEndpoint/ws")
            .build()
            
        val listener = object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                // Emit to flow
            }
        }
        
        ws = client.newWebSocket(request, listener)
    }
    
    fun sendCommand(command: String) {
        ws?.send(command)
    }
}

// Pi 5 endpoint handlers:
// POST /sensor/camera - receive image frames
// POST /sensor/audio - receive audio chunks
// POST /command - receive commands from Pi 5
// WS /ws - bidirectional stream
