# Using Pygame CE (Community Edition) - is actively maintained
# Better support for windows + raspberry pi

import sys
import os
import cv2
import mediapipe as mp
import pygame

USE_CAMERA = False  # Set to False to disable camera

# Bot import
try:
    from bot.bot import RPSBot
except ImportError:
    from bot import RPSBot

import fairness

pygame.init()

# Active window
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Rock Paper Scissors")
clock = pygame.time.Clock()

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

titleFont = pygame.font.SysFont("verdana", 46, bold=True)
labelFont = pygame.font.SysFont("verdana", 30, bold=True)
smallFont = pygame.font.SysFont("verdana", 24)
hashFont = pygame.font.SysFont("verdana", 16, bold=True)

# Load images
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
bot = RPSBot()
bot_choice = None
player_choice = None  # 'R', 'P', 'S' — from camera or keyboard fallback
botScore = 0
playerScore = 0
difficulty = "Choose"  # for later, maybe add difficulty selection in UI?

#Starting game
max_rounds = 10
round_num = 1            # for later
revealed = False         # True after the player played the round
game_phase = "select bot"
selected_bot = None
round_delay = 1000
last_round_time = 0

countdownActive = False
countdownStart = 0
countdownDuration = 3
CountdownPlayerMove = None

# Fairness state
commitment_hash = None
commitment_seed = None

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

    # Bot mode text on screen
    surface.blit(signpost, (WIDTH - 290, -20))
    mode_text = smallFont.render(difficulty, True, ACCENT_GREEN)
    mode_rect = mode_text.get_rect(center=(WIDTH - 110, 60))
    surface.blit(mode_text, mode_rect)

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
            g = int(BACKGROUND_2[1] * (1 - blend) + BACKGROUND_3[1] * blend)
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


def gesture_to_move(gesture_name):
    """Convert gesture string to R/P/S code."""
    return {"Rock": "R", "Paper": "P", "Scissors": "S"}.get(gesture_name)


def cv2_to_pygame(frame, width, height):
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb = cv2.resize(frame_rgb, (width, height))
    return pygame.image.frombuffer(frame_rgb.tobytes(), (width, height), "RGB")


def draw_fairness():
    if commitment_hash is None:
        return "Game Validity"
    return f"{commitment_hash}"


def start_round(forced_move=None):
    """Bot commits its move BEFORE the player reveals. Starts the countdown."""
    global bot_choice, commitment_hash, commitment_seed
    global countdownActive, countdownStart, CountdownPlayerMove, revealed

    bot_choice = bot.next_move()
    commitment_hash, commitment_seed = fairness.commit(bot_choice)
    CountdownPlayerMove = forced_move
    countdownActive = True
    countdownStart = pygame.time.get_ticks()
    revealed = False


def resolve_round(p_move):
    """Player has revealed — score the already-committed bot move."""
    global botScore, playerScore, revealed, round_num
    global game_phase, selected_bot, difficulty, last_round_time

    bot.record_round(player_move=p_move, bot_move=bot_choice)
    last = bot.history[-1]
    if last["result"] == "loss":
        botScore += 1
    elif last["result"] == "win":
        playerScore += 1

    revealed = True
    round_num += 1

    if len(bot.history) >= max_rounds:
        reset_game()
        selected_bot = None
        difficulty = "choose"
        game_phase = "select bot"
        last_round_time = pygame.time.get_ticks()

def choose_bot_mode(move):
    global selected_bot, difficulty, game_phase
    if move == "P":
        selected_bot = "strategic bot"
        difficulty = "strategic bot"
        game_phase = "play"
        reset_game()
    elif move == "R":
        selected_bot = "random bot"
        difficulty = "random bot"
        game_phase = "play"
        reset_game()
    

def reset_game():
    global bot_choice, player_choice, botScore, playerScore
    global commitment_hash, commitment_seed, revealed, round_num
    global countdownActive

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

        if game_phase == "select bot":
            chooseText1 = smallFont.render("Select bot mode", True, TEXT_BRIGHT)
            chooseText2 = smallFont.render("Show PAPER to play with the strategic bot", True, ACCENT_PURPLE)
            chooseText3 = smallFont.render("Show SCISSORS to play with the random bot", True, ACCENT_RED)

            screen.blit(chooseText1, chooseText1.get_rect(center=(botSection.centerx, botSection.centery - 50)))
            screen.blit(chooseText2, chooseText2.get_rect(center=(botSection.centerx, botSection.centery)))
            screen.blit(chooseText3, chooseText3.get_rect(center=(botSection.centerx, botSection.centery + 50)))

        # Bot move image — only shown AFTER the reveal
        if revealed and bot_choice in bot_images:
            img = bot_images[bot_choice]
            img_rect = img.get_rect(center=(botSection.centerx, botSection.centery + 20))
            screen.blit(img, img_rect)

        # Reveals player move
        if countdownActive:
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
                countdownActive = False

        # Show last round result (only after reveal)
        if revealed and bot.history:
            last = bot.history[-1]
            result_map = {
                "win": "YOU WIN!",
                "loss": "BOT WINS!",
                "tie": "DRAW!"
            }
            result_text = smallFont.render(result_map[last["result"]], True, BLACK)
            result_rect = result_text.get_rect(center=(botSection.centerx, botSection.bottom - 55))
            screen.blit(result_text, result_rect)


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

        # move = bot choice
        current_move = gesture_to_move(gesture_name)
        if game_phase == "select bot":
            if current_move == "P":
                choose_bot_mode("P")
                selected_bot = "strategic bot"
                difficulty = "Strategic"
                reset_game()
                game_phase = "play"
                last_round_time = pygame.time.get_ticks()

            elif current_move == "S":
                selected_bot = "random"
                difficulty = "Random"
                reset_game()
                game_phase = "play"
                last_round_time = pygame.time.get_ticks()

        if game_phase == "play" and not countdownActive:
            now = pygame.time.get_ticks()
            if now - last_round_time > round_delay:
                start_round()
                last_round_time = now

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    reset_game()
                    selected_bot = None
                    difficulty = "Choose"
                    game_phase = "select bot"

                # SPACE — camera mode: bot commits, player reveals at countdown end
                if event.key == pygame.K_SPACE and USE_CAMERA and not countdownActive:
                    start_round(forced_move=None)

                # Keyboard fallback: R / P / S
                elif event.key == pygame.K_r and not countdownActive:
                    start_round(forced_move="R")
                elif event.key == pygame.K_p and not countdownActive:
                    start_round(forced_move="P")
                elif event.key == pygame.K_s and not countdownActive:
                    start_round(forced_move="S")

                # Reset game
                elif event.key == pygame.K_ESCAPE:
                    bot.reset()
                    bot_choice = None
                    botScore = 0
                    playerScore = 0
                    commitment_hash = None
                    commitment_seed = None
                    revealed = False
                    round_num = 1
                    countdownActive = False


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

    pygame.quit()
    sys.exit()