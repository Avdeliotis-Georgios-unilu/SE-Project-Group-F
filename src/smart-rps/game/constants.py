"""Shared constants — game rules + window/layout geometry."""
from __future__ import annotations

WINDOW_W, WINDOW_H = 1280, 800

# Stage split: player (camera) side vs bot side.
# 60 % / 40 % — camera gets the wider half.
PLAYER_W = 768  # left column width (player/camera side)
FPS = 60

MOVES = ("R", "P", "S")
# BEATS[x] -> the move that *beats* x
BEATS: dict[str, str] = {"R": "P", "P": "S", "S": "R"}
MOVE_NAMES: dict[str, str] = {"R": "ROCK", "P": "PAPER", "S": "SCISSORS"}

# Stage layout (used by the playing screen).
TOP_BAR_H = 80
BOTTOM_HUD_H = 88
STAGE_H = WINDOW_H - TOP_BAR_H - BOTTOM_HUD_H