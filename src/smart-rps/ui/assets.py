"""Sprite/pixel-art data, item images, and the pixel-art blitter."""
from __future__ import annotations

import os

import pygame

_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJ_ROOT = os.path.dirname(_PKG_DIR)
ASSET_DIR = os.path.join(_PROJ_ROOT, "assets")

FIST_DATA = [
    "................",
    "................",
    "....HHHHHH......",
    "...HHKKKKHH.....",
    "..HHKKKKKKH.....",
    "..HKKKWWKKH.....",
    ".HHKKKWWKKHH....",
    ".HKKKKKKKKKH....",
    ".HKKKKKKKKKH....",
    ".HKKKKKKKKKH....",
    "..HKKKKKKKKH....",
    "..HHKKKKKKHH....",
    "...HHKKKKHH.....",
    "....HHHHHH......",
    "................",
    "................",
]

PALM_DATA = [
    "................",
    "...K..K..K..K...",
    "..HK.HK.HK.HK...",
    "..HK.HK.HK.HK...",
    "..HK.HK.HK.HK...",
    "..HK.HK.HK.HK...",
    "..HKKHKKHKKHK...",
    "..HKKKKKKKKKK...",
    "..HKKKKKKKKKKK..",
    "..HKKKKKKKKKKK..",
    "..HKKKKKKKKKKK..",
    "..HHKKKKKKKKKK..",
    "...HHKKKKKKKKK..",
    "....HHHHHHHHH...",
    "................",
    "................",
]

PEACE_DATA = [
    "................",
    "....K.....K.....",
    "...HK....HK.....",
    "...HK....HK.....",
    "...HK....HK.....",
    "...HK....HK.....",
    "...HKKKKKHK.....",
    "...HKWWWKKK.....",
    "..HKKWWWKKKK....",
    "..HKKKKKKKKK....",
    "..HKKKKKKKKK....",
    "..HKKKKKKKKK....",
    "..HHKKKKKKKK....",
    "...HHHHHHHHH....",
    "................",
    "................",
]

HAND_PALETTE = {
    "K": (230, 181, 138),
    "H": (122, 74, 42),
    "W": (192, 140, 90),
}

GESTURE_DATA = {
    "R": FIST_DATA,
    "P": PALM_DATA,
    "S": PEACE_DATA,
}

# Bot portraits — three robots

BOT_EASY_DATA = [
    "................",
    "...GGGGGGGGGG...",
    "..GGggggggggGG..",
    "..GgYYYYYYYYgG..",
    "..GgYsskssksYgG.",
    "..GgYskkkkkkYgG.",
    "..GgYssksskkYgG.",
    "..GgYYWWWWYYYgG.",
    "..GgYYWmmWYYYgG.",
    "..GgYYWmmWYYYgG.",
    "..GgYYYYYYYYYgG.",
    "..GggggggggggG..",
    "...GGGGGGGGGG...",
    "....G.G..G.G....",
    "................",
    "................",
]
BOT_EASY_PAL = {
    "G": (42, 58, 26), "g": (90, 122, 58), "Y": (154, 171, 102),
    "s": (58, 58, 58), "k": (26, 26, 26),
    "W": (122, 106, 74), "m": (58, 42, 26),
}

BOT_MED_DATA = [
    "................",
    "..GGGGGGGGGGGG..",
    ".GggggggggggggG.",
    ".Ggggssggssgggg.",
    ".GgggsssggssggG.",
    ".GgggssggssgggG.",
    ".GgggggggggggGG.",
    ".GggKKgggggKKgG.",
    ".GggKKgggggKKgG.",
    ".GggggggggggggG.",
    ".GgggggMMMggggG.",
    ".GgggMMmmmMMggG.",
    ".GggMMMMMMMMggG.",
    ".GgggggggggggGG.",
    "..GGGGGGGGGGGG..",
    "................",
]
BOT_MED_PAL = {
    "G": (26, 58, 26), "g": (58, 106, 58), "s": (10, 10, 10),
    "K": (160, 230, 160), "M": (26, 26, 26), "m": (122, 58, 58),
}

