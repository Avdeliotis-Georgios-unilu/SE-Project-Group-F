"""
RPS Dataset Analysis
====================
Author: Gabriel (Group F)

Computes behavioral constants from human RPS datasets for use in bot.py.

Outputs:
  1. Move frequency distribution (Rock / Paper / Scissors %)
  2. Win-Stay / Lose-Shift rates
  3. Order-1 Markov transition matrix (with Laplace smoothing)
  4. Bot constants ready to paste into bot.py

Supported datasets (via parsers at the bottom):
  - Brockbank v2  : CSV from json_to_csv_v2.py (filtered: human rows only)
  - Uppsala       : PizzaRollExpert .txt file
  - OSF/Zhang-CMU : CSV (column names adapted once inspected)
  - Synthetic     : our own test CSV

Usage:
  python analyze_rps.py --dataset brockbank --file data/brockbank_v2.csv
  python analyze_rps.py --dataset uppsala   --file data/uppsala.txt
  python analyze_rps.py --dataset osf       --file data/osf_data.csv
  python analyze_rps.py --dataset synthetic --file data/rps_dataset.csv
"""

import csv
import argparse
from collections import defaultdict


# ---------------------------------------------------------------------------
# CANONICAL MOVE NAMES
# All parsers must output moves in this set.
# ---------------------------------------------------------------------------
MOVES = ["R", "P", "S"]
BEATS = {"R": "S", "P": "R", "S": "P"}    # key beats value
LOSES_TO = {"R": "P", "P": "S", "S": "R"}  # key loses to value
NAMES = {"R": "Rock", "P": "Paper", "S": "Scissors"}


def outcome(player_move, opponent_move):
    """Return 'WIN', 'LOSS', or 'TIE' from player's perspective."""
    if player_move == opponent_move:
        return "TIE"
    if BEATS[player_move] == opponent_move:
        return "WIN"
    return "LOSS"


# ---------------------------------------------------------------------------
# PARSERS — each returns a list of rounds:
#   [{"player": "R", "opponent": "P"}, ...]
# opponent may be None if not available in the dataset.
# ---------------------------------------------------------------------------

def parse_brockbank(filepath):
    """
    Brockbank v2 CSV (output of json_to_csv_v2.py).
    Expected columns: player_id, round_index, player_move, bot_move, is_bot
    Move encoding: 'rock' / 'paper' / 'scissors'  (lowercase strings)

    v2 note: every round has 2 rows (one per side). We filter is_bot == 0
    to keep only human moves, and pair each human row with its bot counterpart
    as the opponent.
    """
    encoding = {"rock": "R", "paper": "P", "scissors": "S"}
    rounds = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        print(f"[Brockbank] Columns found: {reader.fieldnames}")

        # v2 has is_bot column — filter for humans only
        has_is_bot = "is_bot" in (reader.fieldnames or [])

        for row in reader:
            # Skip bot rows in v2 format
            if has_is_bot and str(row.get("is_bot", "")).strip() not in ("0", "False", "false", ""):
                continue
            try:
                pm = encoding.get(str(row.get("player_move", "")).strip().lower())
                bm = encoding.get(str(row.get("bot_move", "")).strip().lower())
            except KeyError:
                print(f"[Brockbank] Unexpected row keys: {list(row.keys())}")
                print(f"[Brockbank] Sample row: {dict(row)}")
                raise
            if pm:
                rounds.append({"player": pm, "opponent": bm})
    print(f"[Brockbank] Loaded {len(rounds)} rounds.")
    return rounds


def parse_uppsala(filepath):
    """
    PizzaRollExpert Uppsala .txt format.
    Encoding: s=rock, x=scissors, p=paper, -=end of game
    Opponent moves are not recorded — opponent field will be None.
    """
    encoding = {"s": "R", "x": "S", "p": "P"}
    rounds = []
    with open(filepath, encoding="utf-8") as f:
        content = f.read()
    for char in content:
        if char in encoding:
            rounds.append({"player": encoding[char], "opponent": None})
        # '-' and whitespace are ignored (game separator / whitespace)
    print(f"[Uppsala] Loaded {len(rounds)} rounds.")
    return rounds


