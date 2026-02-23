# Bridge Layer

Android sensory extension for Mylzeron Rzeros.

The Pi 5 is the brain; Android is the sensory body.

## Components

### camera/
- Stream to Mylzeron's "eyes"
- Object detection pipeline
- Facial recognition for user ID

### mic/
- Audio capture
- Wake word detection ("Mylzeron")
- Noise cancellation
- Speech-to-text bridge

### speaker/
- Text-to-speech (Adam voice)
- Audio playback
- Sound effects

### network/
- HTTP client to Pi 5
- WebSocket for real-time
- Fallback to REST polling

## Protocol

```
Android (senses) <---> Pi 5 (brain)
    |                    |
    +-- Camera --------->|
    +-- Mic ----------->|
    <--+ Speaker --------+
    <--+ Command --------+
```

## Security
- Local network only
- No cloud dependencies
- Owner signature on all commands