BOT_HARD_DATA = [
    "................",
    "...nnnnnnnnnn...",
    "..nNNNNNNNNNNn..",
    "..nNbbbbbbbbNn..",
    "..nNbWWbbbWWbNn.",
    "..nNbWoWbWoWbNn.",
    "..nNbWWbbbWWbNn.",
    "..nNbbbbbbbbNn..",
    "..nNbbbWWWbbbNn.",
    "..nNbbWoooWbbNn.",
    "..nNbbbWWWbbbNn.",
    "..nNbbbbbbbbNn..",
    "..nNNNNNNNNNNn..",
    "...nnnnnnnnnn...",
    "....n.n..n.n....",
    "................",
]
BOT_HARD_PAL = {
    "n": (10, 10, 10), "N": (26, 26, 26), "b": (42, 42, 42),
    "W": (255, 229, 90), "o": (255, 241, 168),
}

BOT_PORTRAITS = {
    "easy": {
        "data": BOT_EASY_DATA, "palette": BOT_EASY_PAL,
        "name": "Beginner", "lvl": "RANDOM",
        "desc": "Picks uniformly at random. No strategy, no memory.",
        "stats": {"accuracy": 1, "speed": 2, "deception": 1},
        "accent": (90, 200, 90),
    },
    "medium": {
        "data": BOT_MED_DATA, "palette": BOT_MED_PAL,
        "name": "Intermediate", "lvl": "LEARNER",
        "desc": "Counters your last move. Assumes you repeat.",
        "stats": {"accuracy": 3, "speed": 3, "deception": 2},
        "accent": (255, 180, 40),
    },
    "hard": {
        "data": BOT_HARD_DATA, "palette": BOT_HARD_PAL,
        "name": "Advanced", "lvl": "STRATEGIC",
        "desc": "Dataset-trained Markov + WSLS predictor. 69K matches.",
        "stats": {"accuracy": 5, "speed": 5, "deception": 4},
        "accent": (255, 90, 90),
    },
}

def draw_pixel_art(surf: pygame.Surface, pos: tuple[int, int],
                   data: list[str], palette: dict[str, tuple[int, int, int]],
                   scale: int = 4) -> tuple[int, int]:
    """Draw pixel art from string-grid data. Returns (width, height) in pixels."""
    h = len(data)
    w = len(data[0]) if data else 0
    for y in range(h):
        row = data[y]
        for x in range(len(row)):
            ch = row[x]
            if ch in (".", " "):
                continue
            colour = palette.get(ch)
            if colour is None:
                continue
            px = pos[0] + x * scale
            py = pos[1] + y * scale
            pygame.draw.rect(surf, colour, (px, py, scale, scale))
    return (w * scale, h * scale)

_ITEM_IMAGES: dict[str, pygame.Surface] = {}
_ITEM_IMAGE_SIZE = (220, 220)

def _load_item_images() -> dict[str, pygame.Surface]:
    """Load and cache the Minecraft item PNGs. Called once at startup."""
    global _ITEM_IMAGES
    if _ITEM_IMAGES:
        return _ITEM_IMAGES
    mapping = {"R": "RockMC.png", "P": "PaperMC.png", "S": "ScissorMC.png"}
    for move, filename in mapping.items():
        path = os.path.join(ASSET_DIR, filename)
        try:
            img = pygame.image.load(path).convert_alpha()
            _ITEM_IMAGES[move] = img
        except Exception:
            # Fallback: create a solid-colour rect so the game still works
            fallback = pygame.Surface(_ITEM_IMAGE_SIZE, pygame.SRCALPHA)
            colours = {"R": (100, 100, 100), "P": (244, 236, 208), "S": (184, 184, 192)}
            fallback.fill(colours.get(move, (128, 128, 128)))
            _ITEM_IMAGES[move] = fallback
    return _ITEM_IMAGES


def get_item_image(move: str, size: tuple[int, int] | None = None) -> pygame.Surface:
    """Return the asset image for a move, optionally scaled."""
    imgs = _load_item_images()
    img = imgs.get(move)
    if img is None:
        img = imgs.get("R")  # fallback
    if size is not None and img is not None:
        img = pygame.transform.smoothscale(img, size)
    return img