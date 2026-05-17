# Using Pygame CE (Community Edition) - is actively maintained
# Better support for windows + raspberry pi

import sys
import os
import cv2
import mediapipe as mp
import pygame

USE_CAMERA = True       # Set to True to enable webcam input
USE_RANDOM_BOT = False   # False = strategic (normal), True = random (easy)
                         # Placeholder until the selection screen exists.

# Bot import
try:
    from bot.bot import StrategicBot, RandomBot
except ImportError:
    from bot import StrategicBot, RandomBot

import fairness


# Active window
WIDTH, HEIGHT = 1200, 800

# colours
BACKGROUND = (95, 85, 150)
BACKGROUND_2 = (165, 135, 195)
BACKGROUND_3 = (235, 210, 170)
PANEL = (245, 236, 215)
PANEL_SHADOW = (120, 90, 100)

ACCENT_PURPLE = (150, 75, 190)
ACCENT_RED = (180, 95, 75)
ACCENT_GREEN = (95, 135, 95)
ACCENT_ORANGE = (205, 140, 75)

TEXT_BRIGHT = (55, 45, 40)
TEXT_DIM = (110, 95, 80)

WHITE = (250, 245, 235)
BLACK = (55, 45, 40)


# Drawing helpers — pure functions, no game state.

def draw_background(surface):
    for x in range(WIDTH):
        ratio = x / WIDTH

        # purple -> pink
        if ratio < 0.5:
            blend = ratio * 2
            r = int(BACKGROUND[0] * (1 - blend) + BACKGROUND_2[0] * blend)
            g = int(BACKGROUND[1] * (1 - blend) + BACKGROUND_2[1] * blend)
            b = int(BACKGROUND[2] * (1 - blend) + BACKGROUND_2[2] * blend)

        # pink -> peach
        else:
            blend = (ratio - 0.5) * 2
            r = int(BACKGROUND_2[0] * (1 - blend) + BACKGROUND_3[0] * blend)
            g = int(BACKGROUND_2[1] * (1 - blend) + BACKGROUND_3[2] * blend)
            b = int(BACKGROUND_2[2] * (1 - blend) + BACKGROUND_3[2] * blend)

        pygame.draw.line(surface, (r, g, b), (x, 0), (x, HEIGHT))


def draw_card(surface, rect, radius=26):
    shadow = rect.copy()
    shadow.x += 8
    shadow.y += 10
    pygame.draw.rect(surface, (175, 105, 115), shadow, border_radius=radius)
    pygame.draw.rect(surface, PANEL, rect, border_radius=radius)


def draw_inner_panel(surface, rect, radius=20):
    pygame.draw.rect(
        surface,
        (245, 225, 210),
        rect,
        border_radius=radius
    )


def gesture_to_move(gesture_name):
    """Convert gesture string to R/P/S code."""
    return {"Rock": "R", "Paper": "P", "Scissors": "S"}.get(gesture_name)


def cv2_to_pygame(frame, width, height):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb = cv2.resize(frame_rgb, (width, height))
    return pygame.image.frombuffer(frame_rgb.tobytes(), (width, height), "RGB")


# Main game entry point.
# All per-game state (bot, scores, camera, fonts) lives inside this function
# so that calling run_game(StrategicBot()) and then run_game(RandomBot())
# gives a clean game each time. The selection screen (when built) will call
# this with whichever bot the user picked.

