"""SmartRPSGame — state machine, round flow, and main loop."""
from __future__ import annotations

from typing import Any, Optional

import pygame

from game.constants import WINDOW_W, WINDOW_H, FPS
from game.gesture_lock import GestureLock
from camera.integration import CameraFeed
from bot.game_bot import pick_bot_move, judge, update_bot_history, reset_bot
from ui.fairness import commit
from ui.theme import Theme, THEME
from ui.widgets import ClickZone
from ui.screens import (_screen_menu, _screen_bot_select,
                        _screen_playing, _screen_gameover)


class SmartRPSGame:
    """Complete game state machine and main loop."""

    def __init__(self) -> None:
        pygame.init()
        # pygame.SCALED scales the logical 1280×800 surface to fit the
        # user's display and translates mouse events to logical coordinates.
        # Falls back to a regular window if the hardware renderer is absent
        # (headless environments, older GPU drivers, etc.).
        try:
            self.screen = pygame.display.set_mode(
                (WINDOW_W, WINDOW_H), pygame.SCALED)
        except pygame.error:
            self.screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
        pygame.display.set_caption("RPS Arena")
        self.clock = pygame.time.Clock()

        # Game state
        self.screen_name: str = "menu"  # menu | botselect | playing | gameover
        self.phase: str = "idle"  # idle | countdown | shoot | reveal
        self.bot_id: str = "medium"
        self.total_rounds: int = 5
        self.history: list[dict] = []
        self.player_score: int = 0
        self.bot_score: int = 0
        self.current_round: int = 0
        self.player_move: Optional[str] = None
        self.bot_move: Optional[str] = None
        self.locked: bool = False

        # Fairness commitment
        self.fair_hash: str = ""
        self.fair_seed: int = 0

        # Countdown
        self.countdown_val = None
        self.countdown_start: int = 0
        self.countdown_num: int = 3

        # Reveal
        self.reveal_start: int = 0
        self.reveal_duration: int = 2200

        # Camera (device lifecycle lives in camera/integration.py)
        self.camera_feed = CameraFeed()
        self.cam_status: str = self.camera_feed.status
        self.cam_ok: bool = self.camera_feed.ok
        # Latest camera frame + detected gesture, refreshed by _poll_camera.
        # Hand detection (MediaPipe, ~10 ms/call) is throttled OFF the
        # render rate: at most once per _detect_interval_ms. The cached
        # gesture is still fed to the lock every frame, so lock timing is
        # unchanged. 0 disables the throttle (used by deterministic tests).
        self._cam_frame = None
        self._cam_gesture: str = "No hand"
        self._detect_interval_ms: int = 33  # ~30 Hz detection
        self._last_detect_ms: int = 0

        # Gesture lock-in — the sole move-input channel during a battle.
        self.gesture_lock = GestureLock()

        # Tick counter for animations
        self.clock_tick: int = 0

        # Button hover state (reset each frame)
        self._click_zones: list[ClickZone] = []


    @property
    def theme(self) -> Theme:
        return THEME

    @property
    def camera_ready(self) -> bool:
        """A live camera is mandatory — the battle is gesture-only."""
        return self.cam_ok and self.cam_status == "LIVE"

    # ------------------------------------------------------------------
    # Camera
    # ------------------------------------------------------------------

    def _read_camera(self):
        """Delegate to the camera feed. Returns (frame, gesture_name)."""
        return self.camera_feed.read()

    def _poll_camera(self) -> None:
        if self.screen_name != "playing":
            return
        now = pygame.time.get_ticks()
        if self._detect_interval_ms == 0 \
                or now - self._last_detect_ms >= self._detect_interval_ms:
            self._last_detect_ms = now
            frame, gesture_name = self._read_camera()
            self._cam_frame = frame
            self._cam_gesture = gesture_name
        if self.screen_name == "playing" and self.phase == "shoot" \
                and not self.locked:
            move = self.gesture_lock.update(self._cam_gesture)
            if move is not None:
                self.pick_move(move)

    # ------------------------------------------------------------------
    # Game flow
    # ------------------------------------------------------------------

    def start_match(self) -> None:
        """Begin a new match. No-op without a camera — the battle is
        gesture-only, so a match is unplayable without one. The bot-select
        screen also disables its entry button; this is defense in depth
        (also guards the game-over 'PLAY AGAIN' path)."""
        if not self.camera_ready:
            return
        self.history = []
        self.player_score = 0
        self.bot_score = 0
        self.current_round = 0
        self.player_move = None
        self.bot_move = None
        self.locked = False
        self.fair_hash = ""
        self.fair_seed = 0
        self.gesture_lock.reset()
        reset_bot()
        self.phase = "idle"
        self.screen_name = "playing"
        self._start_round()

    def _start_round(self) -> None:
        """Initiate a new round: bot picks, countdown begins."""
        self.player_move = None
        self.bot_move = None
        self.locked = False

        # Bot picks its move now (before player reveals)
        self.bot_move = pick_bot_move(self.bot_id, self.history)
        self.fair_hash, self.fair_seed = commit(self.bot_move)

        # Begin countdown
        self.phase = "countdown"
        self.countdown_num = 3
        self.countdown_val = 3
        self.countdown_start = pygame.time.get_ticks()

    def _handle_countdown(self) -> None:
        """Progress the countdown sequence."""
        if self.phase != "countdown":
            return

        elapsed = pygame.time.get_ticks() - self.countdown_start
        tick_duration = 800  # ms per count

        if self.countdown_num > 0 and elapsed >= tick_duration:
            self.countdown_num -= 1
            if self.countdown_num > 0:
                self.countdown_val = self.countdown_num
                self.countdown_start = pygame.time.get_ticks()
            else:
                # SHOOT! — from here the detected hand gesture is the only
                # way to commit a move. No timer, no random fallback: the
                # phase stays open until GestureLock locks one in.
                self.countdown_val = "SHOOT"
                self.countdown_start = pygame.time.get_ticks()
                self.phase = "shoot"
                self.gesture_lock.reset()
                self.countdown_num = 0

    def pick_move(self, move: str) -> None:
        """Commit the player's move. Sole caller is the gesture lock."""
        if self.phase != "shoot" or self.locked:
            return
        self.locked = True
        self.player_move = move
        # Brief lock-in pause, then reveal.
        pygame.time.set_timer(pygame.USEREVENT + 1, 450, True)

    def _resolve_round(self, player_move: str) -> None:
        """Score the round and show the result."""
        self.player_move = player_move
        self.locked = True
        self.phase = "reveal"
        self.reveal_start = pygame.time.get_ticks()

        outcome = judge(player_move, self.bot_move)
        self.history.append({
            "player": player_move,
            "bot": self.bot_move,
            "outcome": outcome,
        })

        update_bot_history(player_move, outcome)

        if outcome == "win":
            self.player_score += 1
        elif outcome == "lose":
            self.bot_score += 1

    def _check_reveal_done(self) -> None:
        """After reveal, advance to next round or game over."""
        if self.phase != "reveal":
            return
        if pygame.time.get_ticks() - self.reveal_start >= self.reveal_duration:
            self.current_round += 1
            if self.current_round >= self.total_rounds:
                self.screen_name = "gameover"
                self.phase = "idle"
            else:
                self._start_round()

    def quit_to_menu(self) -> None:
        """Return to main menu."""
        self.screen_name = "menu"
        self.phase = "idle"
        self.fair_hash = ""
        self.fair_seed = 0
        self.cam_ok = self.camera_feed.is_open() and self.camera_feed.ok

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Run the game loop."""
        running = True

        while running:
            dt = self.clock.tick(FPS)
            self.clock_tick += 1

            # --- Event handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    running = self._handle_keydown(event) if running else False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self._handle_click(event.pos)

                elif event.type == pygame.USEREVENT + 1:
                    # Delayed reveal after lock-in
                    if self.player_move:
                        self._resolve_round(self.player_move)

            # --- Update ---
            self._handle_countdown()
            self._check_reveal_done()
            self._poll_camera()

            # --- Draw ---
            self._click_zones.clear()
            self.screen.fill(self.theme.bg)

            if self.screen_name == "menu":
                _screen_menu(self.screen, self.theme, self._click_zones)
            elif self.screen_name == "botselect":
                _screen_bot_select(self.screen, self.theme,
                                    self.bot_id, self.total_rounds,
                                    self._click_zones, self.camera_ready)
            elif self.screen_name == "playing":
                self._draw_playing_screen()
            elif self.screen_name == "gameover":
                _screen_gameover(self.screen, self.theme,
                                 self._build_state_dict(), self._click_zones)

            pygame.display.flip()

        self._cleanup()

    def _draw_playing_screen(self) -> None:
        """Draw the playing screen.

        Uses the frame cached by _poll_camera so the device is read at most
        once per tick.
        """
        _screen_playing(self.screen, self.theme, self._build_state_dict(),
                        self._click_zones, self._cam_frame, self._cam_gesture)

    def _build_state_dict(self) -> dict:
        """Package current state for render functions."""
        return {
            "screen": self.screen_name,
            "phase": self.phase,
            "bot_id": self.bot_id,
            "total_rounds": self.total_rounds,
            "history": self.history,
            "player_score": self.player_score,
            "bot_score": self.bot_score,
            "current_round": self.current_round,
            "player_move": self.player_move,
            "bot_move": self.bot_move,
            "locked": self.locked,
            "gesture_held": self.gesture_lock.held_move,
            "gesture_progress": self.gesture_lock.progress,
            "countdown": self.countdown_val,
            "countdown_start": self.countdown_start,
            "cam_status": self.cam_status,
            "cam_ok": self.cam_ok,
            "clock_tick": self.clock_tick,
            "fair_hash": self.fair_hash,
            "fair_seed": self.fair_seed,
        }

    def _handle_keydown(self, event: pygame.event.Event) -> bool:
        """Handle keyboard input. Returns False if the game should quit."""
        if event.key == pygame.K_ESCAPE:
            if self.screen_name == "playing":
                self.quit_to_menu()
            elif self.screen_name in ("botselect", "gameover"):
                self.screen_name = "menu"
            return True

        # Menu screen: any key -> bot select (menu navigation only; not a
        # battle interaction). During a battle there is intentionally NO
        # keyboard move input — the hand gesture is the only way to play.
        if self.screen_name == "menu":
            self.screen_name = "botselect"
            return True

        return True

    def _handle_click(self, pos: tuple[int, int]) -> None:
        """Handle mouse clicks via click zones."""
        # Check zones in reverse (last drawn = on top)
        for zone in reversed(self._click_zones):
            if zone.rect.collidepoint(pos):
                self._dispatch_click(zone.action, zone.data)
                return

    def _dispatch_click(self, action: str, data: Any) -> None:
        """Execute the action associated with a click zone."""
        if action == "start":
            self.screen_name = "botselect"

        elif action == "close_bot_select":
            self.screen_name = "menu"

        elif action == "select_bot":
            self.bot_id = data

        elif action == "select_rounds":
            self.total_rounds = data

        elif action == "start_match":
            self.start_match()

        elif action == "quit_to_menu":
            self.quit_to_menu()

        elif action == "play_again":
            self.start_match()

    def _cleanup(self) -> None:
        """Release resources."""
        self.camera_feed.release()
        pygame.quit()