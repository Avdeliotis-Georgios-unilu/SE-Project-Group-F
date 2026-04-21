"""
RPS Static Bot
==============
Author: Gabriel (Group F)
Role  : Data analysis + bot strategy

Purpose
-------
Decide what move the bot should play next, given the history of a game
against a single human player at the expo.

Architecture (Option B — fully static)
--------------------------------------
No runtime training. All behavioral constants are computed OFFLINE from
human RPS datasets (Brockbank, Uppsala, OSF) by `analyze_rps.py`, then
hardcoded into the CONSTANTS block below.

At runtime, the bot uses a PRIORITY-ORDER decision:

    Round 1 (no history)     -> play Paper    (exploits Rock bias)
    Round 2+ after a WIN     -> Win-Stay      (predict player repeats)
    Round 2+ after a LOSS    -> Lose-Shift    (predict player changes)
    Round 2+ after a TIE     -> Markov matrix (predict from last move)

The bot always plays the move that BEATS the predicted player move.

Usage
-----
    from bot import RPSBot

    bot = RPSBot()
    bot_move = bot.next_move()                   # round 1
    bot.record_round(player_move="R", bot_move=bot_move)

    bot_move = bot.next_move()                   # round 2
    bot.record_round(player_move="P", bot_move=bot_move)
    ...
"""

import random


# ============================================================================
# CONSTANTS  —  REPLACE THIS BLOCK WITH OUTPUT OF analyze_rps.py
# ============================================================================
# These are LITERATURE DEFAULTS used as placeholders so the bot runs today.
# Once analyze_rps.py is run on the real datasets (Brockbank + Uppsala),
# paste the printed "BOT CONSTANTS" block here verbatim.
#
# Sources for defaults:
#   - Rock bias ~35%    (Wang et al., 2014; Batzilis et al., 2019)
#   - Win-Stay  ~60%    (Brockbank & Vul, 2021)
#   - Lose-Shift ~80%   (Brockbank & Vul, 2021)

# Move frequency prior (used only as a tiebreaker when Markov is uniform)
MOVE_FREQUENCY = {
    "R": 0.354,
    "P": 0.330,
    "S": 0.316,
}

# Win-Stay / Lose-Shift rates from the human player's perspective
WSLS_RATES = {
    "win_stay":   0.60,   # after winning, player repeats their move
    "lose_shift": 0.80,   # after losing, player changes their move
}

# Order-1 Markov transition matrix with Laplace smoothing
# matrix[prev_player_move][next_player_move] = probability
# Literature default: slight diagonal bias (people repeat more than chance)
MARKOV_MATRIX = {
    "R": {"R": 0.40, "P": 0.32, "S": 0.28},
    "P": {"R": 0.30, "P": 0.38, "S": 0.32},
    "S": {"R": 0.31, "P": 0.33, "S": 0.36},
}

# Opening move — Paper beats the Rock bias
OPENING_MOVE = "P"


# ============================================================================
# GAME MECHANICS (do not modify)
# ============================================================================
MOVES = ("R", "P", "S")

# What beats what: BEATS[x] = the move that beats x
BEATS = {"R": "P", "P": "S", "S": "R"}

# Readable names
NAMES = {"R": "Rock", "P": "Paper", "S": "Scissors"}


def outcome(player_move, bot_move):
    """Return 'win' / 'loss' / 'tie' from the PLAYER's perspective."""
    if player_move == bot_move:
        return "tie"
    if BEATS[player_move] == bot_move:
        return "loss"   # bot played what beats player -> player lost
    return "win"


# ============================================================================
# BOT
# ============================================================================
class RPSBot:
    """
    Static RPS bot. Stateless across games, stateful within a game.

    Call `next_move()` to get the bot's move for the current round, then
    call `record_round(player_move, bot_move)` after revealing the player's
    move so the bot can update its history.
    """

    def __init__(self, seed=None):
        # Reproducibility for testing; None = truly random
        self._rng = random.Random(seed)

        # Full history of the current game
        self.history = []   # list of dicts: {"player": "R", "bot": "P", "result": "loss"}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def next_move(self):
        """Decide what the bot plays this round."""
        predicted_player_move = self._predict_player_move()
        return BEATS[predicted_player_move]

    def record_round(self, player_move, bot_move):
        """Store what happened so the next prediction has context."""
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
        """Clear history — call between players at the expo."""
        self.history = []

    # ------------------------------------------------------------------
    # Prediction logic (priority order)
    # ------------------------------------------------------------------

    def _predict_player_move(self):
        """
        Priority:
          1. No history           -> assume Rock (so bot plays Paper)
          2. Last round = WIN     -> Win-Stay
          3. Last round = LOSS    -> Lose-Shift
          4. Last round = TIE     -> Markov
        """
        # Rule 1 — opening move
        if not self.history:
            # Bot plays OPENING_MOVE, which beats the move we assume the player plays
            # OPENING_MOVE = "P" beats "R" -> we assume player plays Rock
            assumed = {v: k for k, v in BEATS.items()}[OPENING_MOVE]
            return assumed

        last = self.history[-1]
        last_player = last["player"]
        last_result = last["result"]

        # Rule 2 — Win-Stay
        if last_result == "win":
            if self._rng.random() < WSLS_RATES["win_stay"]:
                return last_player             # player repeats
            return self._markov_predict(last_player)

        # Rule 3 — Lose-Shift
        if last_result == "loss":
            if self._rng.random() < WSLS_RATES["lose_shift"]:
                # Player changes — Markov picks the more likely of the two other moves
                return self._markov_predict(last_player, exclude=last_player)
            return last_player                 # player sticks anyway

        # Rule 4 — Tie -> Markov only
        return self._markov_predict(last_player)

    def _markov_predict(self, prev_move, exclude=None):
        """
        Return the most probable next player move given the previous one.
        If `exclude` is given, that move is ignored (used for lose-shift).
        """
        row = MARKOV_MATRIX[prev_move]
        candidates = [m for m in MOVES if m != exclude]
        return max(candidates, key=lambda m: row[m])

    # ------------------------------------------------------------------
    # Stats (handy for the expo display)
    # ------------------------------------------------------------------

    def stats(self):
        """Return W/L/T counts and win rate from the BOT's perspective."""
        n = len(self.history)
        if n == 0:
            return {"rounds": 0, "bot_wins": 0, "player_wins": 0, "ties": 0, "bot_win_rate": 0.0}

        bot_wins    = sum(1 for r in self.history if r["result"] == "loss")  # player lost -> bot won
        player_wins = sum(1 for r in self.history if r["result"] == "win")
        ties        = sum(1 for r in self.history if r["result"] == "tie")

        return {
            "rounds":       n,
            "bot_wins":     bot_wins,
            "player_wins":  player_wins,
            "ties":         ties,
            "bot_win_rate": bot_wins / n,
        }


# ============================================================================
# DEMO — run `python3 bot.py` to see it play against a simulated human
# ============================================================================
if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("RPS BOT — quick interactive demo")
    print("=" * 60)
    print("Type R, P, or S to play a round. Type 'q' to quit.\n")

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

    # Final stats
    s = bot.stats()
    print("\n" + "=" * 60)
    print("FINAL STATS")
    print("=" * 60)
    print(f"  Rounds played : {s['rounds']}")
    print(f"  Bot wins      : {s['bot_wins']}")
    print(f"  Player wins   : {s['player_wins']}")
    print(f"  Ties          : {s['ties']}")
    if s["rounds"] > 0:
        print(f"  Bot win rate  : {s['bot_win_rate']*100:.1f}%")
    sys.exit(0)