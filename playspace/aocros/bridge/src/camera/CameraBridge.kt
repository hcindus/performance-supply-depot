/**n * AndroidCameraBridge.ktn * Stream camera feed to Mylzeron (Pi 5)n */npackage com.aocros.bridge.sensornnimport android.content.Contextnimport android.hardware.camera2.*nimport kotlinx.coroutines.flow.MutableStateFlownnclass CameraBridge(context: Context, private val piEndpoint: String) {n    private val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManagern    private val _frameFlow = MutableStateFlow<ByteArray?>(null)n    val frameFlow = _frameFlow
    
    suspend fun startStream() {n        // Continuously capture and POST to Pi 5n        // Implementation: Camera2 API + OkHttpn    }n    
    fun stopStream() {n        // Clean shutdownn    }n}
