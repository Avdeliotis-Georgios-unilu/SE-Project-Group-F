from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pygame

from ui.theme import Theme

_FONT_CACHE: dict[tuple[int, bool], pygame.font.Font] = {}

def _get_font(size: int, bold: bool = False) -> pygame.font.Font:
    key = (size, bold)
    if key not in _FONT_CACHE:
        _FONT_CACHE[key] = pygame.font.SysFont("dejavusansmono", size, bold=bold)
    return _FONT_CACHE[key]

def display_font(size: int) -> pygame.font.Font:
    return _get_font(size, bold=True)


def body_font(size: int) -> pygame.font.Font:
    return _get_font(size, bold=False)

def _blend(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )

def draw_panel(surf: pygame.Surface, rect: pygame.Rect, theme: Theme) -> None:
    pygame.draw.rect(surf, theme.panel, rect)
    pygame.draw.rect(surf, theme.line, rect, 1)

def draw_button(surf: pygame.Surface, rect: pygame.Rect, text: str,
                theme: Theme, font_size: int = 12, primary: bool = False,
                danger: bool = False, hover: bool = False) -> None:
    font = display_font(font_size)

    if primary:
        bg = theme.accent
        border = theme.accent
        ink = theme.accent_ink
        if hover:
            bg = _blend(bg, (255, 255, 255), 0.08)
    else:
        bg = theme.bg2
        border = theme.line2
        ink = theme.ink
        if hover:
            if danger:
                border = (255, 77, 77)
                ink = (255, 77, 77)
                bg = _blend(bg, (255, 77, 77), 0.1)
            else:
                border = theme.accent
                bg = _blend(bg, theme.accent, 0.14)

    pygame.draw.rect(surf, bg, rect)
    pygame.draw.rect(surf, border, rect, 2)

    text_surf = font.render(text, True, ink)
    text_rect = text_surf.get_rect(center=rect.center)
    surf.blit(text_surf, text_rect)

@dataclass
class ClickZone:
    rect: pygame.Rect
    action: str
    data: Any = None

def _wrap_text(text: str, font: pygame.font.Font, max_width: int,
               colour: tuple[int, int, int] | None = None) -> list[pygame.Surface]:
    if colour is None:
        colour = (255, 255, 255)
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = current + (" " if current else "") + word
        if font.size(test)[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return [font.render(line, True, colour) for line in lines]
