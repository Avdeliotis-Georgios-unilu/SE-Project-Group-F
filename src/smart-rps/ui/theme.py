"""Single colour theme — Cave."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Theme:
    name: str
    bg: tuple[int, int, int]
    bg1: tuple[int, int, int]
    bg2: tuple[int, int, int]
    panel: tuple[int, int, int]
    line: tuple[int, int, int]
    line2: tuple[int, int, int]
    ink: tuple[int, int, int]
    dim: tuple[int, int, int]
    accent: tuple[int, int, int]
    accent_ink: tuple[int, int, int]
    bot_accent: tuple[int, int, int]
    player_accent: tuple[int, int, int]


THEME = Theme(
    name="CAVE",
    bg=(10, 15, 18), bg1=(17, 24, 28), bg2=(24, 36, 40),
    panel=(14, 20, 22), line=(31, 46, 50), line2=(42, 61, 66),
    ink=(232, 242, 224), dim=(127, 144, 136),
    accent=(61, 255, 142), accent_ink=(5, 32, 18),
    bot_accent=(255, 122, 58), player_accent=(61, 255, 142),
)

# Kept for any legacy import that still uses THEMES["cave"]
THEMES: dict[str, Theme] = {"cave": THEME}
