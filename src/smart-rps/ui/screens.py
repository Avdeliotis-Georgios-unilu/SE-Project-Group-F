from __future__ import annotations

import cv2
import pygame

from game.constants import (MOVES, MOVE_NAMES, WINDOW_W,
                            WINDOW_H, TOP_BAR_H, BOTTOM_HUD_H,
                            STAGE_H, PLAYER_W)
from bot.game_bot import judge
from ui.theme import Theme
try:
    from camera.hand_gestures import ROI_NX1, ROI_NY1, ROI_NX2, ROI_NY2
except Exception:
    ROI_NX1, ROI_NY1, ROI_NX2, ROI_NY2 = 0.266, 0.1875, 0.734, 0.8125
from ui.assets import (get_item_image, draw_pixel_art, GESTURE_DATA,
                       BOT_PORTRAITS, HAND_PALETTE)
from ui.widgets import (display_font, body_font, _blend,
                        draw_panel, draw_button,
                        _wrap_text, ClickZone)


def _screen_menu(surf: pygame.Surface, theme: Theme,
                 click_zones: list[ClickZone]) -> None:
    # main menu screen
    surf.fill(theme.bg)

    cx = WINDOW_W // 2

    accent_y = 140
    pygame.draw.line(surf, theme.accent, (cx - 180, accent_y), (cx + 180, accent_y), 2)
    dot_r = 4
    pygame.draw.circle(surf, theme.accent, (cx - 180, accent_y), dot_r)
    pygame.draw.circle(surf, theme.accent, (cx + 180, accent_y), dot_r)

    # fonts, buttons, layout
    pre_font = display_font(12)
    pre_title = pre_font.render("CAMERA-GESTURE ARCADE", True, theme.dim)
    pre_h = pre_title.get_height()

    title_font = display_font(68)
    rps = title_font.render("RPS", True, theme.ink)
    arena = title_font.render("ARENA", True, theme.accent)
    title_h = rps.get_height()
    total_title_w = rps.get_width() + arena.get_width()

    sub_font = body_font(20)
    sub1 = sub_font.render("Three moves. One bot trained on thousands of human matches.", True, theme.dim)
    sub2 = sub_font.render("Can you out-bluff the machine?", True, theme.dim)
    sub_h = sub1.get_height()

    btn_w, btn_h = 380, 62

    # Vertical layout
    spacing = 18
    total_content_h = (pre_h + spacing + title_h + spacing +
                       sub_h + spacing + sub_h + spacing + 50 + btn_h)

    start_y = (WINDOW_H - total_content_h) // 2 + 40

    surf.blit(pre_title, pre_title.get_rect(center=(cx, start_y + pre_h // 2)))
    cur_y = start_y + pre_h + spacing

    title_x = cx - total_title_w // 2
    surf.blit(rps, (title_x, cur_y))
    surf.blit(arena, (title_x + rps.get_width(), cur_y))
    cur_y += title_h + spacing

    surf.blit(sub1, sub1.get_rect(center=(cx, cur_y + sub_h // 2)))
    cur_y += sub_h + spacing
    surf.blit(sub2, sub2.get_rect(center=(cx, cur_y + sub_h // 2)))
    cur_y += sub_h + spacing + 80

    start_rect = pygame.Rect(cx - btn_w // 2, cur_y, btn_w, btn_h)

    mouse_pos = pygame.mouse.get_pos()
    draw_button(surf, start_rect, "START GAME", theme, font_size=11,
                primary=True, hover=start_rect.collidepoint(mouse_pos))

    click_zones.append(ClickZone(start_rect, "start"))



def _screen_bot_select(surf: pygame.Surface, theme: Theme,
                        selected_bot: str, selected_rounds: int,
                        click_zones: list[ClickZone],
                        cam_ready: bool = True) -> None:
    dim_bg = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
    dim_bg.fill((0, 0, 0, 190))
    surf.blit(dim_bg, (0, 0))

    card_w, card_h = 940, 560
    card_x = (WINDOW_W - card_w) // 2
    card_y = (WINDOW_H - card_h) // 2
    card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
    draw_panel(surf, card_rect, theme)
    pygame.draw.rect(surf, theme.line2, card_rect, 2)

    # Header 
    kicker = display_font(11).render("CONFIGURE MATCH", True, theme.dim)
    surf.blit(kicker, (card_x + 40, card_y + 28))
    title = display_font(24).render("PICK YOUR OPPONENT", True, theme.ink)
    surf.blit(title, (card_x + 40, card_y + 48))
    pygame.draw.line(surf, theme.accent, (card_x + 40, card_y + 82),
                     (card_x + card_w - 40, card_y + 82), 1)

    close_rect = pygame.Rect(card_x + card_w - 56, card_y + 22, 38, 38)
    draw_button(surf, close_rect, "X", theme, font_size=11,
                hover=close_rect.collidepoint(pygame.mouse.get_pos()))
    click_zones.append(ClickZone(close_rect, "close_bot_select"))

    # Bot cards 
    bot_ids = ["easy", "medium", "hard"]
    card_padding = 18
    card_item_w = (card_w - 80 - card_padding * 2) // 3
    card_item_h = 266
    grid_y = card_y + 96

    for i, bid in enumerate(bot_ids):
        bx = card_x + 40 + i * (card_item_w + card_padding)
        by = grid_y
        bot = BOT_PORTRAITS[bid]
        bot_accent = bot["accent"]
        is_selected = selected_bot == bid
        mouse_pos = pygame.mouse.get_pos()
        hover = pygame.Rect(bx, by, card_item_w, card_item_h).collidepoint(mouse_pos)

        active = is_selected or hover

        # Card surface
        card_bg = theme.panel
        card_border = theme.line2
        if active:
            card_border = bot_accent
            card_bg = _blend(theme.panel, bot_accent, 0.08)

        bot_rect = pygame.Rect(bx, by, card_item_w, card_item_h)
        pygame.draw.rect(surf, card_bg, bot_rect)
        pygame.draw.rect(surf, card_border, bot_rect, 2)

        # Top accent bar 
        top_bar_h = 4 if not is_selected else 8
        pygame.draw.rect(surf, bot_accent, (bx + 1, by + 1, card_item_w - 2, top_bar_h))

        num_str = ["I", "II", "III"][i]
        num_font = display_font(28)
        num_surf = num_font.render(num_str, True, bot_accent if active else theme.dim)
        surf.blit(num_surf, num_surf.get_rect(center=(bx + card_item_w // 2, by + 40)))

        # Bot name
        name_font = display_font(16)
        name_surf = name_font.render(bot["name"], True, theme.ink if active else theme.dim)
        surf.blit(name_surf, name_surf.get_rect(center=(bx + card_item_w // 2, by + 76)))

        # Level badge
        lvl_text = bot["lvl"]
        lvl_font = display_font(10)
        lvl_surf = lvl_font.render(lvl_text, True, theme.accent_ink if is_selected else theme.dim)
        lvl_w = lvl_surf.get_width() + 16
        lvl_h = lvl_surf.get_height() + 8
        lvl_rect = pygame.Rect(bx + card_item_w // 2 - lvl_w // 2, by + 96, lvl_w, lvl_h)
        if is_selected:
            pygame.draw.rect(surf, bot_accent, lvl_rect)
        else:
            pygame.draw.rect(surf, theme.bg2, lvl_rect)
            pygame.draw.rect(surf, theme.line2, lvl_rect, 1)
        surf.blit(lvl_surf, lvl_surf.get_rect(center=lvl_rect.center))

        # Description
        desc_lines = _wrap_text(bot["desc"], body_font(18), card_item_w - 28, theme.dim)
        dy = by + 140
        for line in desc_lines[:3]:
            surf.blit(line, (bx + 14, dy))
            dy += line.get_height() + 3

        # Selection indicator, with glow effect
        if is_selected:
            glow_rect = bot_rect.inflate(6, 6)
            pygame.draw.rect(surf, bot_accent, glow_rect, 2)

        click_zones.append(ClickZone(bot_rect, "select_bot", bid))

    # Rounds 
    rounds_y = grid_y + card_item_h + 8
    rounds_label = display_font(11).render("MATCH LENGTH . BEST OF", True, theme.dim)
    surf.blit(rounds_label, (card_x + 40, rounds_y))

    round_opts = [3, 5, 10, 20]
    opt_w = (card_w - 80 - 36) // 4
    opt_h = 44
    opt_y = rounds_y + 18
    for i, n in enumerate(round_opts):
        ox = card_x + 40 + i * (opt_w + 12)
        opt_rect = pygame.Rect(ox, opt_y, opt_w, opt_h)
        hover = opt_rect.collidepoint(pygame.mouse.get_pos())
        is_sel = selected_rounds == n

        bg = theme.panel
        border = theme.line2
        if is_sel or hover:
            border = BOT_PORTRAITS[selected_bot]["accent"] if is_sel else theme.accent
            bg = _blend(theme.panel, border, 0.1)
        pygame.draw.rect(surf, bg, opt_rect)
        pygame.draw.rect(surf, border, opt_rect, 2)

        num_surf = display_font(26).render(str(n), True, theme.ink if is_sel else theme.dim)
        surf.blit(num_surf, num_surf.get_rect(center=(ox + opt_w // 2, opt_y + opt_h // 2)))

        click_zones.append(ClickZone(opt_rect, "select_rounds", n))

    # Footer
    foot_y = card_y + card_h - 68
    pygame.draw.line(surf, theme.line2, (card_x + 40, foot_y - 8),
                     (card_x + card_w - 40, foot_y - 8), 1)

    if cam_ready:
        bot_name = BOT_PORTRAITS[selected_bot]["name"]
        foot_text = display_font(12).render(
            f"VS {bot_name}  .  BEST OF {selected_rounds}", True, theme.dim)
        surf.blit(foot_text, (card_x + 40, foot_y + 6))
    else:
        warn_surf = display_font(12).render(
            "CAMERA REQUIRED . CONNECT A CAMERA TO PLAY", True, theme.bot_accent)
        surf.blit(warn_surf, (card_x + 40, foot_y + 6))

    enter_rect = pygame.Rect(card_x + card_w - 280, foot_y + 4, 240, 54)
    if cam_ready:
        enter_hover = enter_rect.collidepoint(pygame.mouse.get_pos())
        draw_button(surf, enter_rect, "ENTER ARENA", theme, font_size=11,
                    primary=True, hover=enter_hover)
        click_zones.append(ClickZone(enter_rect, "start_match"))
    else:
        pygame.draw.rect(surf, theme.bg2, enter_rect)
        pygame.draw.rect(surf, theme.line2, enter_rect, 2)
        dis_surf = display_font(13).render("ENTER ARENA", True, theme.dim)
        surf.blit(dis_surf, dis_surf.get_rect(center=enter_rect.center))



def _screen_playing(surf: pygame.Surface, theme: Theme, state: dict,
                    click_zones: list[ClickZone], camera_frame=None,
                    gesture_name: str = "No hand") -> None:

    _draw_top_bar(surf, theme, state, click_zones)

    stage_y = TOP_BAR_H
    bot_w = WINDOW_W - PLAYER_W  # 512 px at 1280 wide

    # Player side 
    player_rect = pygame.Rect(0, stage_y, PLAYER_W, STAGE_H)
    _draw_player_side(surf, theme, state, player_rect, click_zones,
                      camera_frame, gesture_name)

    # Bot side
    bot_rect = pygame.Rect(PLAYER_W, stage_y, bot_w, STAGE_H)
    _draw_bot_side(surf, theme, state, bot_rect)

    # VS 
    _draw_vs_rail(surf, theme, stage_y, STAGE_H, state)

    # Countdown 
    _draw_countdown(surf, theme, state)

    # Result
    _draw_result_banner(surf, theme, state)

    _draw_bottom_hud(surf, theme, state)


def _draw_top_bar(surf: pygame.Surface, theme: Theme, state: dict,
                  click_zones: list[ClickZone]) -> None:
    bar_rect = pygame.Rect(0, 0, WINDOW_W, TOP_BAR_H)
    pygame.draw.rect(surf, theme.bg1, bar_rect)
    pygame.draw.line(surf, theme.line, (0, TOP_BAR_H - 1), (WINDOW_W, TOP_BAR_H - 1))

    # Brand
    logo_rect = pygame.Rect(18, 16, 32, 32)
    pygame.draw.rect(surf, theme.accent, logo_rect)
    logo_text = display_font(17).render("R", True, theme.accent_ink)
    surf.blit(logo_text, logo_text.get_rect(center=logo_rect.center))

    name_surf = display_font(17).render("RPS ARENA", True, theme.ink)
    surf.blit(name_surf, (58, 18))

    # Fairness hash
    fair_hash = state.get("fair_hash", "")
    if fair_hash:
        hash_short = fair_hash
        hash_font = display_font(10)
        hash_surf = hash_font.render(hash_short, True, theme.dim)
        hash_w = hash_surf.get_width() + 20
        hash_h = hash_surf.get_height() + 10
        hash_x = 58 + name_surf.get_width() + 16
        hash_rect = pygame.Rect(hash_x, 18, hash_w, hash_h)
        pygame.draw.rect(surf, theme.bg1, hash_rect)
        pygame.draw.rect(surf, theme.line2, hash_rect, 1)
        surf.blit(hash_surf, (hash_x + 10, hash_rect.y + 5))

    # Right side info
    screen = state.get("screen", "playing")
    round_idx = state.get("current_round", 0)
    total_rounds = state.get("total_rounds", 5)

    right_x = WINDOW_W - 28

    # Round chip
    if screen == "playing":
        rd_text = f"ROUND {round_idx + 1} / {total_rounds}"
        rd_font = display_font(11)
        rd_surf = rd_font.render(rd_text, True, theme.dim)
        rd_w = rd_surf.get_width() + 20
        rd_h = rd_surf.get_height() + 12
        rd_rect = pygame.Rect(right_x - rd_w - 80, 20, rd_w, rd_h)
        pygame.draw.rect(surf, theme.bg1, rd_rect)
        pygame.draw.rect(surf, theme.line2, rd_rect, 1)
        surf.blit(rd_surf, (rd_rect.x + 10, rd_rect.y + 6))

    # Quit button
    quit_btn_rect = pygame.Rect(right_x - 62, 13, 54, 42)
    quit_hover = quit_btn_rect.collidepoint(pygame.mouse.get_pos())
    draw_button(surf, quit_btn_rect, "QUIT", theme, font_size=9,
                danger=True, hover=quit_hover)
    click_zones.append(ClickZone(quit_btn_rect, "quit_to_menu"))



def _draw_gesture_zone(surf: pygame.Surface, roi: pygame.Rect, theme: Theme,
                       gesture_held: str | None, locked: bool,
                       progress: float) -> None:
    if locked:
        corner_col = theme.accent
        label_text = "LOCKED IN"
        label_fg = theme.accent_ink
        label_bg = (*theme.accent, 230)
        label_border = theme.accent
    elif gesture_held:
        corner_col = theme.accent
        label_text = "HOLD TO LOCK"
        label_fg = theme.accent
        label_bg = (0, 0, 0, 200)
        label_border = theme.accent
    else:
        corner_col = _blend(theme.accent, theme.dim, 0.55)
        label_text = "RPS ZONE"
        label_fg = theme.dim
        label_bg = (0, 0, 0, 180)
        label_border = _blend(theme.line2, theme.dim, 0.3)

    arm, bw = 40, 2
    pip = 4
    for cx, cy, sx, sy in [
        (roi.left,  roi.top,    +1, +1),
        (roi.right, roi.top,    -1, +1),
        (roi.left,  roi.bottom, +1, -1),
        (roi.right, roi.bottom, -1, -1),
    ]:
        pygame.draw.line(surf, corner_col, (cx, cy), (cx + sx * arm, cy), bw)
        pygame.draw.line(surf, corner_col, (cx, cy), (cx, cy + sy * arm), bw)
        pygame.draw.rect(surf, corner_col,
                         (cx + sx * (pip // 2) - pip // 2,
                          cy + sy * (pip // 2) - pip // 2, pip, pip))

    # Label chip below zone
    lbl_font = display_font(11)
    lbl_surf = lbl_font.render(label_text, True, label_fg)
    pad_x, pad_y = 14, 6
    chip_w = lbl_surf.get_width() + pad_x * 2
    chip_h = lbl_surf.get_height() + pad_y * 2
    chip_x = roi.centerx - chip_w // 2
    chip_y = roi.bottom + 8
    chip_bg = pygame.Surface((chip_w, chip_h), pygame.SRCALPHA)
    chip_bg.fill(label_bg)
    surf.blit(chip_bg, (chip_x, chip_y))
    pygame.draw.rect(surf, label_border, (chip_x, chip_y, chip_w, chip_h), 1)
    surf.blit(lbl_surf, (chip_x + pad_x, chip_y + pad_y))


def _draw_player_side(surf: pygame.Surface, theme: Theme, state: dict,
                      rect: pygame.Rect, click_zones: list[ClickZone],
                      camera_frame, gesture_name: str) -> None:
    header_h = 50

    pygame.draw.rect(surf, theme.player_accent,
                     (rect.x + 28, rect.y + 19, 12, 12))
    who_surf = display_font(13).render("PLAYER . YOU", True, theme.ink)
    surf.blit(who_surf, (rect.x + 50, rect.y + 16))

    vp_margin = 28
    vp_rect = pygame.Rect(rect.x + vp_margin, rect.y + header_h,
                           rect.width - vp_margin * 2,
                           rect.height - header_h - vp_margin)
    draw_panel(surf, vp_rect, theme)

    inner_margin = 2
    inner_rect = pygame.Rect(vp_rect.x + inner_margin, vp_rect.y + inner_margin,
                              vp_rect.width - inner_margin * 2,
                              vp_rect.height - inner_margin * 2)

    cam_ok = state.get("cam_ok", False)
    if cam_ok and camera_frame is not None:
        try:
            frame_rgb = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
            frame_rgb = cv2.resize(frame_rgb, (inner_rect.width, inner_rect.height))
            frame_surf = pygame.image.frombuffer(
                frame_rgb.tobytes(), (inner_rect.width, inner_rect.height), "RGB")
            surf.blit(frame_surf, inner_rect)
        except Exception:
            _draw_no_cam(surf, inner_rect, theme, state.get("cam_status", "DEMO"))
    else:
        _draw_no_cam(surf, inner_rect, theme, state.get("cam_status", "DEMO"))

    roi_pygame = pygame.Rect(
        inner_rect.x + int(ROI_NX1 * inner_rect.width),
        inner_rect.y + int(ROI_NY1 * inner_rect.height),
        int((ROI_NX2 - ROI_NX1) * inner_rect.width),
        int((ROI_NY2 - ROI_NY1) * inner_rect.height),
    )
    _draw_gesture_zone(
        surf, roi_pygame, theme,
        state.get("gesture_held"),
        state.get("locked", False),
        float(state.get("gesture_progress", 0.0)),
    )

    _draw_detection_stamp(surf, theme, vp_rect, state)

    phase = state.get("phase", "idle")
    if phase == "shoot":
        _draw_picker(surf, theme, vp_rect, state)


def _draw_no_cam(surf: pygame.Surface, rect: pygame.Rect, theme: Theme,
                 cam_status: str) -> None:
    surf.fill((8, 8, 8), rect)

    msgs: list[str]
    if cam_status == "DENIED":
        msgs = ["CAMERA BLOCKED", "GRANT ACCESS AND RESTART"]
    elif cam_status == "UNSUPPORTED":
        msgs = ["NO CAMERA DEVICE"]
    elif cam_status == "REQUESTING":
        msgs = ["REQUESTING CAMERA..."]
    else:
        msgs = ["CAMERA STANDBY"]

    font = display_font(13)
    total_h = len(msgs) * 28
    start_y = rect.centery - total_h // 2
    for i, msg in enumerate(msgs):
        msg_surf = font.render(msg, True, theme.dim)
        surf.blit(msg_surf, msg_surf.get_rect(center=(rect.centerx, start_y + i * 28)))


def _draw_detection_stamp(surf: pygame.Surface, theme: Theme,
                          vp_rect: pygame.Rect, state: dict) -> None:
    locked = state.get("locked", False)
    locked_move = state.get("player_move")
    if locked and locked_move:
        stamp_text = f"LOCKED . {MOVE_NAMES.get(locked_move, locked_move)}"
    elif state.get("cam_status") == "REQUESTING":
        stamp_text = "CONNECTING"
    elif state.get("cam_status") in ("DENIED", "UNSUPPORTED"):
        stamp_text = "DEMO MODE"
    else:
        stamp_text = "TRACKING"

    stamp_font = display_font(11)
    stamp_surf = stamp_font.render(stamp_text, True, theme.accent_ink if locked else theme.accent)
    stamp_pad = 10
    stamp_w = stamp_surf.get_width() + stamp_pad * 2
    stamp_h = stamp_surf.get_height() + stamp_pad
    stamp_rect = pygame.Rect(vp_rect.right - 14 - stamp_w, vp_rect.y + 14, stamp_w, stamp_h)

    if locked:
        pygame.draw.rect(surf, theme.accent, stamp_rect)
        pygame.draw.rect(surf, theme.accent, stamp_rect, 1)
    else:
        pygame.draw.rect(surf, (0, 0, 0, 150), stamp_rect)
        pygame.draw.rect(surf, theme.accent, stamp_rect, 1)
    surf.blit(stamp_surf, (stamp_rect.x + stamp_pad, stamp_rect.y + 5))


def _draw_picker(surf: pygame.Surface, theme: Theme, vp_rect: pygame.Rect,
                 state: dict) -> None:
    chip_w, chip_h = 124, 42
    gap = 14
    total_w = chip_w * 3 + gap * 2
    strip_x = vp_rect.centerx - total_w // 2
    strip_y = vp_rect.y + 14

    locked = state.get("locked", False)
    locked_move = state.get("player_move")
    held_move = state.get("gesture_held")
    progress = float(state.get("gesture_progress", 0.0))
    active_move = locked_move if locked else held_move

    #  background strip
    pad = 10
    bg_h = chip_h + 5 + 10  # chips + progress bar gap + bar height
    hint_h = 16
    bg_rect = pygame.Rect(strip_x - pad, strip_y - 6,
                          total_w + pad * 2, bg_h + hint_h + 8)
    bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    bg_surf.fill((0, 0, 0, 160))
    surf.blit(bg_surf, bg_rect)

    # Three move chips
    chip_labels = {"R": "ROCK", "P": "PAPER", "S": "SCISSORS"}
    for i, move in enumerate(MOVES):
        cx = strip_x + i * (chip_w + gap)
        chip_rect = pygame.Rect(cx, strip_y, chip_w, chip_h)
        is_active = active_move == move

        bg = _blend(theme.panel, theme.accent, 0.20 if locked and is_active
                    else 0.12 if is_active else 0.0)
        border = theme.accent if is_active else theme.line2
        pygame.draw.rect(surf, bg, chip_rect)
        pygame.draw.rect(surf, border, chip_rect, 1 if not is_active else 2)

        label = chip_labels.get(move, move)
        label_col = theme.ink if is_active else theme.dim
        label_surf = display_font(11).render(label, True, label_col)
        surf.blit(label_surf, label_surf.get_rect(center=chip_rect.center))

    bar_y = strip_y + chip_h + 5
    bar_h = 4
    pygame.draw.rect(surf, theme.bg2, (strip_x, bar_y, total_w, bar_h))
    fill = int(total_w * (1.0 if locked else progress))
    if fill > 0:
        bar_col = theme.accent if not locked else _blend(theme.accent, (255, 255, 255), 0.3)
        pygame.draw.rect(surf, bar_col, (strip_x, bar_y, fill, bar_h))

    if locked:
        hint, hint_col = "LOCKED", theme.accent
    elif held_move:
        hint, hint_col = "HOLD TO LOCK", theme.accent
    else:
        hint, hint_col = "SHOW A GESTURE", theme.dim
    hint_surf = display_font(11).render(hint, True, hint_col)
    surf.blit(hint_surf, hint_surf.get_rect(
        center=(vp_rect.centerx, bar_y + bar_h + 6)))


def _draw_bot_side(surf: pygame.Surface, theme: Theme, state: dict,
                   rect: pygame.Rect) -> None:
    bot_id = state.get("bot_id", "medium")
    bot = BOT_PORTRAITS.get(bot_id, BOT_PORTRAITS["medium"])
    difficulty = state.get("bot_id", "medium")

    header_h = 50
    pygame.draw.rect(surf, theme.bot_accent,
                     (rect.x + 28, rect.y + 19, 12, 12))
    who_surf = display_font(13).render(f"BOT . {bot['name']}", True, theme.ink)
    surf.blit(who_surf, (rect.x + 50, rect.y + 16))

    diff_text = f"DIFF . {difficulty.upper()}"
    diff_font = display_font(11)
    diff_surf = diff_font.render(diff_text, True, theme.dim)
    diff_w = diff_surf.get_width() + 28
    diff_h = diff_surf.get_height() + 12
    diff_rect = pygame.Rect(rect.right - diff_w - 28, rect.y + 16, diff_w, diff_h)
    pygame.draw.rect(surf, theme.bg1, diff_rect)
    pygame.draw.rect(surf, theme.line2, diff_rect, 1)
    pygame.draw.rect(surf, theme.bot_accent, (diff_rect.x + 8, diff_rect.y + 8, 8, 8))
    surf.blit(diff_surf, (diff_rect.x + 22, diff_rect.y + 6))

    # Dark themed background
    vp_margin = 28
    vp_rect = pygame.Rect(rect.x + vp_margin, rect.y + header_h,
                           rect.width - vp_margin * 2,
                           rect.height - header_h - vp_margin)
    pygame.draw.rect(surf, theme.bg, vp_rect)
    pygame.draw.rect(surf, theme.line2, vp_rect, 1)

    # Bot content based on phase
    phase = state.get("phase", "idle")
    cx = vp_rect.centerx
    cy = vp_rect.centery

    if phase == "idle":
        portrait_size = 208
        px = cx - portrait_size // 2
        py = cy - portrait_size // 2 - 20
        scale = max(3, portrait_size // 16)
        draw_pixel_art(surf, (px, py), bot["data"], bot["palette"], scale)
        ready_surf = display_font(16).render("READY", True, theme.bot_accent)
        surf.blit(ready_surf, ready_surf.get_rect(center=(cx, py + portrait_size + 24)))

    elif phase == "countdown":
        analyze_surf = display_font(14).render("ANALYZING", True, theme.bot_accent)
        surf.blit(analyze_surf, analyze_surf.get_rect(center=(cx, cy)))
        clock_tick = state.get("clock_tick", 0)
        for d in range(3):
            if (clock_tick // 20 + d) % 3 != 0:
                dot_x = cx + analyze_surf.get_width() // 2 + 12 + d * 16
                pygame.draw.rect(surf, theme.bot_accent, (dot_x, cy - 4, 8, 8))

    elif phase == "shoot":
        locked_surf = display_font(14).render("LOCKED IN", True, theme.bot_accent)
        surf.blit(locked_surf, locked_surf.get_rect(center=(cx, cy)))

    elif phase == "reveal":
        bot_move = state.get("bot_move")
        if bot_move:
            img_size = (220, 220)
            img = get_item_image(bot_move, img_size)
            img_rect = img.get_rect(center=(cx, cy - 10))
            surf.blit(img, img_rect)
            label_surf = display_font(15).render(
                MOVE_NAMES.get(bot_move, bot_move), True, theme.bot_accent)
            surf.blit(label_surf, label_surf.get_rect(center=(cx, cy + img_size[1] // 2 + 20)))


def _draw_vs_rail(surf: pygame.Surface, theme: Theme, stage_y: int,
                  stage_h: int, state: dict) -> None:
    cx = PLAYER_W
    # Rail line
    pygame.draw.line(surf, theme.line, (cx, stage_y), (cx, stage_y + stage_h), 1)

    # VS token
    token_size = 100
    token_rect = pygame.Rect(cx - token_size // 2,
                              stage_y + stage_h // 2 - token_size // 2,
                              token_size, token_size)
    phase = state.get("phase", "idle")
    pygame.draw.rect(surf, theme.bg, token_rect)

    border_col = theme.accent if phase == "shoot" else theme.line2
    vs_col = theme.accent if phase == "shoot" else theme.ink
    pygame.draw.rect(surf, border_col, token_rect, 2)
    vs_surf = display_font(30).render("VS", True, vs_col)

    surf.blit(vs_surf, vs_surf.get_rect(center=token_rect.center))


def _draw_countdown(surf: pygame.Surface, theme: Theme, state: dict) -> None:
    phase = state.get("phase", "idle")
    countdown_val = state.get("countdown")
    countdown_start = state.get("countdown_start", 0)

    if phase != "countdown" or countdown_val is None:
        return

    now = pygame.time.get_ticks()
    elapsed = now - countdown_start
    anim_progress = min(1.0, elapsed / 800)

    cx, cy = WINDOW_W // 2, WINDOW_H // 2

    if isinstance(countdown_val, int) and countdown_val > 0:
        # Number countdown
        scale = 0.4 + anim_progress * 1.0
        num_text = str(countdown_val)
        num_font = display_font(220)
        num_surf = num_font.render(num_text, True, theme.ink)
        # Scale
        new_w = int(num_surf.get_width() * scale)
        new_h = int(num_surf.get_height() * scale)
        if new_w > 0 and new_h > 0:
            scaled = pygame.transform.smoothscale(num_surf, (new_w, new_h))
            # Fade out at end
            if anim_progress > 0.7:
                alpha = int(255 * (1.0 - (anim_progress - 0.7) / 0.3))
                scaled.set_alpha(max(0, alpha))
            surf.blit(scaled, scaled.get_rect(center=(cx, cy)))

    elif countdown_val == "SHOOT":
        shoot_text = "SHOOT!"
        shoot_font = display_font(100)
        shoot_surf = shoot_font.render(shoot_text, True, theme.accent)
        scale = 0.4 + anim_progress * 1.0
        new_w = int(shoot_surf.get_width() * scale)
        new_h = int(shoot_surf.get_height() * scale)
        if new_w > 0 and new_h > 0:
            scaled = pygame.transform.smoothscale(shoot_surf, (new_w, new_h))
            if anim_progress > 0.6:
                alpha = int(255 * (1.0 - (anim_progress - 0.6) / 0.4))
                scaled.set_alpha(max(0, alpha))
            surf.blit(scaled, scaled.get_rect(center=(cx, cy)))


def _draw_result_banner(surf: pygame.Surface, theme: Theme, state: dict) -> None:
    phase = state.get("phase")
    if phase != "reveal":
        return

    player_move = state.get("player_move")
    bot_move = state.get("bot_move")
    if not player_move or not bot_move:
        return

    outcome = judge(player_move, bot_move)

    # Dimmed background
    dim_bg = pygame.Surface((WINDOW_W, WINDOW_H), pygame.SRCALPHA)
    dim_bg.fill((0, 0, 0, 140))
    surf.blit(dim_bg, (0, 0))

    # Card
    card_w, card_h = 620, 260
    card_x = (WINDOW_W - card_w) // 2
    card_y = (WINDOW_H - card_h) // 2
    card_rect = pygame.Rect(card_x, card_y, card_w, card_h)

    if outcome == "win":
        border_col = theme.player_accent
        title_text = "YOU WIN!"
        sub_text = f"{MOVE_NAMES[player_move]} BEATS {MOVE_NAMES[bot_move]}"
    elif outcome == "lose":
        border_col = theme.bot_accent
        title_text = "BOT WINS"
        sub_text = f"{MOVE_NAMES[bot_move]} BEATS {MOVE_NAMES[player_move]}"
    else:
        border_col = theme.dim
        title_text = "TIE"
        sub_text = f"BOTH PICKED {MOVE_NAMES[player_move]}"

    pygame.draw.rect(surf, theme.bg1, card_rect)
    pygame.draw.rect(surf, border_col, card_rect, 3)

    title_surf = display_font(60).render(title_text, True, border_col)
    surf.blit(title_surf, title_surf.get_rect(center=(card_x + card_w // 2, card_y + 60)))

    sub_surf = display_font(13).render(sub_text, True, theme.dim)
    surf.blit(sub_surf, sub_surf.get_rect(center=(card_x + card_w // 2, card_y + 130)))

    # Fairness proof
    fair_hash = state.get("fair_hash", "")
    fair_seed = state.get("fair_seed", 0)
    if fair_hash and bot_move:
        verify = f"PROOF . SHA256({fair_seed}:{bot_move}) . FIRST 12: {fair_hash[:12]}"
        verify_surf = display_font(9).render(verify, True, theme.dim)
        surf.blit(verify_surf, verify_surf.get_rect(center=(card_x + card_w // 2, card_y + 170)))


def _draw_bottom_hud(surf: pygame.Surface, theme: Theme, state: dict) -> None:
    hud_y = WINDOW_H - BOTTOM_HUD_H
    hud_rect = pygame.Rect(0, hud_y, WINDOW_W, BOTTOM_HUD_H)
    pygame.draw.rect(surf, theme.bg1, hud_rect)
    pygame.draw.line(surf, theme.line, (0, hud_y), (WINDOW_W, hud_y))

    player_score = state.get("player_score", 0)
    bot_score = state.get("bot_score", 0)
    total_rounds = state.get("total_rounds", 5)
    current_round = state.get("current_round", 0)
    history = state.get("history", [])

    # Player score (left)
    who_font = display_font(13)
    score_font = display_font(40)

    you_surf = who_font.render("YOU", True, theme.dim)
    surf.blit(you_surf, (32, hud_y + 8))
    ps_surf = score_font.render(f"{player_score:02d}", True, theme.player_accent)
    surf.blit(ps_surf, (32, hud_y + 26))

    # Bot score (right)
    bs_surf = score_font.render(f"{bot_score:02d}", True, theme.bot_accent)
    surf.blit(bs_surf, (WINDOW_W - 32 - bs_surf.get_width(), hud_y + 26))
    bot_who = who_font.render("BOT", True, theme.dim)
    surf.blit(bot_who, (WINDOW_W - 32 - bot_who.get_width(), hud_y + 8))

    # Round pips (center) — larger and more visible
    pip_size = 18
    pip_gap = 8
    total_pip_w = total_rounds * pip_size + (total_rounds - 1) * pip_gap
    pip_start_x = WINDOW_W // 2 - total_pip_w // 2
    pip_y = hud_y + 30

    for i in range(total_rounds):
        px = pip_start_x + i * (pip_size + pip_gap)
        pip_rect = pygame.Rect(px, pip_y, pip_size, pip_size)

        if i < len(history):
            h = history[i]
            if h.get("outcome") == "win":
                col = theme.player_accent
            elif h.get("outcome") == "lose":
                col = theme.bot_accent
            else:
                col = theme.dim
            pygame.draw.rect(surf, col, pip_rect)
        elif i == current_round:
            pygame.draw.rect(surf, theme.bg2, pip_rect)
            pygame.draw.rect(surf, theme.line2, pip_rect, 1)
            pygame.draw.rect(surf, theme.accent, pip_rect, 1)
        else:
            pygame.draw.rect(surf, theme.bg2, pip_rect)
            pygame.draw.rect(surf, theme.line2, pip_rect, 1)

    # Color legend below pips
    legend_y = pip_y + pip_size + 8
    legend_font = display_font(10)
    for label, col, lx in [("YOU", theme.player_accent, pip_start_x),
                             ("TIE", theme.dim, WINDOW_W // 2 - 16),
                             ("BOT", theme.bot_accent, pip_start_x + total_pip_w - 36)]:
        pygame.draw.rect(surf, col, (lx, legend_y, 8, 8))
        lbl = legend_font.render(label, True, theme.dim)
        surf.blit(lbl, (lx + 12, legend_y - 1))



def _screen_gameover(surf: pygame.Surface, theme: Theme, state: dict,
                     click_zones: list[ClickZone]) -> None:
    surf.fill(theme.bg)

    player_score = state.get("player_score", 0)
    bot_score = state.get("bot_score", 0)
    history = state.get("history", [])
    bot_id = state.get("bot_id", "medium")
    bot = BOT_PORTRAITS.get(bot_id, BOT_PORTRAITS["medium"])

    wins = sum(1 for h in history if h.get("outcome") == "win")
    losses = sum(1 for h in history if h.get("outcome") == "lose")
    ties = sum(1 for h in history if h.get("outcome") == "tie")

    if player_score > bot_score:
        verdict = "VICTORY"
        title_col = theme.player_accent
    elif player_score < bot_score:
        verdict = "DEFEATED"
        title_col = theme.bot_accent
    else:
        verdict = "STALEMATE"
        title_col = theme.ink

    # Card
    card_w, card_h = 780, 560
    card_x = (WINDOW_W - card_w) // 2
    card_y = (WINDOW_H - card_h) // 2
    card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
    draw_panel(surf, card_rect, theme)
    pygame.draw.rect(surf, theme.line2, card_rect, 2)

    # Verdict
    verdict_surf = display_font(13).render("FINAL VERDICT", True, theme.dim)
    surf.blit(verdict_surf, verdict_surf.get_rect(center=(WINDOW_W // 2, card_y + 44)))

    # Title 
    title_surf = display_font(74).render(verdict, True, title_col)
    surf.blit(title_surf, title_surf.get_rect(center=(WINDOW_W // 2, card_y + 120)))

    # Final scores
    score_y = card_y + 210
    you_label = display_font(13).render("YOU", True, theme.dim)
    surf.blit(you_label, you_label.get_rect(center=(WINDOW_W // 2 - 100, score_y)))
    ps_surf = display_font(56).render(str(player_score), True, theme.player_accent)
    surf.blit(ps_surf, ps_surf.get_rect(center=(WINDOW_W // 2 - 100, score_y + 50)))

    colon_surf = display_font(28).render(":", True, theme.dim)
    surf.blit(colon_surf, colon_surf.get_rect(center=(WINDOW_W // 2, score_y + 24)))

    bot_label = display_font(13).render(bot["name"], True, theme.dim)
    surf.blit(bot_label, bot_label.get_rect(center=(WINDOW_W // 2 + 100, score_y)))
    bs_surf = display_font(56).render(str(bot_score), True, theme.bot_accent)
    surf.blit(bs_surf, bs_surf.get_rect(center=(WINDOW_W // 2 + 100, score_y + 50)))

    # Stats grid
    stats_y = card_y + 330
    stats_grid_w = 420
    stats_grid_x = WINDOW_W // 2 - stats_grid_w // 2
    cell_w = stats_grid_w // 3

    for i, (label, value) in enumerate([("WINS", wins), ("LOSSES", losses), ("TIES", ties)]):
        cx = stats_grid_x + i * cell_w
        cell_rect = pygame.Rect(cx, stats_y, cell_w, 80)
        pygame.draw.rect(surf, theme.line2, cell_rect, 1)

        lbl_surf = display_font(13).render(label, True, theme.dim)
        surf.blit(lbl_surf, lbl_surf.get_rect(center=(cx + cell_w // 2, stats_y + 20)))
        val_surf = display_font(30).render(str(value), True, theme.ink)
        surf.blit(val_surf, val_surf.get_rect(center=(cx + cell_w // 2, stats_y + 54)))

    # Buttons
    btn_y = card_y + card_h - 88
    menu_rect = pygame.Rect(WINDOW_W // 2 - 248, btn_y, 224, 56)
    play_again_rect = pygame.Rect(WINDOW_W // 2 + 24, btn_y, 224, 56)

    mouse_pos = pygame.mouse.get_pos()
    draw_button(surf, menu_rect, "MAIN MENU", theme, font_size=10,
                hover=menu_rect.collidepoint(mouse_pos))
    draw_button(surf, play_again_rect, "PLAY AGAIN", theme, font_size=10,
                primary=True, hover=play_again_rect.collidepoint(mouse_pos))

    click_zones.append(ClickZone(menu_rect, "quit_to_menu"))
    click_zones.append(ClickZone(play_again_rect, "play_again"))

