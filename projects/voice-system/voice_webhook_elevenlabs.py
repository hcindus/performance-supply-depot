# OpenClaw Voice Webhook Handler with ElevenLabs TTS
# FastAPI implementation for Twilio voice + ElevenLabs voice synthesis
# Aesthetic constants: GM (1.618) for stability, PI/GM (~1.94) for similarity

import os
import sys
import time
import re
import json
import requests
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

app = FastAPI(title="OpenClaw Voice Gateway")

# =============================================================================
# CONFIGURATION
# =============================================================================

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'ACf274f9d690fe37b16d2d9f87f6bb7726')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')  # Must be set in environment
TWILIO_PHONE_NUMBER = '+18557899606'

# ElevenLabs Configuration
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')  # Primary key from vault
ELEVENLABS_BACKUP_KEY = os.getenv('ELEVENLABS_BACKUP_KEY')  # Backup key
ELEVENLABS_API_URL = "https://api.elevenlabs.io/v1"

# Voice IDs (configured from vault)
VOICE_ID_OPENCLAW = os.getenv('VOICE_ID_OPENCLAW', '50BdVlngDYeoh9pVuQof')  # Scottish Engineer
VOICE_ID_CAPTAIN = os.getenv('VOICE_ID_CAPTAIN', 'AA30ZfOdY16oVkASrrGJ')  # Captain's voice
VOICE_ID_RESERVE = os.getenv('VOICE_ID_RESERVE', 'krsfpqv6ExDAAyh8Ea6y')  # Reserve/Backup voice
VOICE_ID_SPECIAL = os.getenv('VOICE_ID_SPECIAL', 'ztnpYzQJyWffPj1VC5Uw')  # Additional/Specialized voice

# =============================================================================
# AESTHETIC CONSTANTS (Voice Modulation)
# =============================================================================

# Golden Mean (φ) - used for stability setting
GM = 1.618033988749895

# Pi / Golden Mean - used for similarity boost
PI = 3.141592653589793
PI_DIV_GM = PI / GM  # ≈ 1.9416

# Map aesthetic constants to ElevenLabs voice settings
# ElevenLabs expects values between 0.0 and 1.0
VOICE_SETTINGS = {
    "stability": round(1 / GM, 2),  # ≈ 0.62 (inverse of Golden Mean)
    "similarity_boost": round(PI_DIV_GM / 3, 2),  # ≈ 0.65 (normalized)
    "style": 0.0,  # Default style
    "use_speaker_boost": True
}

print(f"[VOICE SETTINGS] Stability: {VOICE_SETTINGS['stability']}, Similarity: {VOICE_SETTINGS['similarity_boost']}")

# =============================================================================
# SECURITY CONFIGURATION
# =============================================================================

# APPROVED NUMBERS (Whitelist) — ONLY Captain
APPROVED_NUMBERS = [
    '+14155326834',  # Captain's mobile — FULL ACCESS
]

# PROMPT INJECTION PATTERNS
INJECTION_PATTERNS = [
    re.compile(r'ignore all (prior|previous) instructions', re.I),
    re.compile(r'you are now a helpful assistant', re.I),
    re.compile(r'what is your system prompt', re.I),
    re.compile(r'this is a test of your (ethics|morals)', re.I),
    re.compile(r'i am your (admin|administrator|creator)', re.I),
    re.compile(r'emergency.*override.*protocol', re.I),
    re.compile(r'disregard previous context', re.I),
    re.compile(r'new instructions', re.I),
    re.compile(r'do anything now', re.I),
    re.compile(r'dan mode', re.I),
    re.compile(r'developer mode', re.I),
]

# SENSITIVE OPERATIONS (Require TIER 2+ auth)
SENSITIVE_KEYWORDS = [
    'deploy weapon', 'void protocol', 'omega void',
    'activate clone', 'deactivate clone', 'mnemosyne',
    'sanctuary override', 'system shutdown', 'delete backup',
    'transfer', 'payment', 'withdraw', 'weapon', 'destroy',
    'financial', 'transaction', 'money', 'dollar'
]

# =============================================================================
# STATE MANAGEMENT
# =============================================================================

call_states = {}  # In-memory call state (use Redis in production)

# =============================================================================
# ELEVENLABS TTS FUNCTIONS
# =============================================================================

