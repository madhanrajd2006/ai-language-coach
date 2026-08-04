# app.py
# Flask web server for the AI Language Learning Chatbot
# Run with: python app.py  ->  open http://localhost:5000 in Chrome

import os
from flask import Flask, render_template, request, jsonify, session

from ai_coach import (
    get_conversation_response,
    check_grammar,
    evaluate_speaking,
    get_coaching_tip,
    get_roleplay_response,
    detect_and_translate,
)
from config import SUPPORTED_LANGUAGES, ROLEPLAY_SCENARIOS
from progress_tracker import record_session
from daily_challenge import get_todays_challenge, record_challenge_done

app = Flask(__name__)
app.secret_key = "langchatbot_secret_2024"


# Home page
@app.route("/")
def index():
    session.clear()
    return render_template("index.html")


# Config data endpoint - JS fetches this to build dropdowns
@app.route("/config_data")
def config_data():
    return jsonify({
        "languages": SUPPORTED_LANGUAGES,
        "scenarios": ROLEPLAY_SCENARIOS,
    })


# Save language selection
@app.route("/set_language", methods=["POST"])
def set_language():
    data = request.json
    session["native_lang"] = data.get("native_lang", "English")
    session["target_lang"] = data.get("target_lang", "English")
    session["target_code"] = data.get("target_code", "en")
    session["history"]     = []
    return jsonify({"status": "ok"})


# Main chat endpoint
@app.route("/chat", methods=["POST"])
def chat():
    data        = request.json
    user_text   = data.get("message", "").strip()
    mode        = data.get("mode", "conversation")
    scenario_id = data.get("scenario_id", "1")

    native_lang = session.get("native_lang", "English")
    target_lang = session.get("target_lang", "English")
    history     = session.get("history", [])

    if not user_text:
        return jsonify({"error": "Empty message"}), 400

    response_data = {}

    if mode == "conversation":
        # Detect if user typed in native language (e.g. Tamil) or target language (e.g. English)
        detection = detect_and_translate(user_text, native_lang, target_lang)
        is_native = detection.get("is_native", False)

        if is_native:
            # User typed in their native language — give full translation lesson
            reply  = get_conversation_response(user_text, native_lang, target_lang, history)
            # No grammar check needed when user types in native language
            grammar = {"has_error": False, "corrected": user_text, "explanation": ""}
            scores  = None
            response_data = {
                "reply":   reply,
                "grammar": None,   # skip grammar card for native language input
                "scores":  None,
                "is_native": True,
            }
        else:
            # User typed in target language — check grammar and converse normally
            grammar = check_grammar(user_text, target_lang)
            reply   = get_conversation_response(user_text, native_lang, target_lang, history)
            scores  = None
            if len([m for m in history if m["role"] == "user"]) % 3 == 0:
                scores = evaluate_speaking(user_text, target_lang)
                record_session(scores=scores, vocab_count=1)
            response_data = {
                "reply":   reply,
                "grammar": grammar,
                "scores":  scores,
                "is_native": False,
            }

        history.append({"role": "user",      "content": user_text})
        history.append({"role": "assistant", "content": reply})
        session["history"] = history[-12:]

    elif mode == "grammar":
        grammar = check_grammar(user_text, target_lang)
        response_data = {"grammar": grammar}

    elif mode == "roleplay":
        scenario = ROLEPLAY_SCENARIOS.get(scenario_id, ROLEPLAY_SCENARIOS["1"])
        grammar  = check_grammar(user_text, target_lang)
        reply    = get_roleplay_response(user_text, scenario, target_lang, history)
        history.append({"role": "user",      "content": user_text})
        history.append({"role": "assistant", "content": reply})
        session["history"] = history[-12:]
        response_data = {"reply": reply, "grammar": grammar, "scores": None}

    elif mode == "score":
        scores = evaluate_speaking(user_text, target_lang)
        record_session(scores=scores, vocab_count=0)
        response_data = {"scores": scores}

    elif mode == "coaching":
        topic = data.get("topic", "general")
        tip   = get_coaching_tip(topic)
        response_data = {"reply": tip}

    elif mode == "challenge":
        challenge = get_todays_challenge()
        scores    = evaluate_speaking(user_text, target_lang)
        record_challenge_done(challenge)
        record_session(scores=scores, vocab_count=1)
        response_data = {"scores": scores, "challenge": challenge}

    return jsonify(response_data)


@app.route("/progress")
def progress():
    from progress_tracker import _load
    return jsonify(_load())


@app.route("/daily_challenge")
def daily_challenge():
    return jsonify({"challenge": get_todays_challenge()})


if __name__ == "__main__":
    print("\n Language Chatbot running at: http://localhost:5000")
    print("   Open this URL in Chrome to start.\n")
    app.run(debug=True, port=5000)
