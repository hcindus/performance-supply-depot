#!/usr/bin/env python3
"""
AOCROS Voice Selection Module
Import this in any agent to enable voice selection
"""

from playspace.aocros.services.voice.aocros_voice import (
    set_voice,
    get_voice,
    get_voice_info,
    list_voices,
    speak,
    VOICES
)

# =============================================================================
# QUICK SETUP - Add to your agent's __init__.py
# =============================================================================
"""
# At the top of your agent file:
from playspace.aocros.services.voice import voice

# In your __init__ or setup method:
voice.set_voice("scottish")  # Or any voice from the list

# To speak:
voice.speak("Hello, I am your AI assistant.")
"""

# =============================================================================
# VOICE QUICK REFERENCE - All Free Tier Verified
# =============================================================================
"""
VOICE_OPTIONS = {
    # Male (3) - All use Adam voice
    "scottish":   "pNInz6obpgDQGcFmaJgB",  # MILES default
    "captain":    "pNInz6obpgDQGcFmaJgB",
    "adam":       "pNInz6obpgDQGcFmaJgB",

    # Female (3) - All free tier
    "bella":      "hpp4J3VqNfWAUOO0d1Us",  # Professional, bright, warm
    "sarah":      "EXAVITQu4vr4xnSDxMaL",  # Mature, reassuring
    "jessica":    "cgSgspJ2msm6clMCkdW9",  # Playful, bright, warm
}

# Usage:
voice.set_voice("bella")   # Female option
voice.set_voice("adam")    # Male option
voice.list_voices()        # See all 6 options
"""
