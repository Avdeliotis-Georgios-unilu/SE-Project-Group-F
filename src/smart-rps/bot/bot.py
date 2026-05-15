"""
RPS Static Bot

Decides what move the bot plays next based on the game history.
All constants are computed offline by analyze_rps.py, not at runtime.

Decision priority:
    Round 1          -> play Paper (exploits Rock bias)
    After a WIN      -> Win-Stay (predict player repeats)
    After a LOSS     -> Lose-Shift (predict player changes)
    After a TIE      -> Markov prediction from last move

Usage:
    from bot import RPSBot

    bot = RPSBot()
    bot_move = bot.next_move()
    bot.record_round(player_move="R", bot_move=bot_move)
"""

import random


# CONSTANTS — replace with output of analyze_rps.py
# Current values explained in RPS_BOT_Constants

MOVE_FREQUENCY = {"R": 0.354, "P": 0.330, "S": 0.316}

WSLS_RATES = {
    "win_stay":   0.60,
    "lose_shift": 0.80,
}

MARKOV_MATRIX = {
    "R": {"R": 0.40, "P": 0.32, "S": 0.28},
    "P": {"R": 0.30, "P": 0.38, "S": 0.32},
    "S": {"R": 0.31, "P": 0.33, "S": 0.36},
}

OPENING_MOVE = "P"


# GAME MECHANICS


MOVES = ("R", "P", "S")
BEATS = {"R": "P", "P": "S", "S": "R"}  # BEATS[x] = the move that beats x
NAMES = {"R": "Rock", "P": "Paper", "S": "Scissors"}


def outcome(player_move, bot_move):
    """Return 'win' / 'loss' / 'tie' from the player's perspective."""
    if player_move == bot_move:
        return "tie"
    if BEATS[player_move] == bot_move:
        return "loss"
    return "win"


# BOT


class RPSBot:
    """Stateless across games, stateful within a game."""

    def __init__(self, seed=None):
        self._rng = random.Random(seed)
        self.history = []

    def next_move(self):
        """Return the bot's move for this round."""
        predicted = self._predict_player_move()
        return BEATS[predicted]

    def record_round(self, player_move, bot_move):
        """Store the round result so the next prediction has context."""
        player_move = player_move.upper()
        bot_move = bot_move.upper()
        if player_move not in MOVES or bot_move not in MOVES:
            raise ValueError(f"Invalid move. Must be one of {MOVES}.")

        self.history.append({
            "player": player_move,
            "bot":    bot_move,
            "result": outcome(player_move, bot_move),
        })

    def reset(self):
        """Clear history between players at the expo."""
        self.history = []

    def _predict_player_move(self):
        """Predict what the player will play next (priority order)."""
        if not self.history:
            # Assume player opens with Rock -> bot plays Paper
            assumed = {v: k for k, v in BEATS.items()}[OPENING_MOVE]
            return assumed

        last = self.history[-1]
        last_player = last["player"]
        last_result = last["result"]

        if last_result == "win":
            if self._rng.random() < WSLS_RATES["win_stay"]:
                return last_player
            return self._markov_predict(last_player)

        if last_result == "loss":
            if self._rng.random() < WSLS_RATES["lose_shift"]:
                return self._markov_predict(last_player, exclude=last_player)
            return last_player

        # Tie -> Markov only
        return self._markov_predict(last_player)

    def _markov_predict(self, prev_move, exclude=None):
        """Most probable next move given prev_move. Optionally exclude one move."""
        row = MARKOV_MATRIX[prev_move]
        candidates = [m for m in MOVES if m != exclude]
        return max(candidates, key=lambda m: row[m])

    def stats(self):
        """W/L/T counts and win rates from the bot's perspective."""
        n = len(self.history)
        if n == 0:
            return {
                "rounds": 0, "bot_wins": 0, "player_wins": 0, "ties": 0,
                "bot_win_rate_absolute": 0.0,
                "bot_win_rate_relative": 0.0,
            }

        bot_wins    = sum(1 for r in self.history if r["result"] == "loss")
        player_wins = sum(1 for r in self.history if r["result"] == "win")
        ties        = sum(1 for r in self.history if r["result"] == "tie")
        decisive    = bot_wins + player_wins

        return {
            "rounds":                n,
            "bot_wins":              bot_wins,
            "player_wins":           player_wins,
            "ties":                  ties,
            "bot_win_rate_absolute": bot_wins / n,
            "bot_win_rate_relative": bot_wins / decisive if decisive > 0 else 0.0,
        }


# DEMO

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("RPS BOT — interactive demo")
    print("=" * 60)
    print("Type R, P, or S to play. Type 'q' to quit.\n")

    bot = RPSBot()
    round_num = 1

    while True:
        try:
            raw = input(f"Round {round_num} — your move (R/P/S/q): ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if raw == "Q":
            break
        if raw not in MOVES:
            print("  Invalid. Use R, P, S, or q.")
            continue

        bot_move = bot.next_move()
        bot.record_round(player_move=raw, bot_move=bot_move)
        last = bot.history[-1]

        result_str = {"win": "YOU WIN", "loss": "BOT WINS", "tie": "TIE"}[last["result"]]
        print(f"  You: {NAMES[raw]:8s} | Bot: {NAMES[bot_move]:8s} | -> {result_str}\n")
        round_num += 1

    s = bot.stats()
    print("\n" + "=" * 60)
    print("FINAL STATS")
    print("=" * 60)
    print(f"  Rounds played : {s['rounds']}")
    print(f"  Bot wins      : {s['bot_wins']}")
    print(f"  Player wins   : {s['player_wins']}")
    print(f"  Ties          : {s['ties']}")
    if s["rounds"] > 0:
        print(f"  Bot win rate (absolute): {s['bot_win_rate_absolute']*100:.1f}%")
    print(f"  Bot win rate (relative): {s['bot_win_rate_relative']*100:.1f}%")
    sys.exit(0)