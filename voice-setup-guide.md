# Voice Setup Options for OpenClaw Agent

Four ways to enable voice conversations with your agent.

---

## Option 1: Twilio (Recommended for Real Phone Number)

**What You Get:** A real phone number that rings to your agent.

### Prerequisites
- Twilio account (free trial works)
- A server/webhook endpoint (can use OpenClaw gateway or simple server)
- OpenClaw configured with webhooks

### Step-by-Step

**1. Register Twilio Account**
- Go to https://www.twilio.com/try-twilio
- Verify phone number
- Get Account SID and Auth Token

**2. Buy a Phone Number**
- In Twilio Console → Phone Numbers → Manage → Buy a number
- Choose local number (~$1/month)

**3. Set Up Webhook Endpoint**

Create a simple webhook server:

```python
# webhook_server.py
from flask import Flask, request
import requests

app = Flask(__name__)
OPENCLAW_WEBHOOK_URL = "https://your-openclaw-gateway.com/webhook"
TWILIO_ACCOUNT_SID = "your_account_sid"
TWILIO_AUTH_TOKEN = "your_auth_token"

@app.route("/voice", methods=['POST'])
def voice():
    # Get incoming call details
    from_number = request.form.get('From')
    call_sid = request.form.get('CallSid')
    
    # Forward to OpenClaw
    requests.post(OPENCLAW_WEBHOOK_URL, json={
        "type": "voice_call",
        "from": from_number,
        "call_sid": call_sid,
        "provider": "twilio"
    })
    
    # Return TwiML to gather speech
    return """<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Gather input="speech" action="/process_speech" method="POST">
            <Say>Hello, this is the agent. What can I help you with?</Say>
        </Gather>
    </Response>"""

@app.route("/process_speech", methods=['POST'])
def process_speech():
    speech_text = request.form.get('SpeechResult')
    from_number = request.form.get('From')
    
    # Send to OpenClaw for processing
    response = requests.post(OPENCLAW_WEBHOOK_URL, json={
        "type": "voice_message",
        "message": speech_text,
        "from": from_number,
        "provider": "twilio",
        "channel": "voice"
    })
    
    # Get agent response and convert to speech
    agent_reply = response.json().get('reply', 'I did not understand that.')
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Say>{agent_reply}</Say>
        <Gather input="speech" action="/process_speech" method="POST">
            <Say>What else can I help you with?</Say>
        </Gather>
    </Response>"""

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
```

**4. Configure Twilio Webhook**
- In Twilio Console → Phone Numbers → Manage → Active Numbers
- Click your number
- Set "A call comes in" webhook to: `http://your-server:5000/voice`
- Method: HTTP POST

**5. Configure OpenClaw**
Add to OpenClaw config:
```yaml
webhooks:
  - path: /voice
    handler: voice_webhook
    
voice:
  enabled: true
  provider: twilio
  tts_engine: elevenlabs  # or google, amazon
  voice_id: "male_voice_id"
```

**6. Install Dependencies**
```bash
pip install flask requests twilio
```

**7. Run Server**
```bash
python webhook_server.py
```

**8. Test**
- Call your Twilio number
- Speak when prompted
- Agent should respond via voice

### Costs
- Phone number: ~$1-2/month
- Per-minute calls: ~$0.0085/minute
- Total: ~$5-10/month for moderate use

---

## Option 2: Google Voice / VoIP Integration

**What You Get:** Use your existing Google Voice number or VoIP service.

### Prerequisites
- Google Voice account OR VoIP provider
- SIP trunk or forwarding capability
- OpenClaw with voice handler

### Method A: Google Voice (via forwarding)

**1. Set Up Google Voice**
- Google Voice → Settings → Calls
- Enable "Forward calls to linked numbers"
- Link a SIP/VoIP number that can receive webhooks

**2. Use a VoIP Bridge**
Register with a service like:
- **Sipgate** (sipgate.com) - free US number
- **Callcentric** (callcentric.com) - pay-as-you-go
- **Anveo** (anveo.com) - developer-friendly

**3. Configure VoIP for Webhooks**

Most VoIP providers support webhooks. Example for Sipgate:

```javascript
// sipgate_webhook.js
const express = require('express');
const app = express();

app.post('/incoming-call', (req, res) => {
    const callData = {
        from: req.body.from,
        to: req.body.to,
        callId: req.body.callId
    };
    
    // Forward to OpenClaw
    fetch('https://your-openclaw-gateway.com/webhook', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            type: 'voice_call',
            provider: 'google_voice',
            ...callData
        })
    });
    
    res.json({action: 'connect', destination: 'your-openclaw-handler'});
});

app.listen(3000);
```

**4. Configure OpenClaw**
Same as Twilio config above.

### Method B: Direct VoIP (SIP)

If you have a SIP trunk:

```python
# sip_handler.py
from opensips import MI  # Or use pjsip

def handle_sip_invite(from_uri, to_uri):
    # Incoming SIP call
    openclaw_response = requests.post(OPENCLAW_URL, json={
        'type': 'sip_call',
        'from': from_uri,
        'invite': True
    })
    
    # Convert response to audio stream
    audio_stream = tts_to_stream(openclaw_response.text)
    return audio_stream
```

---

## Option 3: Nodes (OpenClaw Paired Device)

**What You Get:** Voice directly through a paired phone/tablet with OpenClaw Relay.

### Prerequisites
- OpenClaw Node app installed on phone
- Paired with your OpenClaw session
- Browser Relay extension (for voice bridging)

### Step-by-Step

