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
# VOICE QUICK REFERENCE - All Free Tier
# =============================================================================
"""
VOICE_OPTIONS = {
    # Male (3) - All free tier
    "scottish":   "50BdVlngDYeoh9pVuQof",  # MILES default
    "captain":    "AA30ZfOdY16oVkASrrGJ",  # Captain's voice
    "adam":       "pNInz6obpgDQGcFmaJgB",  # Professional male

    # Female (3) - All free tier
    "reserve":    "krsfpqv6ExDAAyh8Ea6y",  # Backup female
    "special":    "ztnpYzQJyWffPj1VC5Uw",  # Special agent
    "rachel":     "CYw3kZ32KmQb2fqXOlX3",  # Warm female
}

# Usage:
voice.set_voice("rachel")  # Agent now speaks as Rachel
voice.speak("Hello!")      # Speaks with selected voice
voice.list_voices()        # See all 6 options
"""
