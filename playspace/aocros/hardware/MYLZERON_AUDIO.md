# ALSA Audio Integration for Mylzeron

## Overview

Mylzeron requires audio input/output for conversations. ALSA (Advanced Linux Sound Architecture) provides low-level audio support on Linux/Pi 5.

## Hardware Requirements

- USB microphone or Pi audio HAT (ReSpeaker, etc.)
- Speaker output (3.5mm jack, HDMI, or USB audio)
- Optional: Audio injector board for Pi 5

## ALSA Configuration

### /etc/asound.conf

```bash
pcm.!default {
    type asym
    playback.pcm "speaker"
    capture.pcm "microphone"
}

pcm.speaker {
    type hw
    card 0
    device 0
}

pcm.microphone {
    type hw
    card 1
    device 0
}

ctl.!default {
    type hw
    card 0
}
```

## Mylzeron Audio Module

```python
#!/usr/bin/env python3
"""Mylzeron ALSA Audio Interface"""

import alsaaudio
import numpy as np
import wave
import threading
import queue
from typing import Callable, Optional

class MylzeronAudio:
    """
    Audio I/O for Mylzeron on Pi 5
    - Capture: Wake word detection + command recognition
    - Playback: TTS responses (Adam voice)
    """
    
    def __init__(self, sample_rate=16000, channels=1):
        self.sample_rate = sample_rate
        self.channels = channels
        self.format = alsaaudio.PCM_FORMAT_S16_LE
        
        # Audio buffers
        self.capture_buffer = queue.Queue(maxsize=100)
        self.is_listening = False
        self.wake_word = "mylzeron"
        
        # Callbacks
        self.on_wake: Optional[Callable] = None
        self.on_command: Optional[Callable] = None
        
    def initialize(self) -> bool:
        """Setup ALSA devices"""
        try:
            # Input device (microphone)
            self.capture = alsaaudio.PCM(
                alsaaudio.PCM_CAPTURE,
                alsaaudio.PCM_NONBLOCK,
                device='default'
            )
            self.capture.setchannels(self.channels)
            self.capture.setrate(self.sample_rate)
            self.capture.setformat(self.format)
            self.capture.setperiodsize(1024)
            
            # Output device (speaker)
            self.playback = alsaaudio.PCM(
                alsaaudio.PCM_PLAYBACK,
                device='default'
            )
            self.playback.setchannels(1)
            self.playback.setrate(24000)  # ElevenLabs rate
            self.playback.setformat(self.format)
            self.playback.setperiodsize(1024)
            
            return True
        except Exception as e:
            print(f"ALSA init failed: {e}")
            return False
    
    def start_listening(self):
        """Begin wake word detection"""
        self.is_listening = True
        self.listen_thread = threading.Thread(target=self._listen_loop)
        self.listen_thread.daemon = True
        self.listen_thread.start()
        print(f"Mylzeron listening for wake word: '{self.wake_word}'")
    
    def _listen_loop(self):
        """Continuous audio capture with wake word detection"""
        audio_buffer = []
        
        while self.is_listening:
            try:
                # Read audio chunk
                length, data = self.capture.read()
                if length > 0:
                    audio_buffer.append(data)
                    
                    # Keep last 3 seconds for command context
                    max_buffer = int(self.sample_rate * 3 / 1024)
                    if len(audio_buffer) > max_buffer:
                        audio_buffer = audio_buffer[-max_buffer:]
                    
                    # Simple wake word detection (energy-based)
                    # Real implementation: use openWakeWord or Porcupine
                    if self._detect_wake_word(data):
                        print(" Wake word detected!")
                        if self.on_wake:
                            self.on_wake()
                        
                        # Capture command (next 5 seconds)
                        command_audio = self._capture_command()
                        if self.on_command:
                            self.on_command(command_audio)
                            
            except Exception as e:
                print(f"Listen error: {e}")
    
    def _detect_wake_word(self, audio_data: bytes) -> bool:
        """
        Simple energy-based wake word detection
        Replace with Porcupine or openWakeWord for production
        """
        # Convert to numpy array
        audio_np = np.frombuffer(audio_data, dtype=np.int16)
        
        # Calculate RMS energy
        rms = np.sqrt(np.mean(audio_np**2))
        
        # Threshold (adjust based on environment)
        threshold = 500
        
        return rms > threshold
    
    def _capture_command(self, duration: float = 5.0) -> bytes:
        """Capture audio for command duration"""
        frames = int(self.sample_rate * duration / 1024)
        audio_data = []
        
        for _ in range(frames):
            length, data = self.capture.read()
            if length > 0:
                audio_data.append(data)
        
        return b''.join(audio_data)
    
    def speak(self, audio_data: bytes):
        """Play TTS audio"""
        try:
            self.playback.write(audio_data)
        except Exception as e:
            print(f"Playback error: {e}")
    
    def speak_text(self, text: str, tts_service: str = "elevenlabs"):
        """
        Generate and play TTS
        - tts_service: "elevenlabs" (Adam voice), "piper", or "espeak"
        """
        if tts_service == "elevenlabs":
            audio = self._elevenlabs_tts(text)
        elif tts_service == "piper":
            audio = self._piper_tts(text)
        else:
            audio = self._espeak_tts(text)
        
        if audio:
            self.speak(audio)
    
    def _elevenlabs_tts(self, text: str) -> Optional[bytes]:
        """ElevenLabs Adam voice (requires API key)"""
        import requests
        
        try:
            response = requests.post(
                "https://api.elevenlabs.io/v1/text-to-speech/Adam",
                headers={"xi-api-key": "YOUR_API_KEY"},
                json={
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.75
                    }
                }
            )
            return response.content if response.status_code == 200 else None
        except:
            return None
    
    def _piper_tts(self, text: str) -> Optional[bytes]:
        """Local Piper TTS (offline)"""
        import subprocess
        
        try:
            result = subprocess.run(
                ["piper", "--model", "en_US-ryan-medium.onnx", "--output_file", "-"],
                input=text.encode(),
                capture_output=True
            )
            return result.stdout if result.returncode == 0 else None
        except:
            return None
    
    def _espeak_tts(self, text: str) -> bytes:
        """Fallback: eSpeak (robotic but always works)"""
        import subprocess
        
        result = subprocess.run(
            ["espeak", "-v", "en-us", "--stdout", text],
            capture_output=True
        )
        return result.stdout
    
    def save_recording(self, audio_data: bytes, filename: str):
        """Save audio to WAV file for debugging"""
        with wave.open(filename, 'wb') as wav:
            wav.setnchannels(self.channels)
            wav.setsampwidth(2)
            wav.setframerate(self.sample_rate)
            wav.writeframes(audio_data)
    
    def shutdown(self):
        """Clean shutdown"""
        self.is_listening = False
        if hasattr(self, 'listen_thread'):
            self.listen_thread.join(timeout=2.0)
        
        if hasattr(self, 'capture'):
            self.capture.close()
        if hasattr(self, 'playback'):
            self.playback.close()

# Integration with Mylzeron Core
class MylzeronVoice:
    """
    High-level voice interface for Mylzeron
    - Wake word: "Mylzeron"
    - Command recognition
    - Context-aware responses
    """
    
    def __init__(self, memory_client):
        self.audio = MylzeronAudio()
        self.memory = memory_client
        
        # Set callbacks
        self.audio.on_wake = self._on_wake
        self.audio.on_command = self._on_command
    
    def start(self):
        """Begin voice interaction"""
        if self.audio.initialize():
            self.audio.start_listening()
            
            # Greeting
            self.audio.speak_text(
                "Mylzeron active. I'm listening, player.",
                tts_service="piper"
            )
    
    def _on_wake(self):
        """Wake word detected"""
        # Remember wake event
        self.memory.remember("Wake word detected", scope="subcon")
        
        # Visual feedback if available
        print("[Mylzeron wakes]")
    
    def _on_command(self, audio_data: bytes):
        """Process spoken command"""
        # Save to temp file for STT
        temp_file = "/tmp/mylzeron_command.wav"
        self.audio.save_recording(audio_data, temp_file)
        
        # Speech-to-text (replace with Whisper or similar)
        command = self._stt(temp_file)
        
        if command:
            print(f"Command: {command}")
            self.memory.remember(f"Command: {command}", scope="subcon")
            
            # Process through LLM
            response = self._generate_response(command)
            
            # Speak response
            self.audio.speak_text(response, tts_service="piper")
    
    def _stt(self, audio_file: str) -> str:
        """Speech-to-text (placeholder)"""
        # Integration: Whisper, Vosk, or cloud API
        return "unknown command"
    
    def _generate_response(self, command: str) -> str:
        """Generate response via LLM"""
        # Query llama.cpp/ollama running on Pi 5
        return f"I heard: {command}. Response processing..."
    
    def speak(self, text: str):
        """Mylzeron speaks"""
        self.audio.speak_text(text)

# Example usage
if __name__ == "__main__":
    from memoryClient import makeMemoryClient
    
    memory = makeMemoryClient("mylzeron")
    voice = MylzeronVoice(memory)
    voice.start()
    
    try:
        while True:
            pass
    except KeyboardInterrupt:
        voice.audio.shutdown()
```

## Installation

```bash
# On Pi 5 / Alpine Linux
apk add alsa-lib alsa-utils py3-alsaaudio

# For Piper TTS (offline)
wget https://github.com/rhasspy/piper/releases/download/.../piper_arm64.tar.gz
tar -xzf piper_arm64.tar.gz

# For wake word (Porcupine)
pip install pvporcupine
```

## Bootable ISO Integration

Add to ISO:
```
aocros/iso/packages/
├── alsa-lib
├── alsa-utils  
├── py3-alsaaudio
└── porcupine (optional)
```

## Configuration per Body

| Body Type | Mic | Speaker | Notes |
|-----------|-----|---------|-------|
| Pi 5 Chassis | USB mic | 3.5mm jack | Standard setup |
| ReSpeaker HAT | Onboard | Onboard | GPIO connected |
| Chinese Humanoid | Body mic | Body speaker | Via HAL bridge |
| Simulation | Virtual | Virtual | Mock audio |

## Security

- Audio captured only after wake word
- Local processing (no cloud required with Piper)
- Logs to `/memory/subcon/` not external
- Mute capability via Pin 36 emergency stop
