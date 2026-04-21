# RPS Bot Constants — Analysis Results

**Author:** Gabriel (Group F)
**Date:** April 2026
**Status:** Analysis complete. `bot.py` still uses literature defaults pending logic refactor.

This document records the behavioral constants extracted from four data sources. `bot.py` currently contains the **literature defaults** as placeholders; the three dataset-derived sets are recorded here for reference and for later A/B testing.

---

## ⚠️ Important finding: Win-Stay literature baseline does not hold in Brockbank

Both Brockbank datasets (v1 and v2) show the **opposite** of the classic Win-Stay pattern documented by Wang et al. (2014):

| Source | Win-Stay rate | Interpretation |
|---|---|---|
| Literature (Wang 2014, lab H-vs-H) | ~60% | Humans repeat after winning |
| Brockbank v1 (online H-vs-bot) | 32.1% | Humans **shift** after winning |
| Brockbank v2 (online H-vs-bot, larger) | 14.7% | Humans shift aggressively |

**Hypothesis:** when humans know they are playing a bot, they deliberately cycle through moves to "feel random," producing a strong Win-Shift pattern. The classic Win-Stay literature was built on human-vs-human lab studies, which is a different behavioral context.

**Implication for `bot.py`:** the current logic says "after a player win, predict they repeat." For our expo context (humans vs bot, just like Brockbank), this is wrong. The prediction logic needs to be flipped — **Win-Shift, not Win-Stay** — before deploying these constants.

Lose-Shift (~73–77%) and the Markov anti-repetition diagonal are consistent across all datasets and match literature reasonably well. Only Win-Stay is reversed.

---

## Constants Set 1 — Literature defaults (currently in `bot.py`)

These are the placeholders `bot.py` uses today. Sourced from Wang et al. (2014), Batzilis et al. (2019), Brockbank & Vul (2021) classic baselines.

```python
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
```

**Notes:**
- Assumes Rock bias (~35%) and slight diagonal bias in Markov (humans repeat more than chance)
- These assumptions are NOT supported by our dataset analysis below
- `win_stay: 0.60` is contradicted by both Brockbank datasets

---

## Constants Set 2 — Uppsala (Markov only)

**Source:** PizzaRollExpert/Rock-paper-scissors-data (Uppsala/Katedralskolan, 2014)
**Sample:** 3,059 rounds, human-vs-human school setting
**Outcome data:** not recorded → WSLS cannot be computed

```python
MOVE_FREQUENCY = {"R": 0.311, "P": 0.318, "S": 0.371}

# WSLS_RATES not available — no outcome column in dataset

MARKOV_MATRIX = {
    "R": {"R": 0.289, "P": 0.336, "S": 0.374},
    "P": {"R": 0.329, "P": 0.302, "S": 0.369},
    "S": {"R": 0.314, "P": 0.315, "S": 0.371},
}

OPENING_MOVE = "R"   # counters Scissors (most frequent at 37.1%)
```

**Notes:**
- Rock bias is absent (31.1% — below 1/3)
- Scissors is the most frequent move (37.1%) — opposite of literature
- Markov signal is weak and dominated by overall frequency (every row predicts Scissors)
- Not recommended as sole source — use only as a stability check against Brockbank

---

## Constants Set 3 — Brockbank v1

**Source:** erik-brockbank/rps, v1 data
**Sample:** 35,969 rounds across an earlier participant pool
**Protocol:** online, human-vs-bot

```python
MOVE_FREQUENCY = {"R": 0.319, "P": 0.336, "S": 0.346}

WSLS_RATES = {
    "win_stay":   0.321,   # ⚠ Actually means Win-Shift at 67.9%
    "lose_shift": 0.765,
}

MARKOV_MATRIX = {
    "R": {"R": 0.294, "P": 0.358, "S": 0.348},
    "P": {"R": 0.334, "P": 0.263, "S": 0.403},
    "S": {"R": 0.326, "P": 0.383, "S": 0.290},
}

OPENING_MOVE = "R"   # counters Scissors (34.6%)
```

**Notes:**
- Win-Stay only 32.1% → Win-Shift is 67.9%
- Lose-Shift 76.5% matches literature
- Anti-repetition pattern visible on Markov diagonal (R→R = 0.29, P→P = 0.26, S→S = 0.29, all below 1/3)

---

## Constants Set 4 — Brockbank v2 (RECOMMENDED for deployment)

**Source:** erik-brockbank/rps, v2 data
**Sample:** 69,365 rounds across 265 players
**Protocol:** online, human-vs-bot, multiple bot strategies

```python
MOVE_FREQUENCY = {"R": 0.309, "P": 0.332, "S": 0.359}

WSLS_RATES = {
    "win_stay":   0.147,   # ⚠ Actually means Win-Shift at 85.3%
    "lose_shift": 0.731,
}

MARKOV_MATRIX = {
    "R": {"R": 0.213, "P": 0.431, "S": 0.356},
    "P": {"R": 0.351, "P": 0.186, "S": 0.463},
    "S": {"R": 0.352, "P": 0.382, "S": 0.266},
}

OPENING_MOVE = "R"   # counters Scissors (35.9%)
```

**Notes:**
- Largest sample → most reliable point estimates
- Strong Win-Shift (85.3%) and anti-repetition pattern
- Clean Markov predictions:
  - After Rock → predict Paper (43%) → bot plays Scissors
  - After Paper → predict Scissors (46%) → bot plays Rock
  - After Scissors → predict Paper (38%) → bot plays Scissors

---

## How to switch which set `bot.py` uses

**Not yet implemented.** Currently `bot.py` has the Literature constants hardcoded at the top.

Switching to a dataset-derived set requires two changes (not done yet):

1. **Replace the four constant values** at the top of `bot.py`
2. **Flip the prediction logic** so that after a player win, the bot predicts they'll **shift**, not stay. Specifically, the `if last_result == "win"` branch in `_predict_player_move()` needs to call `_markov_predict(last_player, exclude=last_player)` (exclude their last move from predictions) instead of returning `last_player` directly.

These two changes should be made together in a single commit — flipping the logic without updating the constants, or vice versa, would silently degrade the bot.

**Until both changes are made, `bot.py` remains on the literature placeholders, which are internally consistent (Win-Stay logic + Win-Stay constants) even if they don't match our deployment context.**

---

## Source data

All three datasets are at `~/rps-datasets/` (not tracked in this repo due to size):

- `uppsala.txt` — 5 KB
- `brockbank_v1.csv` — 4.1 MB
- `brockbank_v2.csv` — 134 MB

To reproduce these numbers:

```bash
cd src/smart-rps/bot
python3 analyze_rps.py --dataset uppsala   --file ~/rps-datasets/uppsala.txt
python3 analyze_rps.py --dataset brockbank --file ~/rps-datasets/brockbank_v1.csv
python3 analyze_rps.py --dataset brockbank --file ~/rps-datasets/brockbank_v2.csv
```

---

## References

- Brockbank, E. & Vul, E. (2021). *Humans fail to outwit adaptive rock-paper-scissors opponents.* Proc. Cognitive Science Society.
- Wang, Z., Xu, B. & Zhou, H.-J. (2014). *Social cycling and conditional responses in the rock-paper-scissors game.* Scientific Reports, 4: 5830.
- Batzilis, D., Jaffe, S., Levitt, S., List, J.A. & Picel, J. (2019). *Behavior in strategic settings: evidence from a million rock-paper-scissors games.* Games, 10(2): 18.