def run_game(bot):
    """Run a single game session with the given bot until the player quits.

    bot: an instance of StrategicBot or RandomBot (anything inheriting from
         RPSBot).
    """
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Smart Rock Paper Scissors")
    clock = pygame.time.Clock()

    # Fonts — must be created after pygame.init()
    titleFont = pygame.font.SysFont("verdana", 46, bold=True)
    labelFont = pygame.font.SysFont("verdana", 30, bold=True)
    smallFont = pygame.font.SysFont("verdana", 24)
    hashFont = pygame.font.SysFont("verdana", 16, bold=True)

    # Load bot images
    ASSET_PATH = os.path.join(os.path.dirname(__file__), "..", "assets")
    IMAGE_SIZE = (220, 220)

    def load_bot_image(filename):
        path = os.path.join(ASSET_PATH, filename)
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, IMAGE_SIZE)

    bot_images = {
        "R": load_bot_image("RockMC.png"),
        "P": load_bot_image("PaperMC.png"),
        "S": load_bot_image("ScissorMC.png"),
    }
    
    signpost = pygame.image.load(os.path.join(ASSET_PATH, "signpost.png")).convert_alpha()
    signpost = pygame.transform.scale(signpost, (180, 180))

    # Bot + game state
    bot = None
    bot_choice = None
    player_choice = None  # 'R', 'P', 'S' — from camera or keyboard fallback
    botScore = 0
    playerScore = 0
    difficulty = "easy" if isinstance(bot, RandomBot) else "normal"
    game_phase = "select_bot"
    max_rounds = 10
    resultsStart = 0

    # reveal phase
    revealStart = 0
    revealDuration = 1500
    revealed = False

    #countdown before using players move
    countdownActive = False
    countdownStart = 0
    countdownDuration = 2
    CountdownPlayerMove = None
    if USE_CAMERA is False:
        countdownDuration = 0

    # Fairness state
    commitment_hash = None
    commitment_seed = None
    round_num = 1            # for later

    # Camera + hand detection
    if USE_CAMERA:
        camera = cv2.VideoCapture(0)
        mp_hands = mp.solutions.hands
        mp_draw = mp.solutions.drawing_utils
        hand_detector = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
    else:
        camera = None
        mp_hands = None
        mp_draw = None
        hand_detector = None

    # Inner helpers that close over the state above.

    def draw_game_header(surface):
        title = titleFont.render("smart RPS", True, WHITE)
        title_shadow = titleFont.render("smart RPS", True, ACCENT_ORANGE)
        surface.blit(title_shadow, title_shadow.get_rect(center=(WIDTH // 2 + 3, 53 + 3)))
        surface.blit(title, title.get_rect(center=(WIDTH // 2, 53)))

        score_text = smallFont.render(
            f"bot {botScore}  •  player {playerScore}",
            True,
            TEXT_BRIGHT
        )
        surface.blit(score_text, score_text.get_rect(center=(WIDTH // 2, 95)))

        # Bot mode text layout on screen with signpost
        surface.blit(signpost, (WIDTH - 290, -20))
        mode_text = smallFont.render(difficulty, True, ACCENT_GREEN)
        mode_rect = mode_text.get_rect(center=(WIDTH - 110, 60))
        surface.blit(mode_text, mode_rect)

    def detect_gesture(frame):
        image = cv2.flip(frame, 1)
        image_height, image_width, _ = image.shape

        square_size = 300
        square_x1 = image_width // 2 - square_size // 2
        square_y1 = image_height // 2 - square_size // 2
        square_x2 = square_x1 + square_size
        square_y2 = square_y1 + square_size

        cv2.rectangle(
            image,
            (square_x1, square_y1),
            (square_x2, square_y2),
            (255, 190, 90),
            3
        )
        hand_area = image[square_y1:square_y2, square_x1:square_x2]
        hand_area_rgb = cv2.cvtColor(hand_area, cv2.COLOR_BGR2RGB)
        result = hand_detector.process(hand_area_rgb)

        gesture_name = "No hand"

        if result.multi_hand_landmarks:
            for one_hand in result.multi_hand_landmarks:
                mp_draw.draw_landmarks(hand_area, one_hand, mp_hands.HAND_CONNECTIONS)
                points = one_hand.landmark

                index_up  = points[8].y  < points[6].y
                middle_up = points[12].y < points[10].y
                ring_up   = points[16].y < points[14].y
                pinky_up  = points[20].y < points[18].y

                if not index_up and not middle_up and not ring_up and not pinky_up:
                    gesture_name = "Rock"
                elif index_up and middle_up and ring_up and pinky_up:
                    gesture_name = "Paper"
                elif index_up and middle_up and not ring_up and not pinky_up:
                    gesture_name = "Scissors"
                else:
                    gesture_name = "Unknown"

        return image, gesture_name

    def draw_fairness():
        if commitment_hash is None:
            return "Game Validity"
        return f"{commitment_hash}"
    
    def reset_match():
        nonlocal bot_choice, player_choice, botScore, playerScore
        nonlocal commitment_hash, commitment_seed, revealed, round_num
        nonlocal countdownActive, CountdownPlayerMove

        if bot is not None:
            bot.reset()

        bot_choice = None
        player_choice = None
        botScore = 0
        playerScore = 0
        commitment_hash = None
        commitment_seed = None
        revealed = False
        round_num = 1
        countdownActive = False
        CountdownPlayerMove = None


    def choose_bot_mode(mode):
        nonlocal bot, difficulty, game_phase

        if mode == "random":
            bot = RandomBot()
            difficulty = "Random"

        elif mode == "trained":
            bot = StrategicBot()
            difficulty = "Strategic"

        reset_match()
        game_phase = "playing" 
        start_round()

    def start_round(forced_move=None):
        """Bot commits its move BEFORE the player reveals. Starts the countdown."""
        nonlocal bot_choice, commitment_hash, commitment_seed
        nonlocal countdownActive, countdownStart, CountdownPlayerMove, revealed

        bot_choice = bot.next_move()
        commitment_hash, commitment_seed = fairness.commit(bot_choice)
        CountdownPlayerMove = forced_move
        countdownActive = True
        countdownStart = pygame.time.get_ticks()
        revealed = False

    def resolve_round(p_move):
        """Player has revealed — score the already-committed bot move."""
        nonlocal botScore, playerScore, revealed, round_num, game_phase, resultsStart
        nonlocal bot_choice, commitment_hash, commitment_seed, countdownActive, CountdownPlayerMove, countdownStart
        nonlocal revealStart, revealDuration

        bot.record_round(player_move=p_move, bot_move=bot_choice)
        last = bot.history[-1]
        if last["result"] == "loss":
            botScore += 1
        elif last["result"] == "win":
            playerScore += 1

        revealed = True
        revealStart = pygame.time.get_ticks()
        countdownActive = False
        round_num += 1

        # If 10 rounds finished go to results
        if len(bot.history) >= max_rounds:
            game_phase = "results"
            resultsStart = pygame.time.get_ticks()

    # Main loop
    try:
        while True:
            draw_background(screen)

            # Layout
            draw_game_header(screen)
            scoreboard   = pygame.Rect(0, 100, WIDTH, 100)
            padding      = 20
            botSection   = pygame.Rect(padding, 120, WIDTH // 2 - 30, HEIGHT - 180)
            playerSection = pygame.Rect(WIDTH // 2 + 10, 120, WIDTH // 2 - 30, HEIGHT - 180)

            # Camera
            ok = False
            gesture_name = "No hand"
            camera_surface = None

            # Draw sections
            draw_card(screen, botSection)
            draw_card(screen, playerSection)

            botInner = pygame.Rect(
                botSection.left + 30,
                botSection.top + 95,
                botSection.width - 60,
                botSection.height - 165
            )
            playerInner = pygame.Rect(
                playerSection.left + 30,
                playerSection.top + 95,
                playerSection.width - 60,
                playerSection.height - 165
            )
            cameraRect = playerInner

            draw_inner_panel(screen, botInner)
            draw_inner_panel(screen, playerInner)

            if USE_CAMERA and camera is not None:
                ok, frame = camera.read()
                if ok:
                    processed_frame, gesture_name = detect_gesture(frame)
                    camera_surface = cv2_to_pygame(
                        processed_frame,
                        playerSection.width - 40,
                        playerSection.height - 140
                    )

            # Bot label
            botLabel = labelFont.render("bot", True, ACCENT_RED)
            botLabel_rect = botLabel.get_rect(center=(botSection.centerx, botSection.top + 40))
            screen.blit(botLabel, botLabel_rect)

            # Bot mode selection instructions
            if game_phase == "select_bot":
                choose1 = smallFont.render("Choose bot mode", True, TEXT_BRIGHT)
                choose2 = smallFont.render("ROCK = Random Bot", True, ACCENT_RED)
                choose3 = smallFont.render("PAPER = Strategic Bot", True, ACCENT_PURPLE)

                screen.blit(choose1, choose1.get_rect(center=(botSection.centerx, botSection.centery - 50)))
                screen.blit(choose2, choose2.get_rect(center=(botSection.centerx, botSection.centery)))
                screen.blit(choose3, choose3.get_rect(center=(botSection.centerx, botSection.centery + 50)))

                if gesture_name == "Rock":
                    choose_bot_mode("random")
                elif gesture_name == "Paper":
                    choose_bot_mode("trained")


            # Bot move image — only shown AFTER the reveal
            if game_phase == "playing" and revealed and bot_choice in bot_images:
                img = bot_images[bot_choice]
                img_rect = img.get_rect(center=(botSection.centerx, botSection.centery + 20))
                screen.blit(img, img_rect)

            # Reveals player move
            if game_phase == "playing" and countdownActive:
                elapsed = pygame.time.get_ticks() - countdownStart
                remaining = countdownDuration - (elapsed // 1000)

                if remaining > 0:
                    countdownText = titleFont.render(str(remaining), True, ACCENT_RED)
                    countdownRect = countdownText.get_rect(
                        center=(botSection.centerx, botSection.centery + 20)
                    )
                    screen.blit(countdownText, countdownRect)
                else:
                    # Countdown finished — resolve the round
                    if CountdownPlayerMove is not None:
                        resolve_round(CountdownPlayerMove)
                    else:
                        p_move = gesture_to_move(gesture_name)
                        if p_move:
                            resolve_round(p_move)
                        else:
                            print("[INFO] No valid gesture detected at countdown end")

            # Show last round result (only after reveal)
            if game_phase == "playing" and revealed and bot.history:
                last = bot.history[-1]
                result_map = {
                    "win": "YOU WIN!",
                    "loss": "BOT WINS!",
                    "tie": "DRAW!"
                }
                result_text = smallFont.render(result_map[last["result"]], True, BLACK)
                result_rect = result_text.get_rect(center=(botSection.centerx, botSection.bottom - 55))
                screen.blit(result_text, result_rect)

                if pygame.time.get_ticks() - revealStart > revealDuration:
                    if game_phase == "playing":
                        revealed = False
                        start_round()

            # Player label
            playerLabel = labelFont.render("player", True, ACCENT_PURPLE)
            playerLabel_rect = playerLabel.get_rect(center=(playerSection.centerx, playerSection.top + 40))
            screen.blit(playerLabel, playerLabel_rect)

            # Camera feed in player section
            if camera_surface is not None:
                screen.blit(camera_surface, cameraRect)

            # Gesture text
            gestureText = smallFont.render(f"{gesture_name.lower()}", True, ACCENT_GREEN) # Rip 30 minutes whiteonwhite Dx
            gestureText_rect = gestureText.get_rect(center=(playerSection.centerx, playerSection.bottom - 25))
            screen.blit(gestureText, gestureText_rect)

            # Keyboard hint (shown when camera is off)
            if not USE_CAMERA:
                hintText = smallFont.render("No camera — use R / P / S keys to play", True, BLACK)
                hintRect = hintText.get_rect(center=(playerSection.centerx, playerSection.centery))
                screen.blit(hintText, hintRect)

            # Final results screen after max rounds reached
            if game_phase == "results":
                result1 = titleFont.render("Final Results", True, ACCENT_RED)
                result2 = smallFont.render(f"Bot: {botScore}   Player: {playerScore}", True, TEXT_BRIGHT)

                if playerScore > botScore:
                    winner = "Player wins!"
                elif botScore > playerScore:
                    winner = "Bot wins!"
                else:
                    winner = "Draw!"

                result3 = smallFont.render(winner, True, ACCENT_PURPLE)

                screen.blit(result1, result1.get_rect(center=(botSection.centerx, botSection.centery - 60)))
                screen.blit(result2, result2.get_rect(center=(botSection.centerx, botSection.centery)))
                screen.blit(result3, result3.get_rect(center=(botSection.centerx, botSection.centery + 50)))

                if pygame.time.get_ticks() - resultsStart > 4000:
                    reset_match()
                    bot = None
                    difficulty = "Choose"
                    game_phase = "select_bot"

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    raise KeyboardInterrupt

                if event.type == pygame.KEYDOWN:

                    if game_phase == "select_bot":
                        if event.key == pygame.K_r:
                            choose_bot_mode("random")

                        elif event.key == pygame.K_t:
                            choose_bot_mode("trained")

                    # elif game_phase == "playing":
                    #     if event.key == pygame.K_SPACE and USE_CAMERA and not countdownActive:
                    #         start_round(forced_move=None)

                    #     elif event.key == pygame.K_r and not countdownActive:
                    #         start_round(forced_move="R")

                    #     elif event.key == pygame.K_p and not countdownActive:
                    #         start_round(forced_move="P")

                    #     elif event.key == pygame.K_s and not countdownActive:
                    #         start_round(forced_move="S")

                    if event.key == pygame.K_ESCAPE:
                        reset_match()
                        bot = None
                        difficulty = "Choose"
                        game_phase = "select_bot"

            validationText = hashFont.render(draw_fairness(), True, WHITE)
            validationRect = validationText.get_rect(center=(WIDTH // 2, HEIGHT - 20))
            validationsShadow = hashFont.render("Game Validity", True, ACCENT_ORANGE)
            validationsShadowRect = validationsShadow.get_rect(center=(WIDTH // 2 + 2, HEIGHT - 18))
            screen.blit(validationsShadow, validationsShadowRect)
            screen.blit(validationText, validationRect)
            pygame.display.update()
            clock.tick(20)

    except KeyboardInterrupt:
        pass

    if camera is not None:
        camera.release()
    pygame.quit()


# Direct-run entry point. Until the selection screen exists, flip
# USE_RANDOM_BOT at the top of this file to switch between bots.
# Once the selection screen is wired, it will call run_game(StrategicBot())
# or run_game(RandomBot()) directly.
if __name__ == "__main__":
    bot = RandomBot() if USE_RANDOM_BOT else StrategicBot()
    run_game(bot)
    sys.exit()