def parse_osf(filepath):
    """
    OSF / Zhang-Moisan-Gonzalez CSV.
    Column names are UNKNOWN until you download the file.
    Run once with --dataset osf to see column names printed,
    then update the keys below.
    """
    encoding = {"rock": "R", "paper": "P", "scissors": "S",
                "r": "R", "p": "P", "s": "S",
                "1": "R", "2": "P", "3": "S"}  # common encodings
    rounds = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        print(f"[OSF] Columns found: {reader.fieldnames}")
        for row in reader:
            # --- ADJUST COLUMN NAMES HERE once you see them ---
            player_col = "player_move"   # <-- change if different
            opponent_col = "opponent_move"  # <-- change if different
            pm = encoding.get(str(row.get(player_col, "")).strip().lower())
            bm = encoding.get(str(row.get(opponent_col, "")).strip().lower())
            if pm:
                rounds.append({"player": pm, "opponent": bm})
    print(f"[OSF] Loaded {len(rounds)} rounds.")
    return rounds


def parse_synthetic(filepath):
    """
    Our own synthetic dataset (rps_dataset.csv).
    Columns: round_id, player_id, player_move, bot_move, result,
             last_player_move, last_result
    Move encoding: 'Rock' / 'Paper' / 'Scissors'
    """
    encoding = {"rock": "R", "paper": "P", "scissors": "S"}
    rounds = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        print(f"[Synthetic] Columns found: {reader.fieldnames}")
        for row in reader:
            pm = encoding.get(row["player_move"].strip().lower())
            bm = encoding.get(row["bot_move"].strip().lower())
            if pm and bm:
                rounds.append({"player": pm, "opponent": bm})
    print(f"[Synthetic] Loaded {len(rounds)} rounds.")
    return rounds


PARSERS = {
    "brockbank": parse_brockbank,
    "uppsala":   parse_uppsala,
    "osf":       parse_osf,
    "synthetic": parse_synthetic,
}


# ---------------------------------------------------------------------------
# ANALYSIS FUNCTIONS
# ---------------------------------------------------------------------------

def frequency_analysis(rounds):
    """
    Count how often each move appears.
    Returns dict: {"R": 0.35, "P": 0.33, "S": 0.32}
    """
    counts = defaultdict(int)
    for r in rounds:
        counts[r["player"]] += 1
    total = sum(counts.values())
    freq = {m: counts[m] / total for m in MOVES}

    print("\n=== 1. MOVE FREQUENCY ===")
    for m in MOVES:
        print(f"  {NAMES[m]:8s}: {freq[m]*100:.1f}%  ({counts[m]} rounds)")
    print(f"  Total rounds: {total}")
    print(f"  Literature baseline: Rock ~35%, Paper ~33%, Scissors ~32%")

    # Flag if Rock is over-represented (expected)
    if freq["R"] > 0.34:
        print(f"  -> Rock bias confirmed ({freq['R']*100:.1f}%). "
              f"Bot should open with Paper.")
    else:
        print(f"  -> Rock bias NOT confirmed in this dataset.")

    return freq, counts


