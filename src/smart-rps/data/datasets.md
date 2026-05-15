# Datasets

## Sources

Two publicly available datasets were used to derive the bot's behavioral constants.

### Brockbank & Vul (2021)
- **Source**: [OSF repository](https://osf.io/4k5tz/) — *"Human Rock-Paper-Scissors"* by Erik Brockbank and Edward Vul, UC San Diego
- Two versions of the dataset: `brockbank_v1.csv` and `brockbank_v2.csv`
- v2 is the larger file and covers human-vs-bot play specifically, which is the most relevant context for this project
- Format: CSV with columns for player move, opponent move, outcome, and round number

### Uppsala / PizzaRollExpert
- **Source**: [Kaggle](https://www.kaggle.com/datasets/rasmusrse/rps-tournament-data) — tournament data collected at Uppsala University
- Single file: `data.txt`
- Move encoding: `s` = Rock, `x` = Scissors, `p` = Paper
- Format: plain text, one character per move

---

## Why the datasets are not bundled in the repository

The datasets were kept outside the repository (at `~/rps-datasets/`) for two reasons:

1. **Ownership**: the datasets are not ours. They are the work of their respective authors and are subject to their own licenses. Committing them into the project repo without explicit permission would be inappropriate.

2. **Size**: the Brockbank v2 file in particular is large enough that including it would bloat the repository unnecessarily for what is essentially a one-time analysis step.

---

## Parser approach

Rather than loading the datasets directly at runtime, a standalone parser script (`analyze_rps.py`) was written to process them offline.

The parser reads each dataset, computes the relevant behavioral statistics (move frequencies, Win-Stay/Lose-Shift rates, Markov transition probabilities), and outputs a ready-to-paste `CONSTANTS` block for `bot.py`.

This keeps the bot itself lean and dependency-free at runtime: it operates on static, pre-computed constants rather than carrying dataset loading logic or large data files into the expo environment.
