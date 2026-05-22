"""In-game bot move selection + round judging.

Easyandmedium difficulties .
Hard uses a StrategicBot powered by dataset-derived constants
from Brockbank & Vul (2021).
"""
from __future__ import annotations

import random

from game.constants import MOVES, BEATS
from bot.bot import StrategicBot

# One persistent bot instance so history accumulates across rounds.
_strategic_bot = StrategicBot()


def pick_bot_move(difficulty: str, history: list[dict]) -> str:
    if difficulty == "easy":
        return random.choice(MOVES)

    if difficulty == "medium" and len(history) >= 1:
        if random.random() < 0.6:
            return BEATS[history[-1]["player"]]
        return random.choice(MOVES)

    if difficulty == "hard":
        return _strategic_bot.counter_move()

    return random.choice(MOVES)


def judge(player_move: str, bot_move: str) -> str:
    #Return win/lose/tie
    if player_move == bot_move:
        return "tie"
    if BEATS[player_move] == bot_move:
        return "lose"
    return "win"


def update_bot_history(player_move: str, outcome: str) -> None:
    _strategic_bot.record(player_move, outcome)


def reset_bot() -> None:
    global _strategic_bot
    _strategic_bot = StrategicBot()
