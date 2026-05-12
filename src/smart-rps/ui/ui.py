# Using Pygame CE (Community Edition) - is actively maintained
# Better support for windows + raspberry pi

import sys, pygame
pygame.init()

# Active window
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Rock Paper Scissors")
clock = pygame.time.Clock()

# Images in memory = pygame surfaces

# colours & fonts
BACKGROUND = (250, 246, 235) 
PANEL = (255, 255, 255)
PANEL_EDGE = (225, 190, 95)

ACCENT_BLUE = (65, 140, 255)
ACCENT_RED = (235, 85, 95)
ACCENT_GOLD = (235, 180, 55)

TEXT_BRIGHT = (35, 32, 28)
TEXT_DIM = (120, 105, 80)
WHITE = (255, 255, 255)
BLACK = (35, 32, 28)

font_title  = pygame.font.SysFont("bahnschrift", 48, bold=True)
font_label  = pygame.font.SysFont("bahnschrift", 32, bold=True)
font_body   = pygame.font.SysFont("bahnschrift", 23)
font_small  = pygame.font.SysFont("bahnschrift", 18)
font_result = pygame.font.SysFont("bahnschrift", 34, bold=True)

def drawCard(surface, rect, fill=PANEL, radius=22):
    shadow = rect.copy()
    shadow.x += 7
    shadow.y += 7
    pygame.draw.rect(surface, (215, 185, 115), shadow, border_radius=radius)

    pygame.draw.rect(surface, fill, rect, border_radius=radius)
    pygame.draw.rect(surface, PANEL_EDGE, rect, width=2, border_radius=radius)

def draw_header_bar(surface):
    header = pygame.Rect(0, 0, WIDTH, 105)
    pygame.draw.rect(surface, (255, 250, 235), header)

    pygame.draw.line(surface, (255, 220, 120), (30, 102), (WIDTH - 30, 102), 6)
    pygame.draw.line(surface, ACCENT_GOLD, (30, 102), (WIDTH - 30, 102), 2)


# State
botScore = 0
playerScore = 0
difficulty = "Medium"
playerGesture = "No hand"
botGesture = "No hand"

try:
    while True:
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = 8
            g = int(10 + ratio * 12)
            b = int(18 + ratio * 20)
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

        # Layout
        scoreboard = pygame.Rect(0, 0, WIDTH, 100)
        padding = 20
        botSection = pygame.Rect(padding, 120, WIDTH // 2 - 30, HEIGHT - 140)
        playerSection = pygame.Rect(WIDTH // 2 + 10, 120, WIDTH // 2 - 30, HEIGHT - 140)    


        # Draw sections
        draw_header_bar(screen)
        drawCard(screen, botSection)
        drawCard(screen, playerSection)

        # Scoreboard 
        titleText = font_title.render("SMART RPS", True, TEXT_BRIGHT)
        screen.blit(titleText, (35, 28))

        scoreboardText = font_label.render(
            f"Bot {botScore}  :  {playerScore} Player",
            True,
            TEXT_BRIGHT
        )    
        scoreboardText_rect = scoreboardText.get_rect(center=(WIDTH // 2, 52))
        screen.blit(scoreboardText, scoreboardText_rect)

        modeText = font_body.render(f"Mode: {difficulty}", True, ACCENT_GOLD)
        modeText_rect = modeText.get_rect(midright=(WIDTH - 35, 54))
        screen.blit(modeText, modeText_rect)


        # Bot and player 
        botLabel = font_label.render("BOT", True, ACCENT_RED)
        botLabel_rect = botLabel.get_rect(center=(botSection.centerx, botSection.top + 40))
        screen.blit(botLabel, botLabel_rect)

        playerLabel = font_label.render("PLAYER", True, ACCENT_BLUE)
        playerLabel_rect = playerLabel.get_rect(center=(playerSection.centerx, playerSection.top + 40))
        screen.blit(playerLabel, playerLabel_rect)

        # Gesture text
        gestureText = font_small.render(f"{playerGesture}", True, WHITE)
        gestureText_rect = gestureText.get_rect(center=(playerSection.centerx, playerSection.bottom - 25))
        screen.blit(gestureText, gestureText_rect)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt

        pygame.display.update()
        clock.tick(20)

except KeyboardInterrupt:
    pass

    pygame.quit()
    sys.exit()

