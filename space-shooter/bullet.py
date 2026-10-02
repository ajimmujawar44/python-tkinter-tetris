"""
Space Shooter - Bullet / Projectile System
Handles player and enemy laser projectiles with velocity and bounds tracking.
"""

import pygame
from settings import (
    SCREEN_HEIGHT,
    BULLET_SPEED,
    BULLET_DAMAGE,
    BULLET_SIZE,
    COLOR_CYAN,
    COLOR_WHITE,
)


class Bullet(pygame.sprite.Sprite):
    """Energy projectile fired by spaceships."""

    def __init__(
        self,
        x: int,
        y: int,
        speed_y: float = -BULLET_SPEED,
        damage: int = BULLET_DAMAGE,
        is_enemy: bool = False,
        image: pygame.Surface = None,
    ):
        super().__init__()
        self.damage = damage
        self.is_enemy = is_enemy
        self.speed_y = speed_y

        if image:
            self.image = image
        else:
            w, h = BULLET_SIZE
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            fill_color = (255, 60, 60) if is_enemy else COLOR_CYAN
            pygame.draw.ellipse(self.image, fill_color, (0, 0, w, h))
            pygame.draw.ellipse(self.image, COLOR_WHITE, (1, 1, w - 2, h - 2))

        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        """Move bullet vertically and kill if beyond screen bounds."""
        self.rect.y += int(self.speed_y)
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()
