# config.py
# Central configuration file for the AI Language Learning Chatbot
# Edit this file to customize settings like API keys and supported languages

import os

# ─────────────────────────────────────────────
# GROQ API Configuration
# Get your free API key at: https://console.groq.com
# ─────────────────────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "your_groq_api_key_here")
GROQ_MODEL   = "llama-3.3-70b-versatile"   # Fast Llama 3 model via Groq

# ─────────────────────────────────────────────
# Supported Languages
# Key  = display name  |  Value = language code used by gTTS / prompts
# ─────────────────────────────────────────────
SUPPORTED_LANGUAGES = {
    "1": {"name": "English",    "code": "en"},
    "2": {"name": "Spanish",    "code": "es"},
    "3": {"name": "French",     "code": "fr"},
    "4": {"name": "German",     "code": "de"},
    "5": {"name": "Italian",    "code": "it"},
    "6": {"name": "Portuguese", "code": "pt"},
    "7": {"name": "Japanese",   "code": "ja"},
    "8": {"name": "Mandarin",   "code": "zh"},
    "9": {"name": "Tamil",       "code": "ta"},
}

# ─────────────────────────────────────────────
# Roleplay Scenarios
# ─────────────────────────────────────────────
ROLEPLAY_SCENARIOS = {
    "1": {
        "name":        "Job Interview",
        "description": "Practice answering common interview questions",
        "system_hint": "You are a professional interviewer. Ask job-interview questions one at a time.",
    },
    "2": {
        "name":        "Restaurant Ordering",
        "description": "Practice ordering food at a restaurant",
        "system_hint": "You are a friendly waiter at a restaurant. Take the customer's order naturally.",
    },
    "3": {
        "name":        "Meeting Someone New",
        "description": "Practice small talk and introductions",
        "system_hint": "You are someone meeting this person for the first time at a social event. Be warm and curious.",
    },
    "4": {
        "name":        "Shopping",
        "description": "Practice buying items at a store",
        "system_hint": "You are a helpful shop assistant. Help the customer find and purchase items.",
    },
}

# ─────────────────────────────────────────────
# Daily Challenges
# ─────────────────────────────────────────────
DAILY_CHALLENGES = [
    "Introduce yourself in 5 sentences — include your name, age, job, hobby, and a dream.",
    "Describe your morning routine using at least 6 different verbs.",
    "Talk about your favourite movie or book for 1 minute.",
    "Explain how to make your favourite food step by step.",
    "Describe the city or town you live in to someone who has never visited.",
    "Talk about a memorable experience from your childhood.",
    "Give three reasons why learning a new language is important.",
    "Describe your ideal holiday destination and what you would do there.",
    "Talk about a person who has inspired you and why.",
    "Explain what you would do if you won the lottery.",
]

# ─────────────────────────────────────────────
# Progress Tracker File
# ─────────────────────────────────────────────
PROGRESS_FILE = "progress_data.json"

# ─────────────────────────────────────────────
# Speech Recognition Settings
# ─────────────────────────────────────────────
MIC_TIMEOUT        = 5    # seconds to wait for speech to start
MIC_PHRASE_LIMIT   = 30   # maximum seconds per spoken phrase
