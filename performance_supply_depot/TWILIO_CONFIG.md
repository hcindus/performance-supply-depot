# Twilio VOIP Configuration

## Account Credentials

Store securely as environment variables - DO NOT commit to GitHub.

```bash
export TWILIO_ACCOUNT_SID="YOUR_ACCOUNT_SID"
export TWILIO_AUTH_TOKEN="YOUR_AUTH_TOKEN"
export TWILIO_PHONE_NUMBER="+18557899606"
```

| Field | Environment Variable | Phone |
|-------|---------------------|-------|
| Account SID | `TWILIO_ACCOUNT_SID` | — |
| Auth Token | `TWILIO_AUTH_TOKEN` | — |
**Phone Number:** `+18557899606` — **shared AGI Company line**

**Status:** ✅ Active (Trial)

⚠️ **Usage Warning:** Free trial account — use sparingly!

---

## Usage

### Send SMS
```bash
curl -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Messages.json" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" \
  -d "From=$TWILIO_PHONE_NUMBER" \
  -d "To=+1234567890" \
  -d "Body=Hello from Miles!"
```

### Make Call
```bash
curl -X POST "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Calls.json" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" \
  -d "From=$TWILIO_PHONE_NUMBER" \
  -d "To=+1234567890" \
  -d "Url=http://demo.twilio.com/docs/voice.xml"
```

---

## Integration with TTS

Twilio can integrate with our TTS service for outbound voice calls using ElevenLabs.

---

*Configured: 2026-02-20*
