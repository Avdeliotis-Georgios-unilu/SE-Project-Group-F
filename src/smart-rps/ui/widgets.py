"""Reusable rendering primitives: fonts, panels, buttons, chips."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pygame

from ui.theme import Theme


_FONT_CACHE: dict[tuple[str, int, bool], pygame.font.Font] = {}


def _get_font(name_hint: str, size: int, bold: bool = False) -> pygame.font.Font:
    """Cached font loader. Tries the hinted name, falls back to system monospace."""
    key = (name_hint, size, bold)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    candidates = [name_hint, "dejavusansmono", "freemono", "couriernew",
                  "liberationmono", "ubuntumono", "notomono", "monospace", None]
    font = None
    for c in candidates:
        try:
            font = pygame.font.SysFont(c, size, bold=bold)
            test = font.render("W", True, (255, 255, 255))
            if test.get_height() >= size * 0.6:
                break
        except Exception:
            continue

    if font is None:
        font = pygame.font.Font(None, size)

    _FONT_CACHE[key] = font
    return font


def display_font(size: int) -> pygame.font.Font:
    """Bold monospace for headings."""
    return _get_font("dejavusansmono", size, bold=True)


def body_font(size: int) -> pygame.font.Font:
    """Monospace for body text."""
    return _get_font("dejavusansmono", size, bold=False)


def _blend(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    """Linear blend between two colours."""
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )


def draw_panel(surf: pygame.Surface, rect: pygame.Rect, theme: Theme) -> None:
    """Draw a themed panel with border."""
    pygame.draw.rect(surf, theme.panel, rect)
    pygame.draw.rect(surf, theme.line, rect, 1)


def draw_button(surf: pygame.Surface, rect: pygame.Rect, text: str,
                theme: Theme, font_size: int = 12, primary: bool = False,
                danger: bool = False, hover: bool = False,
                font: pygame.font.Font | None = None) -> None:
    """Draw a pixel-style button."""
    if font is None:
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


def draw_chip(surf: pygame.Surface, pos: tuple[int, int], text: str,
              theme: Theme, dot_colour=None) -> pygame.Rect:
    """Draw a small chip/badge. Returns its bounding rect."""
    font = display_font(9)
    text_surf = font.render(text, True, theme.dim)
    padding = 10
    dot_w = 8 if dot_colour else 0
    gap = 8 if dot_w else 0
    w = dot_w + gap + text_surf.get_width() + padding * 2
    h = text_surf.get_height() + 12
    rect = pygame.Rect(pos[0], pos[1], w, h)

    pygame.draw.rect(surf, theme.bg1, rect)
    pygame.draw.rect(surf, theme.line2, rect, 1)

    if dot_colour:
        dot_x = pos[0] + padding
        dot_y = pos[1] + h // 2 - 4
        pygame.draw.rect(surf, dot_colour, (dot_x, dot_y, 8, 8))
        text_x = dot_x + 8 + gap
    else:
        text_x = pos[0] + padding

    surf.blit(text_surf, (text_x, pos[1] + 6))
    return rect


@dataclass
class ClickZone:
    rect: pygame.Rect
    action: str
    data: Any = None


def _wrap_text(text: str, font: pygame.font.Font, max_width: int,
               colour: tuple[int, int, int] | None = None) -> list[pygame.Surface]:
    """Simple word-wrap returning list of pre-rendered surfaces."""
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