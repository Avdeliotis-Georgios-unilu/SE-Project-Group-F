# RPS Bot Constants

## Win-Stay does not hold in human-vs-bot contexts

Both Brockbank datasets show the opposite of the classic Win-Stay pattern:

| Source | Win-Stay rate | Behavior |
|---|---|---|
| Literature (Wang 2014, lab H-vs-H) | ~60% | Repeat after winning |
| Brockbank v1 (online H-vs-bot) | 32.1% | Shift after winning |
| Brockbank v2 (online H-vs-bot) | 14.7% | Shift aggressively |

The prediction logic in `bot.py` currently says "after a player win, predict they repeat." For our expo (humans vs bot), this needs to be flipped to **Win-Shift** before deploying dataset-derived constants.

Lose-Shift (~73–77%) and Markov anti-repetition are consistent across all datasets.

---

## Literature defaults (currently in `bot.py`)

From Wang et al. (2014), Batzilis et al. (2019), Brockbank & Vul (2021).

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

---

## Uppsala

3,059 rounds, human-vs-human. No outcome data — WSLS unavailable.

```python
MOVE_FREQUENCY = {"R": 0.311, "P": 0.318, "S": 0.371}

MARKOV_MATRIX = {
    "R": {"R": 0.289, "P": 0.336, "S": 0.374},
    "P": {"R": 0.329, "P": 0.302, "S": 0.369},
    "S": {"R": 0.314, "P": 0.315, "S": 0.371},
}

OPENING_MOVE = "R"   # counters Scissors (37.1%)
```

Scissors most frequent (37.1%), no Rock bias. Weak Markov signal — every row predicts Scissors.

---

## Brockbank v1

35,969 rounds, online human-vs-bot.

```python
MOVE_FREQUENCY = {"R": 0.319, "P": 0.336, "S": 0.346}

WSLS_RATES = {
    "win_stay":   0.321,   # Win-Shift is 67.9%
    "lose_shift": 0.765,
}

MARKOV_MATRIX = {
    "R": {"R": 0.294, "P": 0.358, "S": 0.348},
    "P": {"R": 0.334, "P": 0.263, "S": 0.403},
    "S": {"R": 0.326, "P": 0.383, "S": 0.290},
}

OPENING_MOVE = "R"   # counters Scissors (34.6%)
```

---

## Brockbank v2 (recommended)

69,365 rounds across 265 players, online human-vs-bot.

```python
MOVE_FREQUENCY = {"R": 0.309, "P": 0.332, "S": 0.359}

WSLS_RATES = {
    "win_stay":   0.147,   # Win-Shift is 85.3%
    "lose_shift": 0.731,
}

MARKOV_MATRIX = {
    "R": {"R": 0.213, "P": 0.431, "S": 0.356},
    "P": {"R": 0.351, "P": 0.186, "S": 0.463},
    "S": {"R": 0.352, "P": 0.382, "S": 0.266},
}

OPENING_MOVE = "R"   # counters Scissors (35.9%)
```

Markov predictions: after Rock → Paper (43%), after Paper → Scissors (46%), after Scissors → Paper (38%).

---

## Switching constants in `bot.py`

Requires two changes together:

1. Replace the four constant values at the top of `bot.py`
2. Flip the `if last_result == "win"` branch in `_predict_player_move()` from Win-Stay to Win-Shift

Do both in one commit — one without the other silently degrades the bot.

---

## References

- Brockbank & Vul (2021). *Humans fail to outwit adaptive rock-paper-scissors opponents.* Proc. Cognitive Science Society.
- Wang, Xu & Zhou (2014). *Social cycling and conditional responses in the rock-paper-scissors game.* Scientific Reports, 4: 5830.
- Batzilis, Jaffe, Levitt, List & Picel (2019). *Behavior in strategic settings: evidence from a million rock-paper-scissors games.* Games, 10(2): 18.