# progress_tracker.py
# Tracks user progress across sessions: vocabulary learned, scores, sessions.
# Data is saved to a local JSON file so it persists between runs.

import json
import os
from datetime import date, datetime
from colorama import Fore, Style

from config import PROGRESS_FILE


# ─────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────
def _load() -> dict:
    """Load progress data from disk, returning an empty structure if not found."""
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass   # Corrupted file — start fresh

    return {
        "sessions":          [],   # list of session summary dicts
        "total_sessions":    0,
        "vocabulary_log":    {},   # date → word count learned that day
        "score_history":     [],   # list of {date, fluency, grammar, pronunciation}
        "challenges_done":   [],   # list of challenge strings completed
        "start_date":        str(date.today()),
    }


def _save(data: dict) -> None:
    """Write progress data to disk."""
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(Fore.RED + f"[Progress Save Error] {e}" + Style.RESET_ALL)


# ─────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────
def record_session(scores: dict | None = None, vocab_count: int = 0) -> None:
    """
    Record a completed practice session.

    Args:
        scores:      Dict with fluency/grammar/pronunciation keys (or None).
        vocab_count: How many new words were introduced this session.
    """
    data    = _load()
    today   = str(date.today())
    now     = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Increment session counter
    data["total_sessions"] += 1

    # Save session summary
    session_entry = {
        "timestamp": now,
        "vocab":     vocab_count,
    }
    if scores:
        session_entry.update(scores)
    data["sessions"].append(session_entry)

    # Update vocabulary log
    prev = data["vocabulary_log"].get(today, 0)
    data["vocabulary_log"][today] = prev + vocab_count

    # Update score history
    if scores:
        data["score_history"].append({"date": today, **scores})

    _save(data)


def record_challenge_done(challenge: str) -> None:
    """Mark a daily challenge as completed."""
    data = _load()
    if challenge not in data["challenges_done"]:
        data["challenges_done"].append(challenge)
    _save(data)


def get_progress_report() -> str:
    """
    Build and return a formatted progress report string.

    Returns:
        Multi-line string summarising the user's progress.
    """
    data  = _load()
    today = str(date.today())

    # ── Basic stats ──────────────────────────────────────────
    total_sessions  = data["total_sessions"]
    start           = data.get("start_date", today)
    days_active     = max(1, len(data["vocabulary_log"]))
    total_vocab     = sum(data["vocabulary_log"].values())
    challenges_done = len(data["challenges_done"])

    # ── Score averages ───────────────────────────────────────
    scores = data.get("score_history", [])
    if scores:
        avg_fluency = round(sum(s.get("fluency", 0)       for s in scores) / len(scores), 1)
        avg_grammar = round(sum(s.get("grammar", 0)       for s in scores) / len(scores), 1)
        avg_pronun  = round(sum(s.get("pronunciation", 0) for s in scores) / len(scores), 1)
        score_block = (
            f"  📊 Average Scores\n"
            f"     Fluency      : {avg_fluency}/10\n"
            f"     Grammar      : {avg_grammar}/10\n"
            f"     Pronunciation: {avg_pronun}/10\n"
        )
    else:
        score_block = "  📊 No scores recorded yet.\n"

    # ── Vocabulary per day (last 5 days) ─────────────────────
    vocab_log = data["vocabulary_log"]
    sorted_days = sorted(vocab_log.keys())[-5:]
    vocab_lines = "\n".join(
        f"     {d}: {vocab_log[d]} words" for d in sorted_days
    ) or "     No vocabulary data yet."

    # ── Build report ─────────────────────────────────────────
    report = (
        f"\n{'='*50}\n"
        f"          📈  PROGRESS REPORT\n"
        f"{'='*50}\n"
        f"  🗓️  Learning Since  : {start}\n"
        f"  🎯  Days Active     : {days_active}\n"
        f"  🏋️  Total Sessions  : {total_sessions}\n"
        f"  📚  Total Vocab     : {total_vocab} words\n"
        f"  🏆  Challenges Done : {challenges_done}\n\n"
        f"{score_block}\n"
        f"  📖 Vocabulary — Last 5 Days\n{vocab_lines}\n"
        f"{'='*50}\n"
    )
    return report
