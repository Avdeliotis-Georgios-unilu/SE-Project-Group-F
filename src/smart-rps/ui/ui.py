# Using Pygame CE (Community Edition) - is actively maintained
# Better support for windows + raspberry pi

import sys
import cv2
import mediapipe as mp
import pygame

pygame.init()

# Camera + hand detection
camera = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hand_detector = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

# Active window
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Rock Paper Scissors")

# Images in memory = pygame surfaces

# colours
BG = (30, 40, 60)  
TEXT_LIGHT = (240, 240, 240)
BOT_BG = (60, 130, 90)     
PLAYER_BG = (70, 100, 170) 
DIVIDER = (100, 100, 120)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)    

titleFont = pygame.font.SysFont(None, 44)
labelFont = pygame.font.SysFont(None, 36)
smallFont = pygame.font.SysFont(None, 28)

# Headers
botScore = 0
playerScore = 0
difficulty = "Easy"

clock = pygame.time.Clock()

def detect_gesture(frame):
    image = cv2.flip(frame, 1)

    image_height, image_width, _ = image.shape

    square_size = 300
    square_x1 = image_width // 2 - square_size // 2
    square_y1 = image_height // 2 - square_size // 2
    square_x2 = square_x1 + square_size
    square_y2 = square_y1 + square_size

    cv2.rectangle(image, (square_x1, square_y1), (square_x2, square_y2), (0, 255, 0), 2)

    hand_area = image[square_y1:square_y2, square_x1:square_x2]
    hand_area_rgb = cv2.cvtColor(hand_area, cv2.COLOR_BGR2RGB)

    result = hand_detector.process(hand_area_rgb)

    gesture_name = "No hand"

    if result.multi_hand_landmarks:
        for one_hand in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(hand_area, one_hand, mp_hands.HAND_CONNECTIONS)

            points = one_hand.landmark

            index_up = points[8].y < points[6].y
            middle_up = points[12].y < points[10].y
            ring_up = points[16].y < points[14].y
            pinky_up = points[20].y < points[18].y

            if not index_up and not middle_up and not ring_up and not pinky_up:
                gesture_name = "Rock"
            elif index_up and middle_up and ring_up and pinky_up:
                gesture_name = "Paper"
            elif index_up and middle_up and not ring_up and not pinky_up:
                gesture_name = "Scissors"
            else:
                gesture_name = "Unknown"

    return image, gesture_name

def cv2_to_pygame(frame, width, height):
    """
    Converts an OpenCV frame into a Pygame surface.
    """
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb = cv2.resize(frame_rgb, (width, height))
    surface = pygame.image.frombuffer(frame_rgb.tobytes(), (width, height), "RGB")
    return surface

try:
    while True:
        screen.fill(BG)

        # Layout
        scoreboard = pygame.Rect(0, 0, WIDTH, 100)
        padding = 20
        botSection = pygame.Rect(padding, 120, WIDTH // 2 - 30, HEIGHT - 140)
        playerSection = pygame.Rect(WIDTH // 2 + 10, 120, WIDTH // 2 - 30, HEIGHT - 140)    

        # Read camera frame
        ok, frame = camera.read()
        gesture_name = "No hand"
        camera_surface = None

        if ok:
            processed_frame, gesture_name = detect_gesture(frame)
            camera_surface = cv2_to_pygame(
                processed_frame,
                playerSection.width - 40,
                playerSection.height - 140
            )

        # Draw sections
        pygame.draw.rect(screen, BG, scoreboard)
        pygame.draw.rect(screen, WHITE, botSection, border_radius=20)
        pygame.draw.rect(screen, WHITE, playerSection, border_radius=20)
        pygame.draw.rect(screen, DIVIDER, botSection, width=2, border_radius=20)
        pygame.draw.rect(screen, DIVIDER, playerSection, width=2, border_radius=20)


        # Scoreboard 
        scoreboardText = titleFont.render(
            f"SMART RPS           |          Bot: {botScore}   Player: {playerScore}        |         Mode: {difficulty}",
            True,
            TEXT_LIGHT
        )    
        scoreboardText_rect = scoreboardText.get_rect(center=scoreboard.center)
        screen.blit(scoreboardText, scoreboardText_rect)


        # Bot and player 
        botLabel = labelFont.render(f"Bot: {botScore}", True, BLACK)
        botLabel_rect = botLabel.get_rect(center=(botSection.centerx, botSection.top + 40))
        screen.blit(botLabel, botLabel_rect)

        playerLabel = labelFont.render(f"Player: {playerScore}", True, BLACK)
        playerLabel_rect = playerLabel.get_rect(center=(playerSection.centerx, playerSection.top + 40))
        screen.blit(playerLabel, playerLabel_rect)

        # Camera feed in player section
        if camera_surface is not None:
            screen.blit(camera_surface, (playerSection.x + 20, playerSection.y + 80))

        # Gesture text
        gestureText = smallFont.render(f"Gesture: {gesture_name}", True, BLACK)
        gestureText_rect = gestureText.get_rect(center=(playerSection.centerx, playerSection.bottom - 25))
        screen.blit(gestureText, gestureText_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt

        pygame.display.update()
        clock.tick(20)

except KeyboardInterrupt:
    pass

finally:
    camera.release()
    hand_detector.close()
    pygame.quit()
    sys.exit()

