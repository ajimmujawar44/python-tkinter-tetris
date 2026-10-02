"""
Space Shooter - Visual Effects & Particles
Provides particle explosion sparks, engine thruster trails, floating score indicators,
and a multi-layer parallax scrolling starfield.
"""

import math
import random
import pygame
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    STAR_LAYERS,
    COLOR_CYAN,
    COLOR_ORANGE,
    COLOR_YELLOW,
    COLOR_WHITE,
)


class Starfield:
    """Multi-depth parallax scrolling starfield background."""

    def __init__(self, width: int = SCREEN_WIDTH, height: int = SCREEN_HEIGHT):
        self.width = width
        self.height = height
        self.stars = []

        for layer in STAR_LAYERS:
            for _ in range(layer["count"]):
                star = {
                    "x": random.uniform(0, self.width),
                    "y": random.uniform(0, self.height),
                    "speed": layer["speed"],
                    "radius": layer["radius"],
                    "color": layer["color"],
                }
                self.stars.append(star)

    def update(self):
        """Scroll stars downward with seamless wrapping."""
        for star in self.stars:
            star["y"] += star["speed"]
            if star["y"] >= self.height:
                star["y"] = 0
                star["x"] = random.uniform(0, self.width)

    def draw(self, surface: pygame.Surface):
        """Render stars onto target surface."""
        for star in self.stars:
            x = int(star["x"])
            y = int(star["y"])
            r = star["radius"]
            if r <= 1:
                surface.set_at((x, y), star["color"])
            else:
                pygame.draw.circle(surface, star["color"], (x, y), r)


class SparkParticle(pygame.sprite.Sprite):
    """Kinetic glowing particle for explosions and impacts."""

    def __init__(self, x: float, y: float, color: tuple, speed_mult: float = 1.0):
        super().__init__()
        self.x = x
        self.y = y
        self.color = color

        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 6.0) * speed_mult
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        self.radius = random.uniform(2.0, 4.5)
        self.decay = random.uniform(0.08, 0.16)
        self.alpha = 255.0
        self.lifetime = 1.0

        self.image = pygame.Surface((int(self.radius * 2 + 2), int(self.radius * 2 + 2)), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.94  # Slight space drag
        self.vy *= 0.94
        self.lifetime -= self.decay
        self.radius = max(0.5, self.radius - 0.06)

        if self.lifetime <= 0 or self.radius <= 0.8:
            self.kill()
        else:
            self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface: pygame.Surface):
        if self.lifetime > 0 and self.radius > 0:
            alpha_int = max(0, min(255, int(self.lifetime * 255)))
            color_with_alpha = (*self.color[:3], alpha_int)
            size = int(self.radius * 2 + 2)
            temp_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, color_with_alpha, (size // 2, size // 2), int(self.radius))
            surface.blit(temp_surf, (int(self.x - size // 2), int(self.y - size // 2)))


class ThrusterParticle(pygame.sprite.Sprite):
    """Engine exhaust particle trailing behind the player spaceship."""

    def __init__(self, x: float, y: float):
        super().__init__()
        self.x = x + random.uniform(-2, 2)
        self.y = y
        self.vx = random.uniform(-0.6, 0.6)
        self.vy = random.uniform(2.5, 5.0)

        # Gradient from white/cyan core to orange/yellow tip
        self.color = random.choice([COLOR_CYAN, COLOR_WHITE, COLOR_YELLOW, COLOR_ORANGE])
        self.radius = random.uniform(2.0, 3.8)
        self.lifetime = 1.0
        self.decay = random.uniform(0.07, 0.14)

        self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= self.decay
        self.radius = max(0.5, self.radius - 0.12)

        if self.lifetime <= 0 or self.radius <= 0.8:
            self.kill()
        else:
            self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface: pygame.Surface):
        if self.lifetime > 0:
            alpha_int = max(0, min(255, int(self.lifetime * 255)))
            size = int(self.radius * 2 + 2)
            temp_surf = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(temp_surf, (*self.color[:3], alpha_int), (size // 2, size // 2), int(self.radius))
            surface.blit(temp_surf, (int(self.x - size // 2), int(self.y - size // 2)))


class FloatingText(pygame.sprite.Sprite):
    """Floating combat text notification (e.g. '+100', 'SHIELD CRITICAL')."""

    def __init__(self, x: int, y: int, text: str, color: tuple, font: pygame.font.Font):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.vy = -1.2
        self.lifetime = 1.0
        self.decay = 0.025
        self.text = text
        self.color = color
        self.font = font

        self.rendered_text = self.font.render(self.text, True, self.color)
        self.shadow_text = self.font.render(self.text, True, (10, 10, 20))
        self.rect = self.rendered_text.get_rect(center=(int(self.x), int(self.y)))

    def update(self):
        self.y += self.vy
        self.lifetime -= self.decay
        if self.lifetime <= 0:
            self.kill()
        else:
            self.rect.center = (int(self.x), int(self.y))

    def draw(self, surface: pygame.Surface):
        if self.lifetime > 0:
            alpha = max(0, min(255, int(self.lifetime * 255)))
            surf = pygame.Surface((self.rect.width + 4, self.rect.height + 4), pygame.SRCALPHA)
            # Render shadow
            shadow_copy = self.shadow_text.copy()
            shadow_copy.set_alpha(alpha)
            surf.blit(shadow_copy, (2, 2))
            # Render main text
            text_copy = self.rendered_text.copy()
            text_copy.set_alpha(alpha)
            surf.blit(text_copy, (0, 0))

            surface.blit(surf, (self.rect.x, self.rect.y))
