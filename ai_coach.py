# ai_coach.py
# All AI logic: chatting, grammar correction, scoring, and coaching advice.
# Communicates with the Groq API using the Llama 3 model.

import re
import json
from groq import Groq
from colorama import Fore, Style

from config import GROQ_API_KEY, GROQ_MODEL


# ─────────────────────────────────────────────────────────────
# Groq Client  (initialised once)
# ─────────────────────────────────────────────────────────────
try:
    _client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    print(Fore.RED + f"[Groq Init Error] {e}" + Style.RESET_ALL)
    _client = None


def _ask_groq(system_prompt: str, user_message: str, max_tokens: int = 600) -> str:
    """
    Send a single-turn request to the Groq / Llama 3 API.

    Args:
        system_prompt: Instructions that define the AI's behaviour.
        user_message:  The actual user text.
        max_tokens:    Maximum tokens in the response.

    Returns:
        The model's reply as a plain string.
    """
    if _client is None:
        return "⚠️ AI service is unavailable. Please check your GROQ_API_KEY."

    try:
        response = _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system",    "content": system_prompt},
                {"role": "user",      "content": user_message},
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ API error: {e}"



# ─────────────────────────────────────────────────────────────
# 0. Detect Language & Translate
# ─────────────────────────────────────────────────────────────
def detect_and_translate(text: str, native_lang: str, target_lang: str) -> dict:
    """
    Detect if user typed in native language or target language.
    Returns dict with is_native (bool).
    """
    prompt = (
        "You are a language detection expert. "
        "Detect what language the following text is written in. "
        "The two possible languages are: " + native_lang + " and " + target_lang + ". "
        "Reply with ONLY this JSON format, nothing else: "
        '{"language": "detected_language_name"}'
    )
    raw = _ask_groq(prompt, text, max_tokens=50)
    try:
        clean = raw.strip().replace("```json","").replace("```","").strip()
        result = json.loads(clean)
        detected = result.get("language", target_lang)
        return {"is_native": detected.strip().lower() == native_lang.strip().lower()}
    except Exception:
        return {"is_native": False}

def get_conversation_response(
    user_text: str,
    native_lang: str,
    target_lang: str,
    conversation_history: list,
) -> str:
    """
    Continue a language-learning conversation, keeping history for context.

    Args:
        user_text:            What the user just said.
        native_lang:          User's native language name (e.g. 'English').
        target_lang:          Language being learned (e.g. 'Spanish').
        conversation_history: List of {'role': ..., 'content': ...} dicts.

    Returns:
        The coach's reply.
    """
    system_prompt = (
        f"You are a friendly and encouraging AI language coach. "
        f"The student's native language is {native_lang} and they are learning {target_lang}.\n\n"
        f"IMPORTANT RULES:\n"
        f"1. If the user writes in {native_lang}, do ALL of the following in order:\n"
        f"   a) Show the {target_lang} translation clearly, labelled as: Translation: ...\n"
        f"   b) Break down each important word/phrase: Word Breakdown: word = meaning\n"
        f"   c) Give a simple example sentence in {target_lang} using those words\n"
        f"   d) Ask the user to try using one of those words in a new sentence\n"
        f"2. If the user writes in {target_lang}, check their sentence, praise what is correct, "
        f"gently fix any mistakes, and continue the conversation in {target_lang}.\n"
        f"3. Always be warm, encouraging, and patient.\n"
        f"4. Introduce one new vocabulary word per reply.\n"
        f"5. Keep responses clear and easy to understand for a beginner."
    )

    if _client is None:
        return "⚠️ AI service unavailable."

    # Build full message list including history
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(conversation_history[-6:])   # keep last 6 turns for context
    messages.append({"role": "user", "content": user_text})

    try:
        response = _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ API error: {e}"


