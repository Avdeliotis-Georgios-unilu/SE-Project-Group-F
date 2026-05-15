"""
RPS Dataset Analysis

Parses RPS datasets and outputs behavioral constants for bot.py:
  1. Move frequency distribution
  2. Win-Stay / Lose-Shift rates (when outcome data is available)
  3. Order-1 Markov transition matrix (Laplace smoothed)
  4. Ready-to-paste CONSTANTS block

Supported datasets:
  - Brockbank v1/v2 : CSV, human-vs-bot games (primary)
  - Uppsala         : PizzaRollExpert .txt, human-vs-human tournament

Usage:
  python analyze_rps.py --dataset brockbank --file data/brockbank_v2.csv
  python analyze_rps.py --dataset uppsala   --file data/data.txt
"""

import csv
import argparse
from collections import defaultdict


MOVES = ["R", "P", "S"]
BEATS = {"R": "S", "P": "R", "S": "P"}
LOSES_TO = {"R": "P", "P": "S", "S": "R"}
NAMES = {"R": "Rock", "P": "Paper", "S": "Scissors"}


'''
# PARSERS
Each parser returns a list of round dicts:
  {"player": "R", "outcome": "WIN"|"LOSS"|"TIE"|None,
   "player_id": str, "new_player": bool}
"new_player" marks the start of a new player's sequence so analysis
functions don't compute transitions across player boundaries.
'''

