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

while True:
    screen.fill(BG)

    # Layout
    scoreboard = pygame.Rect(0, 0, WIDTH, 100)
    padding = 20
    botSection = pygame.Rect(padding, 120, WIDTH // 2 - 30, HEIGHT - 140)
    playerSection = pygame.Rect(WIDTH // 2 + 10, 120, WIDTH // 2 - 30, HEIGHT - 140)    


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
    botLabel = labelFont.render(
        f"Bot: {botScore}", True, BLACK
    )
    botLabel_rect = botLabel.get_rect(center=(botSection.centerx, botSection.top + 40))
    screen.blit(botLabel, botLabel_rect)

    playerLabel = labelFont.render(
        f"Player: {playerScore}", True, BLACK
    )
    playerLabel_rect = playerLabel.get_rect(
        center=(playerSection.centerx, playerSection.top + 40)
    )
    screen.blit(playerLabel, playerLabel_rect)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
 
    pygame.display.update()
    clock.tick(60)  

