/**n * AndroidSpeakerBridge.ktn * TTS and audio output for Mylzeronn */npackage com.aocros.bridge.sensornnimport android.content.Contextnimport android.speech.tts.TextToSpeechnnclass SpeakerBridge(context: Context) : TextToSpeech.OnInitListener {
    private val tts: TextToSpeech = TextToSpeech(context, this)
    private var initialized = false
    
    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            // Set to "Adam" or closest male voice
            tts.language = java.util.Locale.US
            initialized = true
        }
    }
    
    fun speak(text: String) {
        if (initialized) {
            tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "aocros")
        }
    }
    
    fun playSound(effect: SoundEffect) {
        // Play sound effectsn    }
    
    fun shutdown() {
        tts.stop()
        tts.shutdown()
    }
    
    enum class SoundEffect {
        WAKE,
        CONFIRM,
        ERROR,
        PROCESSING
    }
}
