# Using Pygame CE (Community Edition) - is actively maintained
# Better support for windows + raspberry pi

import sys
import os
import cv2
import mediapipe as mp
import pygame

# ── Toggle this to switch between camera and keyboard-only mode ──
USE_CAMERA = True

# Bot import
try:
    from bot.bot import RPSBot
except ImportError:
    from bot import RPSBot

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

ACCENT_BLUE = (85, 150, 175) 
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

# Bot + game state
bot = RPSBot()
bot_choice = None
player_choice = None  # 'R', 'P', 'S' — from camera or keyboard fallback
botScore = 0
playerScore = 0
difficulty = "Easy"

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

    mode_text = smallFont.render(f"mode: {difficulty}", True, ACCENT_GREEN)
    surface.blit(mode_text, mode_text.get_rect(midright=(WIDTH - 40, 95)))


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


def play_round(p_move):
    """Trigger a full round: bot plays, scores update, history recorded."""
    global bot_choice, botScore, playerScore

    player_choice = p_move

    bot_choice = bot.next_move()
    bot.record_round(player_move=p_move, bot_move=bot_choice)

    last = bot.history[-1]
    if last["result"] == "loss":   # player lost = bot won
        botScore += 1
    elif last["result"] == "win":
        playerScore += 1


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
        botLabel = labelFont.render("BOT", True, ACCENT_RED)
        botLabel_rect = botLabel.get_rect(center=(botSection.centerx, botSection.top + 40))
        screen.blit(botLabel, botLabel_rect)

        # Bot move image (show after a round has been played)
        if bot_choice is not None and bot_choice in bot_images:
            img = bot_images[bot_choice]
            img_rect = img.get_rect(center=(botSection.centerx, botSection.centery + 20))
            screen.blit(img, img_rect)

        # Show last round result
        if bot.history:
            last = bot.history[-1]
            result_map = {
                "win": "YOU WIN!",
                "loss": "BOT WINS!",
                "tie": "DRAW!"
            }
            result_text = smallFont.render(result_map[last["result"]], True, BLACK)
            result_rect = result_text.get_rect(center=(botSection.centerx, botSection.bottom - 25))
            screen.blit(result_text, result_rect)

        # Player label
        playerLabel = labelFont.render("PLAYER", True, ACCENT_BLUE)
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

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt

            if event.type == pygame.KEYDOWN:

                # SPACE — play a round using camera gesture (only with camera)
                if event.key == pygame.K_SPACE and USE_CAMERA:
                    p_move = gesture_to_move(gesture_name)
                    if p_move:
                        play_round(p_move)
                    else:
                        print("[INFO] No valid gesture detected — hold your hand in the box first.")

                # Keyboard fallback: R / P / S
                elif event.key == pygame.K_r:
                    play_round("R")
                elif event.key == pygame.K_p:
                    play_round("P")
                elif event.key == pygame.K_s:
                    play_round("S")

                # Reset game
                elif event.key == pygame.K_ESCAPE:
                    bot.reset()
                    bot_choice = None
                    botScore = 0
                    playerScore = 0

        pygame.display.update()
        clock.tick(20)

except KeyboardInterrupt:
    pass

    pygame.quit()
    sys.exit()