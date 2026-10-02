"""
Space Shooter - Main Application Entry Point
Initializes Pygame display, drives the primary event & render loop, and handles clean exit.
"""

import sys
import pygame
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    GAME_TITLE,
)
from game import Game


def main():
    """Main execution function for Space Shooter."""
    # Initialize core Pygame modules
    pygame.init()

    # Create the display window
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(GAME_TITLE)

    # Initialize master game controller
    game = Game(screen)

    # Optional: set window icon from generated player sprite
    try:
        icon = game.assets.get_image("player")
        if icon:
            pygame.display.set_icon(icon)
    except Exception:
        pass

    clock = pygame.time.Clock()
    running = True

    # Main Game Loop
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.handle_event(event)

        # Logic Update
        game.update()

        # Render Frame
        game.draw()

        # Refresh Screen
        pygame.display.flip()

        # Regulate Frame Rate
        clock.tick(FPS)

    # Clean shutdown
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
