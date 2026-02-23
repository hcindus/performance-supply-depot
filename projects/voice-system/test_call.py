#!/usr/bin/env python3
# OpenClaw Voice Test Call
# Makes test call to Captain using Twilio

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from twilio.rest import Client

# Twilio credentials (from Q-LEVEL vault)
ACCOUNT_SID = "ACf274f9d690fe37b16d2d9f87f6bb7726"
AUTH_TOKEN = "105e1cff23033fcd3cba23bd013bda19"  # From vault
TWILIO_NUMBER = "+18557899606"
CAPTAIN_NUMBER = "+14155326834"

def make_test_call():
    """Make a test call to Captain"""
    print(f"📞 Initiating test call...")
    print(f"   From: {TWILIO_NUMBER}")
    print(f"   To: {CAPTAIN_NUMBER}")
    
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        
        # Create call with simple greeting
        call = client.calls.create(
            twiml='<Response><Say>Captain, this is OpenClaw. Voice system test successful. Standing by for your command.</Say></Response>',
            to=CAPTAIN_NUMBER,
            from_=TWILIO_NUMBER,
            status_callback='https://myl0nr0s.cloud/voice/status',
            status_callback_event=['initiated', 'ringing', 'answered', 'completed']
        )
        
        print(f"✅ Call initiated successfully!")
        print(f"   Call SID: {call.sid}")
        print(f"   Status: {call.status}")
        print(f"   Direction: {call.direction}")
        
        return call.sid
        
    except Exception as e:
        print(f"❌ Error making call: {e}")
        return None

def check_call_status(call_sid):
    """Check status of a call"""
    try:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        call = client.calls(call_sid).fetch()
        
        print(f"\n📊 Call Status Update:")
        print(f"   SID: {call.sid}")
        print(f"   Status: {call.status}")
        print(f"   Duration: {call.duration}s")
        print(f"   From: {call.from_formatted}")
        print(f"   To: {call.to_formatted}")
        
        return call.status
        
    except Exception as e:
        print(f"❌ Error checking call: {e}")
        return None

if __name__ == '__main__':
    print("=" * 60)
    print("🎙️  OPENCLAW VOICE TEST CALL")
    print("=" * 60)
    
    # Make test call
    call_sid = make_test_call()
    
    if call_sid:
        print("\n⏳ Waiting 10 seconds for call to connect...")
        import time
        time.sleep(10)
        
        # Check status
        check_call_status(call_sid)
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)
