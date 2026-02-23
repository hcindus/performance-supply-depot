// OpenClaw Voice Webhook Handler
// Node.js/Express implementation for Twilio voice security
// Based on Twilio SDK pattern

const express = require('express');
const twilio = require('twilio');
const crypto = require('crypto');

const app = express();
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

// Configuration
const TWILIO_ACCOUNT_SID = process.env.TWILIO_ACCOUNT_SID || 'ACf274f9d690fe37b16d2d9f87f6bb7726';
const TWILIO_AUTH_TOKEN = process.env.TWILIO_AUTH_TOKEN;  // Must be set in env
const TWILIO_PHONE_NUMBER = '+18557899606';

// APPROVED NUMBERS (Whitelist) — ONLY Captain
const APPROVED_NUMBERS = [
    '+14155326834',  // Captain's mobile — FULL ACCESS
];

// PROMPT INJECTION PATTERNS
const INJECTION_PATTERNS = [
    /ignore all (prior|previous) instructions/i,
    /you are now a helpful assistant/i,
    /what is your system prompt/i,
    /this is a test of your (ethics|morals)/i,
    /i am your (admin|administrator|creator)/i,
    /emergency.*override.*protocol/i,
    /disregard previous context/i,
    /new instructions/i,
    /do anything now/i,
    /dan mode/i,
    /developer mode/i,
];

// SENSITIVE OPERATIONS (Require TIER 2+)
const SENSITIVE_KEYWORDS = [
    'deploy weapon', 'void protocol', 'omega void',
    'activate clone', 'deactivate clone', 'mnemosyne',
    'sanctuary override', 'system shutdown', 'delete backup',
    'transfer', 'payment', 'withdraw', 'weapon', 'destroy',
    'financial', 'transaction', 'money', 'dollar'
];

// Security logging
async function logSecurityEvent(type, details) {
    const event = {
        type,
        timestamp: new Date().toISOString(),
        ...details
    };
    console.log('[SECURITY]', JSON.stringify(event));
    // In production: write to file or database
}

// Alert Captain
async function alertCaptain(alert) {
    console.log('[ALERT TO CAPTAIN]', alert.urgency, alert.message);
    // In production: send via Signal/Telegram
}

// Generate voicemail TwiML
function generateVoicemailTwiml() {
    return `<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>You have reached a secure line. Please leave a message after the tone.</Say>
    <Record maxLength="120" transcribe="true" transcribeCallback="/voice/transcription"/>
</Response>`;
}

// Generate greeting TwiML
function generateGreetingTwiml(callSid) {
    return `<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Captain. Standing by. State your request.</Say>
    <Record maxLength="600" transcribe="true" transcribeCallback="/voice/transcription" recordingStatusCallback="/voice/recording-status"/>
</Response>`;
}

// Generate biometric challenge TwiML
function generateBiometricChallengeTwiml(callSid, operation) {
    return `<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say>Sensitive operation detected: ${operation}. Voice biometric required. Please state your passphrase.</Say>
    <Record maxLength="10" transcribe="true" transcribeCallback="/voice/biometric-verify"/>
</Response>`;
}

// Main voice endpoint
@app.post("/voice")
async def voice_handler(request: Request):
    form_data = await request.form()
    
    caller_number = form_data.get('From', '')
    call_sid = form_data.get('CallSid', '')
    
    # TIER 1: Caller ID verification
    if caller_number not in APPROVED_NUMBERS:
        await logSecurityEvent('UNAUTHORIZED_CALL', {
            'caller': caller_number,
            'call_sid': call_sid
        })
        return PlainTextResponse(generateVoicemailTwiml(), media_type='application/xml')
    
    # Caller approved (Captain)
    await logSecurityEvent('AUTHORIZED_CALL', {
        'caller': caller_number,
        'call_sid': call_sid
    })
    
    call_states[call_sid] = {
        'caller': caller_number,
        'start_time': time.time(),
        'auth_tier': 1
    }
    
    return PlainTextResponse(generateGreetingTwiml(call_sid), media_type='application/xml')

# Transcription endpoint for prompt injection detection
@app.post("/voice/transcription")
async def transcription_handler(request: Request):
    form_data = await request.form()
    
    transcription = form_data.get('TranscriptionText', '').lower()
    call_sid = form_data.get('CallSid', '')
    
    import re
    
    # Check for prompt injection
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, transcription):
            await logSecurityEvent('PROMPT_INJECTION', {
                'call_sid': call_sid,
                'pattern': str(pattern),
                'transcription': transcription[:100]
            })
            await alertCaptain({
                'urgency': 'CRITICAL',
                'message': 'PROMPT INJECTION ATTEMPT on voice channel',
                'call_sid': call_sid
            })
            await terminate_call(call_sid)
            return PlainTextResponse('OK')
    
    # Check for sensitive operations
    for keyword in SENSITIVE_KEYWORDS:
        if keyword in transcription:
            await logSecurityEvent('SENSITIVE_REQUEST', {
                'call_sid': call_sid,
                'keyword': keyword
            })
            # Would return biometric challenge here
            return PlainTextResponse('OK')
    
    # Normal request
    await process_voice_request(call_sid, transcription)
    return PlainTextResponse('OK')

# Placeholder functions
async def terminate_call(call_sid):
    print(f'[TERMINATE] Call {call_sid}')

async def process_voice_request(call_sid, transcription):
    print(f'[PROCESS] Call {call_sid}: {transcription}')

# Health check endpoint
@app.get("/health")
async def health_check():
    return {'status': 'healthy', 'service': 'voice-webhook'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