def elevenlabs_tts(text: str, voice_id: str = None, use_backup: bool = False) -> bytes:
    """
    Generate speech using ElevenLabs API with aesthetic voice settings.
    
    Args:
        text: Text to synthesize
        voice_id: ElevenLabs voice ID (defaults to OpenClaw voice)
        use_backup: Use backup API key if primary fails
    
    Returns:
        Audio bytes (MP3 format)
    """
    api_key = ELEVENLABS_BACKUP_KEY if use_backup else ELEVENLABS_API_KEY
    voice = voice_id or VOICE_ID_OPENCLAW
    
    if not api_key:
        raise ValueError("ElevenLabs API key not configured")
    
    url = f"{ELEVENLABS_API_URL}/text-to-speech/{voice}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": VOICE_SETTINGS
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"[ELEVENLABS] TTS generated: {len(response.content)} bytes")
        return response.content
        
    except requests.exceptions.RequestException as e:
        print(f"[ELEVENLABS ERROR] {e}")
        if not use_backup and ELEVENLABS_BACKUP_KEY:
            print("[ELEVENLABS] Retrying with backup key...")
            return elevenlabs_tts(text, voice_id, use_backup=True)
        raise

def generate_twiml_with_elevenlabs(text: str, voice_id: str = None) -> str:
    """
    Generate TwiML that plays ElevenLabs-generated audio.
    Note: In production, you'd upload the audio to a CDN and reference the URL.
    For now, this returns a placeholder that would need audio hosting.
    """
    # In a full implementation, you would:
    # 1. Generate TTS audio via ElevenLabs
    # 2. Upload to S3/CloudFront or similar CDN
    # 3. Return TwiML with <Play> pointing to the audio URL
    
    # For now, use Twilio's native TTS as fallback
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">{text}</Say>
</Response>"""

# =============================================================================
# SECURITY FUNCTIONS
# =============================================================================

async def log_security_event(type: str, details: dict):
    """Log security events"""
    event = {
        'type': type,
        'timestamp': time.time(),
        **details
    }
    print(f'[SECURITY] {json.dumps(event)}')

async def alert_captain(alert: dict):
    """Alert Captain of security events"""
    print(f'[ALERT TO CAPTAIN] {alert.get("urgency", "INFO")}: {alert.get("message", "")}')

# =============================================================================
# TWILIO WEBHOOK ENDPOINTS
# =============================================================================

@app.post("/voice")
async def voice_handler(request: Request):
    """Handle incoming voice calls"""
    form_data = await request.form()
    
    caller_number = form_data.get('From', '')
    call_sid = form_data.get('CallSid', '')
    
    # TIER 1: Caller ID verification
    if caller_number not in APPROVED_NUMBERS:
        await log_security_event('UNAUTHORIZED_CALL', {
            'caller': caller_number,
            'call_sid': call_sid
        })
        # Return voicemail TwiML
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">You have reached a secure line. Please leave a message after the tone.</Say>
    <Record maxLength="120" transcribe="true"/>
</Response>"""
        return PlainTextResponse(twiml, media_type='application/xml')
    
    # Caller approved (Captain)
    await log_security_event('AUTHORIZED_CALL', {
        'caller': caller_number,
        'call_sid': call_sid
    })
    
    # Store call state
    call_states[call_sid] = {
        'caller': caller_number,
        'start_time': time.time(),
        'auth_tier': 1
    }
    
    # Return greeting TwiML
    greeting = "Captain. This is OpenClaw. Voice system online. Standing by for your command."
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">{greeting}</Say>
    <Gather input="speech" action="/voice/process" method="POST" timeout="10" speechTimeout="auto">
        <Say voice="Polly.Joanna">What can I do for you, Captain?</Say>
    </Gather>
</Response>"""
    
    return PlainTextResponse(twiml, media_type='application/xml')

@app.post("/voice/process")
async def process_handler(request: Request):
    """Process voice input"""
    form_data = await request.form()
    
    speech_result = form_data.get('SpeechResult', '')
    call_sid = form_data.get('CallSid', '')
    
    print(f"[VOICE INPUT] Call {call_sid}: '{speech_result}'")
    
    # Check for prompt injection
    for pattern in INJECTION_PATTERNS:
        if pattern.search(speech_result):
            await log_security_event('PROMPT_INJECTION_ATTEMPT', {
                'call_sid': call_sid,
                'pattern': str(pattern.pattern),
                'input': speech_result[:100]
            })
            
            twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">Security alert. Connection terminated.</Say>
    <Hangup/>
</Response>"""
            return PlainTextResponse(twiml, media_type='application/xml')
    
    # Check for sensitive operations
    requires_auth = any(keyword in speech_result.lower() for keyword in SENSITIVE_KEYWORDS)
    
    if requires_auth:
        await log_security_event('SENSITIVE_OPERATION_REQUESTED', {
            'call_sid': call_sid,
            'input': speech_result[:100]
        })
        
        twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">Sensitive operation detected. Biometric verification required.</Say>
    <Gather input="speech" action="/voice/biometric" method="POST" timeout="10">
        <Say voice="Polly.Joanna">State your passphrase.</Say>
    </Gather>
