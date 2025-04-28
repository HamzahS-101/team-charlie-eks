import sys

import game
import pygame
import settings as st
from utils import button

pygame.init()

# Define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


def main():
    width, height = st.WINDOW_WIDTH, st.WINDOW_HEIGHT
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    start_pos = (width // 2, height // 2 - 50)
    end_pos = (width // 2, height // 2 + 50)
    button_size = (200, 50)
    win_text = ""

    while True:
        screen.fill(BLACK)

        # Display game name
        font = pygame.font.SysFont("Arial", 80)
        text_render = font.render("Mining Mazers", True, WHITE)
        screen.blit(text_render, (width // 2 - text_render.get_width() // 2, 50))

        #  Display win text
        font = pygame.font.SysFont("Arial", 50)
        text_render = font.render(win_text, True, WHITE)
        screen.blit(text_render, (width // 2 - text_render.get_width() // 2, 150))

        # Buttons
        start_button = button(screen, "Start", start_pos, button_size, 40, WHITE, GREEN)
        exit_button = button(screen, "Exit", end_pos, button_size, 40, WHITE, RED)

        mouse = pygame.mouse.get_pos()

        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(mouse):
                    win_text = game.main() or ""
                if exit_button.collidepoint(mouse):
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