# ─────────────────────────────────────────────────────────────
# 2. Grammar Correction
# ─────────────────────────────────────────────────────────────
def check_grammar(text: str, target_lang: str) -> dict:
    """
    Detect grammar mistakes and return correction details.

    Returns a dict with keys:
        has_error  (bool)
        corrected  (str)  – the corrected sentence
        explanation (str) – plain-English explanation of the mistake(s)
    """
    system_prompt = (
        f"You are an expert {target_lang} grammar teacher. "
        f"Analyse the given sentence for grammar mistakes. "
        f"Respond ONLY with valid JSON in this exact format:\n"
        f'{{"has_error": true/false, "corrected": "...", "explanation": "..."}}\n'
        f"No markdown, no extra text — pure JSON only."
    )

    raw = _ask_groq(system_prompt, text, max_tokens=300)

    # Attempt to parse JSON response
    try:
        # Strip any accidental markdown fences
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        return json.loads(clean)
    except json.JSONDecodeError:
        # Fallback if the model didn't return valid JSON
        return {
            "has_error":   False,
            "corrected":   text,
            "explanation": "Grammar check unavailable at the moment.",
        }


# ─────────────────────────────────────────────────────────────
# 3. Speaking Score Evaluation
# ─────────────────────────────────────────────────────────────
def evaluate_speaking(text: str, target_lang: str) -> dict:
    """
    Evaluate the user's spoken/typed text and return numeric scores.

    Returns a dict with:
        fluency        (int 1-10)
        grammar        (int 1-10)
        pronunciation  (int 1-10)  – estimated from text quality
        feedback       (str)       – short motivational tip
    """
    system_prompt = (
        f"You are a strict but encouraging {target_lang} language examiner. "
        f"Score the following text (1-10) for fluency, grammar, and estimated pronunciation. "
        f"Respond ONLY with valid JSON — no markdown:\n"
        f'{{"fluency": 7, "grammar": 8, "pronunciation": 7, "feedback": "Great effort! Work on..."}}' 
    )

    raw = _ask_groq(system_prompt, text, max_tokens=200)

    try:
        clean = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
        data  = json.loads(clean)
        # Clamp all scores to 1–10
        for key in ("fluency", "grammar", "pronunciation"):
            data[key] = max(1, min(10, int(data.get(key, 5))))
        return data
    except (json.JSONDecodeError, ValueError):
        return {
            "fluency":       6,
            "grammar":       6,
            "pronunciation": 6,
            "feedback":      "Keep practising — you're making great progress!",
        }


# ─────────────────────────────────────────────────────────────
# 4. Self-Improvement Coaching
# ─────────────────────────────────────────────────────────────
def get_coaching_tip(topic: str = "general") -> str:
    """
    Return a coaching tip on communication, confidence, or public speaking.

    Args:
        topic: 'confidence', 'public_speaking', 'daily_practice', or 'general'.
    """
    prompts = {
        "confidence":      "Give one practical tip for building speaking confidence in a new language. Be encouraging and specific.",
        "public_speaking": "Share one powerful public speaking tip suitable for language learners. Keep it actionable.",
        "daily_practice":  "Suggest a creative daily speaking practice exercise for language learners. Make it fun.",
        "general":         "Give one motivational piece of advice for someone learning a new language. Keep it warm and inspiring.",
    }
    system_prompt = "You are a world-class communication coach. Keep your advice to 2-3 sentences."
    user_prompt   = prompts.get(topic, prompts["general"])
    return _ask_groq(system_prompt, user_prompt, max_tokens=150)


# ─────────────────────────────────────────────────────────────
# 5. Roleplay Mode
# ─────────────────────────────────────────────────────────────
def get_roleplay_response(
    user_text: str,
    scenario: dict,
    target_lang: str,
    history: list,
) -> str:
    """
    Continue a roleplay conversation acting as the NPC character.

    Args:
        user_text: What the user just said.
        scenario:  Roleplay scenario dict from config.ROLEPLAY_SCENARIOS.
        target_lang: Language being practised.
        history:   Conversation history (list of role/content dicts).
    """
    system_prompt = (
        f"{scenario['system_hint']} "
        f"The user is practising {target_lang}. "
        f"Stay in character. Keep each response to 1-3 sentences. "
        f"If the user makes a clear language error, gently rephrase their sentence correctly "
        f"before continuing the roleplay (prefix your correction with '✏️ Correction:')."
    )

    if _client is None:
        return "⚠️ AI service unavailable."

    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history[-8:])
    messages.append({"role": "user", "content": user_text})

    try:
        response = _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            max_tokens=250,
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ API error: {e}"