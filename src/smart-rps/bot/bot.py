"""Strategic RPS bot powered by dataset-derived constants.

Constants are from Brockbank & Vul (2021) v2 — 69,365 rounds across
265 players, online human-vs-bot games — supplemented with Uppsala
tournament data (3,059 rounds, human-vs-human) for opening-move priors.

The bot predicts the player's next move using a Markov transition matrix
and Win-Stay/Lose-Shift rates, then counters it. No runtime training —
all constants are pre-computed offline.
"""
from __future__ import annotations

import random
from collections import defaultdict

from game.constants import MOVES, BEATS

# Dataset-derived constants (Brockbank v2)

MOVE_FREQUENCY: dict[str, float] = {"R": 0.309, "P": 0.332, "S": 0.359}

WSLS_RATES: dict[str, float] = {
    "win_stay": 0.147,    # i.e. Win-Shift is 85.3%
    "lose_shift": 0.731,
}

# P(next | last) — row = last move, col = next move
MARKOV_MATRIX: dict[str, dict[str, float]] = {
    "R": {"R": 0.213, "P": 0.431, "S": 0.356},
    "P": {"R": 0.351, "P": 0.186, "S": 0.463},
    "S": {"R": 0.352, "P": 0.382, "S": 0.266},
}

OPENING_MOVE: str = "R"  # counters Scissors (35.9%)


class StrategicBot:
    """Bot that predicts player moves using dataset-derived stats."""

    def __init__(self) -> None:
        self.history: list[dict] = []  # {"player": str, "outcome": str}

    def record(self, player_move: str, outcome: str) -> None:
        self.history.append({"player": player_move, "outcome": outcome})

    def predict(self) -> str:
        """Return the predicted player move for the upcoming round."""
        n = len(self.history)

        # First move: use dataset opening prior
        if n == 0:
            return OPENING_MOVE

        # Win-Stay / Lose-Shift
        if n >= 1:
            last = self.history[-1]
            if last["outcome"] == "win":
                if random.random() < WSLS_RATES["win_stay"]:
                    return last["player"]  # stay
                else:
                    # Shift: pick the most frequent alternative per Markov
                    row = MARKOV_MATRIX.get(last["player"], MOVE_FREQUENCY)
                    others = {m: p for m, p in row.items() if m != last["player"]}
                    return max(others, key=others.get)
            elif last["outcome"] == "lose":
                if random.random() < WSLS_RATES["lose_shift"]:
                    # Shift to weighted random alternative
                    row = MARKOV_MATRIX.get(last["player"], MOVE_FREQUENCY)
                    others = {m: p for m, p in row.items() if m != last["player"]}
                    total = sum(others.values())
                    r = random.random() * total
                    for m, p in others.items():
                        r -= p
                        if r <= 0:
                            return m
                    return max(others, key=others.get)
                else:
                    return last["player"]  # stay

        # Markov trigram: P(next | last2)
        if n >= 2:
            last2 = (self.history[-2]["player"], self.history[-1]["player"])
            counts: dict[str, int] = defaultdict(int)
            for i in range(n - 1):
                key = (self.history[i]["player"], self.history[i + 1]["player"])
                if key == last2:
                    if i + 2 < n:
                        counts[self.history[i + 2]["player"]] += 1
            if counts:
                return max(counts, key=lambda k: counts[k])

        # Fallback: Markov first-order P(next | last)
        last_move = self.history[-1]["player"]
        row = MARKOV_MATRIX.get(last_move, MOVE_FREQUENCY)
        return max(row, key=row.get)

    def counter_move(self) -> str:
        """Predict the player's move and return the move that beats it."""
        predicted = self.predict()
        return BEATS[predicted]