def wsls_analysis(rounds):
    """
    Win-Stay / Lose-Shift analysis.
    For each consecutive pair of rounds, check if player:
      - Stayed (same move) after a WIN
      - Shifted (different move) after a LOSS

    Requires opponent move to compute outcome.
    Returns dict with rates.
    """
    # Filter only rounds where we know the opponent move
    usable = [r for r in rounds if r["opponent"] is not None]
    if len(usable) < 2:
        print("\n=== 2. WIN-STAY / LOSE-SHIFT ===")
        print("  Skipped — no opponent move data in this dataset.")
        return None

    win_stay = win_shift = 0
    lose_stay = lose_shift = 0
    tie_stay = tie_shift = 0

    for i in range(1, len(usable)):
        prev = usable[i - 1]
        curr = usable[i]
        prev_outcome = outcome(prev["player"], prev["opponent"])
        stayed = (curr["player"] == prev["player"])

        if prev_outcome == "WIN":
            if stayed: win_stay += 1
            else:      win_shift += 1
        elif prev_outcome == "LOSS":
            if stayed: lose_stay += 1
            else:      lose_shift += 1
        else:  # TIE
            if stayed: tie_stay += 1
            else:      tie_shift += 1

    total_wins   = win_stay + win_shift
    total_losses = lose_stay + lose_shift
    total_ties   = tie_stay + tie_shift

    ws_rate = win_stay / total_wins if total_wins else 0
    ls_rate = lose_shift / total_losses if total_losses else 0

    print("\n=== 2. WIN-STAY / LOSE-SHIFT ===")
    print(f"  After WIN  : Stay {ws_rate*100:.1f}%  |  Shift {(1-ws_rate)*100:.1f}%"
          f"  (n={total_wins})")
    print(f"  After LOSS : Stay {(1-ls_rate)*100:.1f}%  |  Shift {ls_rate*100:.1f}%"
          f"  (n={total_losses})")
    print(f"  After TIE  : Stay {tie_stay/(total_ties or 1)*100:.1f}%  |  "
          f"Shift {tie_shift/(total_ties or 1)*100:.1f}%  (n={total_ties})")
    print(f"  Literature baseline: Win-Stay ~60%, Lose-Shift ~80%")

    if ws_rate > 0.50:
        print(f"  -> Win-Stay exploitable ({ws_rate*100:.1f}%). "
              f"After player wins, predict they repeat.")
    if ls_rate > 0.50:
        print(f"  -> Lose-Shift exploitable ({ls_rate*100:.1f}%). "
              f"After player loses, predict they change.")

    return {
        "win_stay_rate":   ws_rate,
        "lose_shift_rate": ls_rate,
        "n_wins":   total_wins,
        "n_losses": total_losses,
        "n_ties":   total_ties,
    }


def markov_analysis(rounds, laplace=True):
    """
    Build Order-1 Markov transition matrix.
    P(next_move | prev_move) for each (prev, next) pair.

    With Laplace smoothing:
      P(next | prev) = (count(prev->next) + 1) / (count(prev) + 3)

    Returns:
      matrix[prev][next] = probability
    """
    # Raw counts
    counts = defaultdict(lambda: defaultdict(int))
    for i in range(1, len(rounds)):
        prev_move = rounds[i - 1]["player"]
        next_move = rounds[i]["player"]
        counts[prev_move][next_move] += 1

    # Apply smoothing and normalize
    matrix = {}
    for prev in MOVES:
        row_total = sum(counts[prev][nxt] for nxt in MOVES)
        matrix[prev] = {}
        for nxt in MOVES:
            raw = counts[prev][nxt]
            if laplace:
                matrix[prev][nxt] = (raw + 1) / (row_total + 3)
            else:
                matrix[prev][nxt] = raw / row_total if row_total else 1/3

    print("\n=== 3. ORDER-1 MARKOV TRANSITION MATRIX ===")
    print(f"  (Laplace smoothing: {'ON' if laplace else 'OFF'})")
    header = f"  {'prev':8s}" + "".join(f"  -> {nxt}  " for nxt in MOVES)
    print(header)
    print("  " + "-" * (len(header) - 2))
    for prev in MOVES:
        row = f"  {NAMES[prev]:8s}"
        for nxt in MOVES:
            row += f"   {matrix[prev][nxt]:.3f} "
        print(row)

    # For each prev move, what does the bot predict (most likely next move)?
    print("\n  Bot prediction (most likely next move after each move):")
    for prev in MOVES:
        predicted_next = max(MOVES, key=lambda nxt: matrix[prev][nxt])
        bot_plays = LOSES_TO[predicted_next]  # bot plays what beats the predicted move
        print(f"  Player played {NAMES[prev]:8s} -> predict {NAMES[predicted_next]:8s} "
              f"-> bot plays {NAMES[bot_plays]}")

    return matrix


