/**n * AndroidMicBridge.ktn * Audio capture for Mylzeronn */npackage com.aocros.bridge.sensornnimport android.content.Contextnimport android.media.AudioRecordnimport android.media.MediaRecordernimport kotlinx.coroutines.flow.Flownimport kotlinx.coroutines.flow.flow

class MicBridge(context: Context, private val piEndpoint: String) {
    private val bufferSize = AudioRecord.getMinBufferSize(
        44100, 
        android.media.AudioFormat.CHANNEL_IN_MONO,
        android.media.AudioFormat.ENCODING_PCM_16BIT
    )
    
    // Wake word: "Mylzeron"
    private val wakeWordDetector = WakeWordDetector("mylzeron")
    
    fun startListening(): Flow<ByteArray> = flow {
        // Implementation: AudioRecord + wake wordn    }
    
    suspend fun sendToPi(audioData: ByteArray) {n        // POST to Pi 5's STT endpointn    }
}