**1. Install OpenClaw Node App**
- Android: Download from Play Store (or APK)
- iOS: Available via TestFlight

**2. Pair Device**
```bash
# On OpenClaw agent side
openclaw nodes pair
# Shows QR code
```

**3. Scan QR Code**
- Open Node app → Add Node → Scan QR
- Or enter pairing code manually

**4. Enable Voice in Node Settings**
- Open Node app → Settings → Voice
- Enable "Relay voice calls to agent"
- Select voice: Male/Female

**5. Set Up Call Handling**
In OpenClaw config:
```yaml
nodes:
  voice:
    enabled: true
    auto_answer: false  # Or true for hands-free
    forward_to: main_agent
    
    # Voice synthesis
    tts:
      engine: system  # Uses device's TTS
      # OR
      engine: elevenlabs
      api_key: ${ELEVENLABS_API_KEY}
      voice_id: "male_voice"
```

**6. Use Voice Commands**
- Call the Node's virtual number
- Say: "Connect to [agent name]"
- Or use the Node app UI to start voice session

**Advantages:**
- No separate phone number needed
- Uses your existing phone
- Lower latency (direct to device)
- Can switch between text/voice

---

## Option 4: TTS + Messaging (Voice in Telegram/WhatsApp)

**What You Get:** Voice messages in your existing messaging apps.

### For Telegram

**1. Create Telegram Bot**
- Message @BotFather
- Send `/newbot`
- Name your bot
- Save the API token

**2. Configure OpenClaw Telegram Integration**
```yaml
integrations:
  telegram:
    enabled: true
    bot_token: ${TELEGRAM_BOT_TOKEN}
    voice:
      enabled: true
      auto_convert: true  # Auto-speak replies
```

**3. Enable Voice Replies**
```python
# When agent generates response
from gtts import gTTS
import tempfile

def send_voice_reply(chat_id, text):
    # Generate TTS
    tts = gTTS(text=text, lang='en', tld='com', slow=False)
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
        tts.save(f.name)
        voice_file = f.name
    
    # Send to Telegram
    bot.send_voice(chat_id, voice_file)
```

**4. Alternative: ElevenLabs (Better Quality)**
```python
import requests

def elevenlabs_tts(text, voice_id="male_voice"):
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + voice_id
    headers = {"xi-api-key": ELEVENLABS_API_KEY}
    data = {"text": text, "model_id": "eleven_monolingual_v1"}
    
    response = requests.post(url, json=data, headers=headers)
    return response.content  # Audio bytes

# Send voice message
bot.send_voice(chat_id, elevenlabs_tts(agent_reply))
```

**5. User Experience**
- User sends text or voice message
- Agent processes
- Agent replies with voice message (MP3/OGG)
- User hears response

### For WhatsApp

Requires WhatsApp Business API:

**1. Apply for WhatsApp Business API**
- Via Meta Business Partners (Twilio, 360dialog, etc.)
- Or direct via Meta (complex)

**2. Twilio WhatsApp (Easiest)**
```javascript
// In your webhook handler
app.post('/whatsapp', (req, res) => {
    const incoming = req.body.Body; // Text
    const from = req.body.From;     // WhatsApp number
    
    // Process with OpenClaw
    const agentReply = await processWithOpenClaw(incoming);
    
    // Generate voice with ElevenLabs
    const voiceAudio = await elevenlabsTTS(agentReply, "male_voice");
    
    // Send voice via Twilio WhatsApp
    twilioClient.messages.create({
        from: 'whatsapp:+YOUR_NUMBER',
        to: from,
        mediaUrl: voiceAudioUrl  // Must be publicly accessible URL
    });
});
```

**3. Alternative: WhatsApp Web + Python Bridge**
(yowsup or similar libraries — less stable, NOT recommended for production)

---

## Voice Comparison

| Feature | Twilio | Google Voice | Nodes | Telegram/WhatsApp |
|---------|--------|--------------|-------|-------------------|
| Real Phone Number | ✅ Yes | ✅ Yes | ❌ App-based | ❌ App-based |
| Incoming Calls | ✅ Yes | ✅ Yes | ✅ Via app | ❌ No |
| Voice Quality | ★★★ | ★★★ | ★★★ | ★★☆ |
| Cost | $5-10/mo | Free | Free | Free |
| Setup Complexity | Medium | Medium | Low | Low |
| Text Fallback | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Works Offline | ❌ No | ❌ No | ❌ No | ❌ No |

---

## Recommended Setup (Quick Start)

**For testing:** Option 4 (Telegram) — free, fast, works immediately

**For production:** Option 1 (Twilio) — professional, reliable, scalable

**For power user with OpenClaw already:** Option 3 (Nodes) — seamless integration, lowest latency

---

## Male Voice Options

ElevenLabs recommended male voices:
- "Adam" — Professional, warm (default)
- "Sam" — Young, energetic
- "Arnold" — Deep, authoritative
- "Patrick" — Smooth, sales-like
- Custom clone: Record samples to create your own

AWS Polly:
- "Matthew" — Newscaster style
- "Joey" — Natural conversational
- "Justin" — Younger male

Google Cloud TTS:
- "en-US-Neural2-A" — Strong male
- "en-US-Neural2-D" — Warm male

---

## Security Considerations

- Store API keys in environment variables, never in code
- Use HTTPS for all webhook endpoints
- Rate limit to prevent abuse
- Log calls for compliance (if applicable)
- Consider PII handling for voice recordings

---

Need help configuring any of these? Ask which option you're leaning toward and I can provide detailed troubleshooting.
