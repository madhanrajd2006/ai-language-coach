# daily_challenge.py
# Generates and manages the daily speaking challenge.
# Challenges rotate based on the day of the year so each day is different.

from datetime import date
from colorama import Fore, Style

from config import DAILY_CHALLENGES
from progress_tracker import record_challenge_done


def get_todays_challenge() -> str:
    """
    Return today's challenge string.
    Cycles through the challenge list using the day-of-year so it's consistent
    for an entire calendar day but changes every day.
    """
    day_index = date.today().timetuple().tm_yday   # 1–365
    challenge = DAILY_CHALLENGES[(day_index - 1) % len(DAILY_CHALLENGES)]
    return challenge


def display_challenge() -> str:
    """Print today's challenge with formatting and return its text."""
    challenge = get_todays_challenge()
    print(Fore.MAGENTA + "\n" + "="*50)
    print("       🌟  TODAY'S SPEAKING CHALLENGE")
    print("="*50)
    print(f"  {challenge}")
    print("="*50 + Style.RESET_ALL)
    return challenge


def mark_challenge_complete(challenge: str) -> None:
    """Mark a challenge as done and save it to progress tracker."""
    record_challenge_done(challenge)
    print(Fore.GREEN + "\n🎉 Challenge marked as complete! Great work!\n" + Style.RESET_ALL)
