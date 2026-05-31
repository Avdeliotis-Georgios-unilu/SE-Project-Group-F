from __future__ import annotations

import os

import pygame

_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJ_ROOT = os.path.dirname(_PKG_DIR)
ASSET_DIR = os.path.join(_PROJ_ROOT, "assets")

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
        "name": "Random", "lvl": "BEGINNER",
        "desc": "Picks randomly R/P/S. No strategy, no learning",
        "accent": (90, 200, 90),
    },
    "medium": {
        "data": BOT_MED_DATA, "palette": BOT_MED_PAL,
        "name": "Learner", "lvl": "INTERMEDIATE",
        "desc": "Counters your most common move",
        "accent": (255, 180, 40),
    },
    "hard": {
        "data": BOT_HARD_DATA, "palette": BOT_HARD_PAL,
        "name": "Strategic", "lvl": "ADVANCED",
        "desc": "Dataset-trained Markov + WSLS predictor",
        "accent": (255, 90, 90),
    },
}


def draw_pixel_art(surf: pygame.Surface, pos: tuple[int, int],
                   data: list[str], palette: dict[str, tuple[int, int, int]],
                   scale: int = 4) -> tuple[int, int]:
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
    if _ITEM_IMAGES:
        return _ITEM_IMAGES

    mapping = {"R": "RockMC.png", "P": "PaperMC.png", "S": "ScissorMC.png"}
    colours = {"R": (100, 100, 100), "P": (244, 236, 208), "S": (184, 184, 192)}
    for move, filename in mapping.items():
        path = os.path.join(ASSET_DIR, filename)
        try:
            _ITEM_IMAGES[move] = pygame.image.load(path).convert_alpha()
        except Exception:
            fallback = pygame.Surface(_ITEM_IMAGE_SIZE, pygame.SRCALPHA)
            fallback.fill(colours.get(move, (128, 128, 128)))
            _ITEM_IMAGES[move] = fallback
    return _ITEM_IMAGES


def get_item_image(move: str, size: tuple[int, int] | None = None) -> pygame.Surface:
    img = _load_item_images().get(move) or _ITEM_IMAGES["R"]
    if size is not None:
        img = pygame.transform.smoothscale(img, size)
    return img
