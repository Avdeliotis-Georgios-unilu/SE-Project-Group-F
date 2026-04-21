"""
Smart RPS — Alpha
=================
Plays Rock-Paper-Scissors: human vs bot, round by round, with a running score.

This is the ALPHA. Player moves are entered on the keyboard (R/P/S).
When Irina exposes camera classification as `camera.classifier.classify_move`,
flip USE_CAMERA = True below and rounds will use the webcam instead.

Run:
    cd src/smart-rps
    python3 main.py              # keyboard mode (default)
    python3 main.py --rounds 10  # play exactly 10 rounds

Author: Gabriel (Group F)
"""

import argparse
import sys

from bot import RPSBot
from bot.bot import MOVES, NAMES, outcome


# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------
# Flip to True once camera.classifier.classify_move(frame) exists.
USE_CAMERA = False

# Default number of rounds per game (expo sessions are ~10).
DEFAULT_ROUNDS = 10


# ----------------------------------------------------------------------------
# INPUT BACKENDS
# ----------------------------------------------------------------------------
def get_player_move_keyboard(round_num):
    """Ask the player to type their move. Returns 'R'/'P'/'S' or None to quit."""
    while True:
        try:
            raw = input(f"Round {round_num} — your move (R/P/S, q to quit): ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print()
            return None

        if raw == "Q":
            return None
        if raw in MOVES:
            return raw
        print("  Invalid. Please type R, P, S, or q.")


def get_player_move_camera(round_num):
    """
    Camera-backed input. Requires camera.classifier.classify_move(frame) -> 'R'/'P'/'S'.
    Does NOT exist yet — this is the integration stub for when Irina's code is ready.
    """
    # Deferred imports so keyboard mode works even if cv2/mediapipe aren't installed.
    from camera.camera import get_camera
    from camera.classifier import classify_move  # <-- Irina's module will export this

    print(f"Round {round_num} — show your hand to the camera (q to quit)...")
    cam = get_camera()
    if cam is None:
        print("  [ERROR] No camera available. Falling back to keyboard.")
        return get_player_move_keyboard(round_num)

    try:
        # Simple policy: grab frames until we get a confident classification.
        # Irina's classify_move should return 'R'/'P'/'S' or None if no hand.
        while True:
            frame = cam.read_frame()
            if frame is None:
                continue
            move = classify_move(frame)
            if move in MOVES:
                return move
    finally:
        cam.release()


# ----------------------------------------------------------------------------
# ROUND LIFECYCLE
# ----------------------------------------------------------------------------
def play_round(bot, round_num, get_move):
    """Play one round. Returns True if the round was played, False if quit."""
    # Bot decides FIRST (commits to its move before seeing the player's).
    bot_move = bot.next_move()

    # Get the human's move via whichever backend is active.
    player_move = get_move(round_num)
    if player_move is None:
        return False  # user quit

    # Record + compute outcome.
    bot.record_round(player_move=player_move, bot_move=bot_move)
    result = outcome(player_move, bot_move)
    result_str = {"win": "YOU WIN", "loss": "BOT WINS", "tie": "TIE"}[result]

    print(f"  You: {NAMES[player_move]:8s} | Bot: {NAMES[bot_move]:8s} | -> {result_str}\n")
    return True


# ----------------------------------------------------------------------------
# MAIN LOOP
# ----------------------------------------------------------------------------
def run_game(max_rounds=DEFAULT_ROUNDS, use_camera=USE_CAMERA):
    print("=" * 60)
    print("SMART RPS — alpha")
    print(f"Mode: {'camera' if use_camera else 'keyboard'}   Rounds: {max_rounds}")
    print("=" * 60)

    bot = RPSBot()
    get_move = get_player_move_camera if use_camera else get_player_move_keyboard

    for round_num in range(1, max_rounds + 1):
        played = play_round(bot, round_num, get_move)
        if not played:
            break

    # Final summary.
    s = bot.stats()
    print("=" * 60)
    print("FINAL")
    print("=" * 60)
    print(f"  Rounds       : {s['rounds']}")
    print(f"  Bot wins     : {s['bot_wins']}")
    print(f"  Player wins  : {s['player_wins']}")
    print(f"  Ties         : {s['ties']}")
    if s["rounds"] > 0:
        print(f"  Bot win rate : {s['bot_win_rate'] * 100:.1f}%")


def main():
    parser = argparse.ArgumentParser(description="Smart RPS alpha game loop")
    parser.add_argument("--rounds", type=int, default=DEFAULT_ROUNDS,
                        help=f"Number of rounds to play (default: {DEFAULT_ROUNDS})")
    parser.add_argument("--camera", action="store_true",
                        help="Use camera input instead of keyboard (requires Irina's classifier)")
    args = parser.parse_args()

    run_game(max_rounds=args.rounds, use_camera=args.camera or USE_CAMERA)


if __name__ == "__main__":
    main()