def statistical_check(counts, wsls, matrix):
    """
    Quick sanity checks on the computed values.
    Flags anything that deviates strongly from literature.
    """
    print("\n=== 4. SANITY CHECKS vs LITERATURE ===")
    total = sum(counts.values())

    checks = [
        ("Rock frequency",   counts["R"]/total, 0.33, 0.40, "expected ~35%"),
        ("Paper frequency",  counts["P"]/total, 0.30, 0.37, "expected ~33%"),
        ("Scissors freq",    counts["S"]/total, 0.28, 0.36, "expected ~32%"),
    ]
    if wsls:
        checks += [
            ("Win-Stay rate",   wsls["win_stay_rate"],   0.50, 0.75, "expected ~60%"),
            ("Lose-Shift rate", wsls["lose_shift_rate"], 0.65, 0.95, "expected ~80%"),
        ]

    for name, value, lo, hi, note in checks:
        status = "OK" if lo <= value <= hi else "WARN"
        print(f"  [{status}] {name:20s}: {value*100:.1f}%  ({note})")


def print_bot_constants(freq, wsls, matrix):
    """
    Print the final constants ready to paste into bot.py.
    """
    print("\n" + "=" * 60)
    print("BOT CONSTANTS — paste these into bot.py")
    print("=" * 60)

    print("\n# Move frequency priors (from dataset analysis)")
    print(f"MOVE_FREQUENCY = {{'R': {freq['R']:.3f}, 'P': {freq['P']:.3f}, 'S': {freq['S']:.3f}}}")

    if wsls:
        print(f"\n# Behavioral rates (from dataset analysis)")
        print(f"WSLS_RATES = {{")
        print(f"    'win_stay':   {wsls['win_stay_rate']:.3f},  "
              f"# probability player repeats after winning")
        print(f"    'lose_shift': {wsls['lose_shift_rate']:.3f},  "
              f"# probability player changes after losing")
        print(f"}}")

    print(f"\n# Order-1 Markov transition matrix (Laplace smoothed)")
    print(f"# MARKOV_MATRIX[prev_move][next_move] = probability")
    print(f"MARKOV_MATRIX = {{")
    for prev in MOVES:
        inner = ", ".join(f"'{nxt}': {matrix[prev][nxt]:.3f}" for nxt in MOVES)
        print(f"    '{prev}': {{{inner}}},")
    print(f"}}")

    print(f"\n# First move: play Paper (counters Rock bias)")
    print(f"OPENING_MOVE = 'P'")
    print("=" * 60)


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="RPS dataset analysis")
    parser.add_argument("--dataset", required=True,
                        choices=list(PARSERS.keys()),
                        help="Which dataset parser to use")
    parser.add_argument("--file", required=True,
                        help="Path to the dataset file")
    parser.add_argument("--no-laplace", action="store_true",
                        help="Disable Laplace smoothing on Markov matrix")
    args = parser.parse_args()

    print(f"\nRPS Analysis — dataset: {args.dataset}")
    print(f"File: {args.file}")
    print("=" * 60)

    # Load data
    parse_fn = PARSERS[args.dataset]
    rounds = parse_fn(args.file)

    if len(rounds) < 30:
        print(f"\nWARNING: Only {len(rounds)} rounds loaded. "
              f"Results may not be statistically reliable (need >=30).")
        return

    # Run analyses
    freq, counts = frequency_analysis(rounds)
    wsls = wsls_analysis(rounds)
    matrix = markov_analysis(rounds, laplace=not args.no_laplace)
    statistical_check(counts, wsls, matrix)
    print_bot_constants(freq, wsls, matrix)


if __name__ == "__main__":
    main()