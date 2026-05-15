# Datasets

## What we use

Two datasets are used to compute the bot's behavioral constants (move frequencies, Win-Stay/Lose-Shift rates, Markov transition probabilities).

### Brockbank & Vul (2021)
- **Where**: [OSF repository](https://osf.io/4k5tz/)
- **Files**: `brockbank_v1.csv`, `brockbank_v2.csv`
- **Why**: v2 contains human-vs-bot RPS games, which matches our expo setup. It includes outcome data, so we can compute Win-Stay/Lose-Shift rates alongside move frequencies and Markov transitions.
- **Format**: CSV — columns include `player_move`, `player_outcome`, `player_id`, `round_index`, `is_bot`

### Uppsala / PizzaRollExpert
- **Where**: [Kaggle](https://www.kaggle.com/datasets/rasmusrse/rps-tournament-data)
- **File**: `data.txt`
- **Why**: large set of human-vs-human tournament moves. No outcome data, so only move frequencies and Markov transitions are computed (WSLS is skipped).
- **Format**: plain text — `s` = Rock, `x` = Scissors, `p` = Paper, `-` = player boundary

## Why they are not in the repository

1. **Not ours** — they belong to their respective authors and are subject to their own licenses.
2. **Too large** — the Brockbank v2 file in particular would bloat the repo for a one-time analysis step.

## How they are used

The datasets are processed offline by `analyze_rps.py`, which parses each file and outputs a `CONSTANTS` block ready to paste into `bot.py`. The bot itself never loads or reads the datasets — it runs on static, pre-computed constants.

```
python analyze_rps.py --dataset brockbank --file data/brockbank_v2.csv
python analyze_rps.py --dataset uppsala   --file data/data.txt
```