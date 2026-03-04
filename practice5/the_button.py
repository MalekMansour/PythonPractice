import pygame
import sys

pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Button")

# Colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)

# Button settings
button_width = 200
button_height = 100
button_rect = pygame.Rect(
    WIDTH // 2 - button_width // 2,
    HEIGHT // 2 - button_height // 2,
    button_width,
    button_height
)

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Detect button click (does nothing)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                pass  # Button does nothing

    screen.fill(WHITE)

    # Draw button
    pygame.draw.rect(screen, RED, button_rect)

    pygame.display.flip()
    clock.tick(60)
