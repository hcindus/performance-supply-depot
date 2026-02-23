#!/usr/bin/env python3
"""
AOCROS Voice Service - Multi-Voice TTS Integration
Supports 6 ElevenLabs voices (3 male, 3 female)
"""

import os
import requests
from typing import Optional

# =============================================================================
# VOICE CONFIGURATION - 6 Voices (3 Male, 3 Female)
# =============================================================================

VOICES = {
    # MALE VOICES (3) - Verified Free Tier
    "scottish": {
        "id": "pNInz6obpgDQGcFmaJgB",  # Adam (verified working)
        "name": "Scottish Engineer",
        "gender": "male",
        "persona": "Warm, technical, Scottish accent"
    },
    "captain": {
        "id": "pNInz6obpgDQGcFmaJgB",  # Adam
        "name": "Captain",
        "gender": "male",
        "persona": "Captain's voice (using Adam)"
    },
    "adam": {
        "id": "pNInz6obpgDQGcFmaJgB",
        "name": "Adam",
        "gender": "male",
        "persona": "Professional, deep, clear"
    },
    # FEMALE VOICES (3) - Verified Free Tier
    "bella": {
        "id": "hpp4J3VqNfWAUOO0d1Us",
        "name": "Bella",
        "gender": "female",
        "persona": "Professional, bright, warm"
    },
    "sarah": {
        "id": "EXAVITQu4vr4xnSDxMaL",
        "name": "Sarah",
        "gender": "female",
        "persona": "Mature, reassuring, confident"
    },
    "jessica": {
        "id": "cgSgspJ2msm6clMCkdW9",
        "name": "Jessica",
        "gender": "female",
        "persona": "Playful, bright, warm"
    }
}

# Default voice
DEFAULT_VOICE = "scottish"

# Current active voice
_current_voice = DEFAULT_VOICE


# =============================================================================
# CORE FUNCTIONS
# =============================================================================

def set_voice(voice_key: str) -> bool:
    """Set the active voice for TTS."""
    global _current_voice
    
    if voice_key.lower() in VOICES:
        _current_voice = voice_key.lower()
        return True
    return False


def get_voice() -> str:
    """Get the current active voice key."""
    return _current_voice


def get_voice_info(voice_key: str = None) -> dict:
    """Get information about a voice."""
    key = voice_key.lower() if voice_key else _current_voice
    return VOICES.get(key, VOICES[DEFAULT_VOICE])


def list_voices() -> list:
    """List all available voices."""
    return [
        {
            "key": key,
            "name": v["name"],
            "gender": v["gender"],
            "persona": v["persona"]
        }
        for key, v in VOICES.items()
    ]


def speak(text: str, voice_key: str = None) -> bool:
    """Convert text to speech using ElevenLabs API."""
    key = voice_key.lower() if voice_key else _current_voice
    voice_config = VOICES.get(key, VOICES[DEFAULT_VOICE])
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print(f"[VOICE] No API key configured. Would speak: {text}")
        return False
    
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_config['id']}"
    
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            # Save to file for playback
            output_file = "/tmp/aocros_voice.mp3"
            with open(output_file, "wb") as f:
                f.write(response.content)
            print(f"[VOICE] Saved to {output_file}")
            return True
        else:
            print(f"[VOICE] Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"[VOICE] Exception: {e}")
        return False


# =============================================================================
# CLI INTERFACE
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AOCROS Voice Service")
    parser.add_argument("command", choices=["list", "speak", "set"], help="Command to run")
    parser.add_argument("--voice", "-v", help="Voice key (scottish, adam, rachel, etc.)")
    parser.add_argument("--text", "-t", help="Text to speak")
    
    args = parser.parse_args()
    
    if args.command == "list":
        print("\n=== Available Voices ===")
        for v in list_voices():
            print(f"  {v['key']:12} | {v['name']:20} | {v['gender']:6} | {v['persona']}")
        print()
    
    elif args.command == "set":
        if args.voice and set_voice(args.voice):
            print(f"Voice set to: {get_voice_info()['name']}")
        else:
            print("Invalid voice. Use 'list' to see available voices.")
    
    elif args.command == "speak":
        if args.text:
            voice = args.voice or get_voice()
            print(f"Speaking with {get_voice_info(voice)['name']}...")
            speak(args.text, voice)
        else:
            print("Please provide --text or -t argument")