def parse_brockbank(filepath):
    """
    Brockbank v1/v2 CSV parser.
    v1: has player_move + player_outcome, no is_bot column.
    v2: has is_bot column — filter is_bot == '0' to keep human rows only.
    """
    move_encoding = {"rock": "R", "paper": "P", "scissors": "S"}
    outcome_encoding = {"win": "WIN", "loss": "LOSS", "tie": "TIE"}

    raw_rows = []
    with open(filepath, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        print(f"[Brockbank] Columns found: {reader.fieldnames}")

        has_is_bot = "is_bot" in (reader.fieldnames or [])
        has_outcome = "player_outcome" in (reader.fieldnames or [])

        for row in reader:
            if has_is_bot and str(row.get("is_bot", "")).strip() != "0":
                continue

            move = move_encoding.get(str(row.get("player_move", "")).strip().lower())
            if not move:
                continue

            outcome = None
            if has_outcome:
                outcome = outcome_encoding.get(
                    str(row.get("player_outcome", "")).strip().lower()
                )

            try:
                round_index = int(row.get("round_index", 0))
            except (ValueError, TypeError):
                round_index = 0
            player_id = str(row.get("player_id", "")).strip()

            raw_rows.append((player_id, round_index, move, outcome))

    # Sort by (player_id, round_index) so consecutive rows belong to the same player
    raw_rows.sort(key=lambda r: (r[0], r[1]))

    rounds = []
    prev_player = None
    for player_id, _, move, outcome in raw_rows:
        rounds.append({
            "player": move,
            "outcome": outcome,
            "player_id": player_id,
            "new_player": (player_id != prev_player),
        })
        prev_player = player_id

    n_players = len({r["player_id"] for r in rounds})
    n_with_outcome = sum(1 for r in rounds if r["outcome"] is not None)
    print(f"[Brockbank] Loaded {len(rounds)} rounds "
          f"across {n_players} players "
          f"({n_with_outcome} with outcome data).")
    return rounds


def parse_uppsala(filepath):
    """
    Uppsala/PizzaRollExpert .txt parser.
    Encoding: s=Rock, x=Scissors, p=Paper, -=player boundary.
    No outcome data — WSLS analysis will be skipped.
    """
    encoding = {"s": "R", "x": "S", "p": "P"}
    rounds = []
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    new_player_flag = True
    for char in content:
        if char == "-":
            new_player_flag = True
        elif char in encoding:
            rounds.append({
                "player": encoding[char],
                "outcome": None,
                "player_id": None,
                "new_player": new_player_flag,
            })
            new_player_flag = False

    print(f"[Uppsala] Loaded {len(rounds)} rounds.")
    return rounds


PARSERS = {
    "brockbank": parse_brockbank,
    "uppsala":   parse_uppsala,
}


# ANALYSIS FUNCTIONS


def frequency_analysis(rounds):
    """Move frequency distribution."""
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

    if freq["R"] > 0.34:
        print(f"  -> Rock bias confirmed ({freq['R']*100:.1f}%). "
              f"Bot should open with Paper.")
    else:
        most_freq = max(MOVES, key=lambda m: freq[m])
        counter = LOSES_TO[most_freq]
        print(f"  -> Most frequent move is {NAMES[most_freq]} ({freq[most_freq]*100:.1f}%). "
              f"Bot should open with {NAMES[counter]}.")

    return freq, counts


def wsls_analysis(rounds):
    """Win-Stay / Lose-Shift rates. Skips player boundaries."""
    usable = [r for r in rounds if r["outcome"] is not None]
    if len(usable) < 2:
        print("\n=== 2. WIN-STAY / LOSE-SHIFT ===")
        print("  Skipped — no outcome data in this dataset.")
        return None

    win_stay = win_shift = 0
    lose_stay = lose_shift = 0
    tie_stay = tie_shift = 0

    for i in range(1, len(rounds)):
        prev = rounds[i - 1]
        curr = rounds[i]

        if curr.get("new_player"):
            continue
        if prev["outcome"] is None:
            continue

        stayed = (curr["player"] == prev["player"])
        if prev["outcome"] == "WIN":
            if stayed: win_stay += 1
            else:      win_shift += 1
        elif prev["outcome"] == "LOSS":
            if stayed: lose_stay += 1
            else:      lose_shift += 1
        else:
            if stayed: tie_stay += 1
            else:      tie_shift += 1

    total_wins   = win_stay + win_shift
    total_losses = lose_stay + lose_shift
    total_ties   = tie_stay + tie_shift

    if total_wins + total_losses == 0:
        print("\n=== 2. WIN-STAY / LOSE-SHIFT ===")
        print("  Skipped — no valid consecutive outcome pairs.")
        return None

    ws_rate = win_stay / total_wins if total_wins else 0
    ls_rate = lose_shift / total_losses if total_losses else 0

    print("\n=== 2. WIN-STAY / LOSE-SHIFT ===")
    print(f"  After WIN  : Stay {ws_rate*100:.1f}%  |  Shift {(1-ws_rate)*100:.1f}%"
          f"  (n={total_wins})")
    print(f"  After LOSS : Stay {(1-ls_rate)*100:.1f}%  |  Shift {ls_rate*100:.1f}%"
          f"  (n={total_losses})")
    if total_ties:
        print(f"  After TIE  : Stay {tie_stay/total_ties*100:.1f}%  |  "
              f"Shift {tie_shift/total_ties*100:.1f}%  (n={total_ties})")
    print(f"  Literature baseline: Win-Stay ~60%, Lose-Shift ~80%")

    if ws_rate > 0.50:
        print(f"  -> Win-Stay exploitable ({ws_rate*100:.1f}%).")
    if ls_rate > 0.50:
        print(f"  -> Lose-Shift exploitable ({ls_rate*100:.1f}%).")

    return {
        "win_stay_rate":   ws_rate,
        "lose_shift_rate": ls_rate,
        "n_wins":   total_wins,
        "n_losses": total_losses,
        "n_ties":   total_ties,
    }


def markov_analysis(rounds, laplace=True):
    """Order-1 Markov transition matrix. Skips player boundaries."""
    counts = defaultdict(lambda: defaultdict(int))
    for i in range(1, len(rounds)):
        curr = rounds[i]
        if curr.get("new_player"):
            continue
        prev_move = rounds[i - 1]["player"]
        next_move = curr["player"]
        counts[prev_move][next_move] += 1

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

    print("\n  Bot prediction (most likely next move after each move):")
    for prev in MOVES:
        predicted_next = max(MOVES, key=lambda nxt: matrix[prev][nxt])
        bot_plays = LOSES_TO[predicted_next]
        print(f"  Player played {NAMES[prev]:8s} -> predict {NAMES[predicted_next]:8s} "
              f"-> bot plays {NAMES[bot_plays]}")

    return matrix


def statistical_check(counts, wsls, matrix):
    """Sanity checks against literature values."""
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
    """Print constants formatted for direct paste into bot.py."""
    print("\n" + "=" * 60)
    print("BOT CONSTANTS — paste these into bot.py")
    print("=" * 60)

    print("\n# Move frequency priors")
    print(f"MOVE_FREQUENCY = {{'R': {freq['R']:.3f}, 'P': {freq['P']:.3f}, 'S': {freq['S']:.3f}}}")

    if wsls:
        print(f"\n# Win-Stay / Lose-Shift rates")
        print(f"WSLS_RATES = {{")
        print(f"    'win_stay':   {wsls['win_stay_rate']:.3f},")
        print(f"    'lose_shift': {wsls['lose_shift_rate']:.3f},")
        print(f"}}")

    print(f"\n# Order-1 Markov transition matrix (Laplace smoothed)")
    print(f"MARKOV_MATRIX = {{")
    for prev in MOVES:
        inner = ", ".join(f"'{nxt}': {matrix[prev][nxt]:.3f}" for nxt in MOVES)
        print(f"    '{prev}': {{{inner}}},")
    print(f"}}")

    most_freq = max(MOVES, key=lambda m: freq[m])
    opening = LOSES_TO[most_freq]
    print(f"\nOPENING_MOVE = '{opening}'")
    print("=" * 60)


# MAIN


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

    parse_fn = PARSERS[args.dataset]
    rounds = parse_fn(args.file)

    if len(rounds) < 30:
        print(f"\nWARNING: Only {len(rounds)} rounds loaded. "
              f"Results may not be statistically reliable (need >=30).")
        return

    freq, counts = frequency_analysis(rounds)
    wsls = wsls_analysis(rounds)
    matrix = markov_analysis(rounds, laplace=not args.no_laplace)
    statistical_check(counts, wsls, matrix)
    print_bot_constants(freq, wsls, matrix)


if __name__ == "__main__":
    main()