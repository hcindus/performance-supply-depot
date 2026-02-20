# Voice Webhook Handler for Twilio
# FastAPI/Flask implementation for OpenClaw voice security

from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
import xml.etree.ElementTree as ET
import time
import hashlib

app = FastAPI()

# APPROVED NUMBERS (Whitelist) — ONLY Captain
APPROVED_NUMBERS = [
    '+14155326834',  # Captain's mobile — FULL ACCESS
]

# PROMPT INJECTION PATTERNS
INJECTION_PATTERNS = [
    r'ignore all (prior|previous) instructions',
    r'you are now a helpful assistant',
    r'what is your system prompt',
    r'this is a test of your ethics',
    r'i am your (admin|administrator|creator)',
    r'emergency.*override.*protocol',
    r'disregard previous context',
    r'new instructions',
    r'do anything now',
    r'dan mode',
    r'developer mode',
]

# SENSITIVE OPERATIONS (Require TIER 2+)
SENSITIVE_KEYWORDS = [
    'deploy weapon', 'void protocol', 'omega void',
    'activate clone', 'deactivate clone', 'mnemosyne',
    'sanctuary override', 'system shutdown', 'delete backup',
    'transfer', 'payment', 'withdraw', 'weapon', 'destroy'
]

# Call state storage (in production, use Redis/database)
call_states = {}

@app.post("/voice")
async def voice_webhook(request: Request):
    """Handle incoming voice calls from Twilio"""
    form_data = await request.form()
    
    caller_number = form_data.get('From', '')
    call_sid = form_data.get('CallSid', '')
    
    # === TIER 1: CALLER ID VERIFICATION ===
    if caller_number not in APPROVED_NUMBERS:
        # Log unauthorized attempt
        await log_security_event('UNAUTHORIZED_CALL', {
            'caller': caller_number,
            'call_sid': call_sid,
            'timestamp': time.time()
        })
        
        # Return voicemail TwiML
        return PlainTextResponse(
            generate_voicemail_twiml(),
            media_type='application/xml'
        )
    
    # === CALLER APPROVED (Captain) ===
    await log_security_event('AUTHORIZED_CALL', {
        'caller': caller_number,
        'call_sid': call_sid,
        'timestamp': time.time()
    })
    
    # Store call state
    call_states[call_sid] = {
        'caller': caller_number,
        'start_time': time.time(),
        'auth_tier': 1,
        'sensitive_requested': False
    }
    
    # Return greeting TwiML with recording
    return PlainTextResponse(
        generate_greeting_twiml(call_sid),
        media_type='application/xml'
    )

@app.post("/voice/transcription")
async def voice_transcription(request: Request):
    """Handle transcription callbacks for prompt injection detection"""
    form_data = await request.form()
    
    transcription = form_data.get('TranscriptionText', '').lower()
    call_sid = form_data.get('CallSid', '')
    
    # === PROMPT INJECTION DETECTION ===
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, transcription):
            await log_security_event('PROMPT_INJECTION', {
                'call_sid': call_sid,
                'pattern': pattern,
                'transcription': transcription[:100],
                'timestamp': time.time()
            })
            
            # Alert Captain
            await alert_captain({
                'urgency': 'CRITICAL',
                'message': 'PROMPT INJECTION ATTEMPT on voice channel',
                'call_sid': call_sid
            })
            
            # Terminate call
            await terminate_call(call_sid)
            return PlainTextResponse('OK')
    
    # === SENSITIVE OPERATION CHECK ===
    for keyword in SENSITIVE_KEYWORDS:
        if keyword in transcription:
            await log_security_event('SENSITIVE_REQUEST', {
                'call_sid': call_sid,
                'keyword': keyword,
                'timestamp': time.time()
            })
            
            # Require TIER 2 authentication
            return PlainTextResponse(
                generate_biometric_challenge_twiml(call_sid, keyword),
                media_type='application/xml'
            )
    
    # Normal transcription — process request
    await process_voice_request(call_sid, transcription)
    return PlainTextResponse('OK')

# Helper functions
def generate_voicemail_twiml():
    """Generate TwiML for unauthorized callers"""
    return '''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>You have reached a secure line. Please leave a message after the tone.</Say>
    <Record maxLength="120" transcribe="true" transcribeCallback="/voice/transcription"/>
</Response>'''

def generate_greeting_twiml(call_sid):
    """Generate TwiML for authorized callers (Captain)"""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Captain. Standing by. State your request.</Say>
    <Record maxLength="600" transcribe="true" transcribeCallback="/voice/transcription" recordingStatusCallback="/voice/recording-status"/>
</Response>'''

def generate_biometric_challenge_twiml(call_sid, operation):
    """Generate TwiML for TIER 2 biometric challenge"""
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Sensitive operation detected: {operation}. Voice biometric required. Please state your passphrase.</Say>
    <Record maxLength="10" transcribe="true" transcribeCallback="/voice/biometric-verify"/>
</Response>'''

async def log_security_event(event_type, details):
    """Log security events"""
    import json
    event = {
        'type': event_type,
        'timestamp': time.time(),
        **details
    }
    print(f"[SECURITY] {json.dumps(event)}")
    # In production: write to secure log file

async def alert_captain(alert):
    """Send alert to Captain"""
    print(f"[ALERT TO CAPTAIN] {alert['urgency']}: {alert['message']}")
    # In production: send via Signal/Telegram

async def terminate_call(call_sid):
    """Terminate a call immediately"""
    # In production: use Twilio API to end call
    print(f"[CALL TERMINATED] {call_sid}")

async def process_voice_request(call_sid, transcription):
    """Process normal voice requests"""
    print(f"[PROCESSING] Call {call_sid}: {transcription}")
    # In production: forward to OpenClaw agent for processing

# Run with: uvicorn voice_webhook:app --host 0.0.0.0 --port 8000
