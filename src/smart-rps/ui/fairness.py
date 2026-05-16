"""
Provably Fair

Proves the bot's move was decided before the player revealed their gesture.

Verification (anyone can check):
    SHA256("{seed}:{move}") == hash_str
"""

import hashlib
import random


def commit(move: str) -> tuple[str, int]:
    

    seed = random.randint(0, 100)
    hash_str = _hash(move, seed)
    return hash_str, seed


def _hash(move: str, seed: int) -> str:
    """SHA-256 of '{seed}:{move}'. Seed goes first to prevent prefix guessing."""
    payload = f"{seed}:{move}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()