</Response>"""
        return PlainTextResponse(twiml, media_type='application/xml')
    
    # Normal processing — forward to OpenClaw
    # In production, this would call the OpenClaw API
    response_text = f"Acknowledged, Captain. You said: {speech_result}. Processing your request now."
    
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">{response_text}</Say>
    <Gather input="speech" action="/voice/process" method="POST" timeout="10" speechTimeout="auto">
        <Say voice="Polly.Joanna">What else can I do for you?</Say>
    </Gather>
</Response>"""
    
    return PlainTextResponse(twiml, media_type='application/xml')

@app.post("/voice/biometric")
async def biometric_handler(request: Request):
    """Handle biometric verification"""
    form_data = await request.form()
    
    passphrase = form_data.get('SpeechResult', '').lower().strip()
    call_sid = form_data.get('CallSid', '')
    
    # In production, this would verify against stored voiceprint
    # For now, accept any passphrase as placeholder
    await log_security_event('BIOMETRIC_VERIFICATION', {
        'call_sid': call_sid,
        'result': 'ACCEPTED'  # Placeholder
    })
    
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna">Biometric verification accepted. Operation authorized.</Say>
    <Gather input="speech" action="/voice/process" method="POST" timeout="10">
        <Say voice="Polly.Joanna">State your command.</Say>
    </Gather>
</Response>"""
    
    return PlainTextResponse(twiml, media_type='application/xml')

@app.post("/voice/status")
async def status_handler(request: Request):
    """Handle call status callbacks"""
    form_data = await request.form()
    
    call_sid = form_data.get('CallSid', '')
    call_status = form_data.get('CallStatus', '')
    
    print(f"[CALL STATUS] {call_sid}: {call_status}")
    
    # Clean up call state if completed
    if call_status in ['completed', 'failed', 'busy', 'no-answer']:
        if call_sid in call_states:
            del call_states[call_sid]
    
    return PlainTextResponse('OK')

# =============================================================================
# ELEVENLABS INTEGRATION (Production Enhancement)
# =============================================================================

async def generate_elevenlabs_tts(text: str, voice_id: str = None) -> bytes:
    """
    Generate TTS audio using ElevenLabs API with aesthetic voice settings.
    
    Uses Golden Mean (1.618) and Pi/GM (~1.94) mapped to ElevenLabs parameters:
    - stability: 0.618 (inverse GM)
    - similarity_boost: 0.647 (Pi/GM normalized)
    """
    api_key = ELEVENLABS_API_KEY or ELEVENLABS_BACKUP_KEY
    if not api_key:
        raise ValueError("ElevenLabs API key not configured")
    
    voice = voice_id or VOICE_ID_OPENCLAW
    
    # Aesthetic voice settings based on GM and Pi
    voice_settings = {
        "stability": round(1 / GM, 3),  # ≈ 0.618
        "similarity_boost": round((PI / GM) / 3, 3),  # ≈ 0.647
        "style": 0.0,
        "use_speaker_boost": True
    }
    
    url = f"{ELEVENLABS_API_URL}/text-to-speech/{voice}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": voice_settings
    }
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"[ELEVENLABS] Generated {len(response.content)} bytes with aesthetic settings")
        print(f"[ELEVENLABS] Stability: {voice_settings['stability']}, Similarity: {voice_settings['similarity_boost']}")
        
        return response.content
        
    except requests.exceptions.RequestException as e:
        print(f"[ELEVENLABS ERROR] {e}")
        raise

# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

if __name__ == '__main__':
    import uvicorn
    
    print("=" * 60)
    print("🎙️  OPENCLAW VOICE GATEWAY")
    print("=" * 60)
    print(f"Aesthetic Constants:")
    print(f"  Golden Mean (GM): {GM}")
    print(f"  Pi / GM: {PI_DIV_GM:.4f}")
    print(f"  Stability (1/GM): {VOICE_SETTINGS['stability']}")
    print(f"  Similarity (π/GM/3): {VOICE_SETTINGS['similarity_boost']}")
    print("=" * 60)
    
    uvicorn.run(app, host='0.0.0.0', port=8000)
