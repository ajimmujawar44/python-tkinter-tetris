"""
Space Shooter - Enemy Entity & Spawn Manager
Implements enemy spaceships with distinct flight patterns (Scout, Interceptor, Cruiser),
damage mechanics, particle explosions, and dynamic difficulty scaling.
"""

import math
import random
import pygame
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ENEMY_TYPES,
    ENEMY_SPAWN_INTERVAL_BASE_MS,
    ENEMY_SPAWN_INTERVAL_MIN_MS,
    COLOR_ORANGE,
    COLOR_RED,
    COLOR_YELLOW,
)
from particles import SparkParticle


class Enemy(pygame.sprite.Sprite):
    """Enemy spaceship with movement pattern and combat stats."""

    def __init__(
        self,
        enemy_type: str,
        asset_manager,
        particle_group,
        speed_multiplier: float = 1.0,
    ):
        super().__init__()
        self.enemy_type = enemy_type
        self.asset_manager = asset_manager
        self.particle_group = particle_group
        self.config = ENEMY_TYPES.get(enemy_type, ENEMY_TYPES["scout"])

        # Visuals
        self.image = self.asset_manager.get_image(enemy_type)
        if self.image is None:
            w, h = self.config["size"]
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, self.config["color"], [(w // 2, h - 2), (w - 2, 2), (2, 2)])

        self.rect = self.image.get_rect()

        # Spawn Position (randomized above screen top)
        margin = self.rect.width // 2 + 10
        self.center_x = float(random.randint(margin, SCREEN_WIDTH - margin))
        self.pos_y = float(random.randint(-70, -40))
        self.rect.centerx = int(self.center_x)
        self.rect.centery = int(self.pos_y)

        # Stats
        self.health = self.config["health"]
        self.max_health = self.config["health"]
        self.speed = self.config["speed"] * speed_multiplier
        self.score_value = self.config["score_value"]
        self.pattern = self.config["pattern"]

        # Pattern kinematics
        self.spawn_time = pygame.time.get_ticks()
        self.wave_amplitude = random.uniform(35, 75)
        self.wave_frequency = random.uniform(2.5, 4.0)

    def update(self):
        """Update position based on specialized flight trajectory."""
        current_time = pygame.time.get_ticks()
        elapsed_sec = (current_time - self.spawn_time) / 1000.0

        # Vertical descent
        self.pos_y += self.speed

        # Horizontal behavior based on pattern
        if self.pattern == "wave":
            # Sinusoidal weaving flight
            offset_x = math.sin(elapsed_sec * self.wave_frequency) * self.wave_amplitude
            self.rect.centerx = int(self.center_x + offset_x)
        else:
            self.rect.centerx = int(self.center_x)

        self.rect.centery = int(self.pos_y)

        # Despawn when far below bottom of the viewport
        if self.rect.top > SCREEN_HEIGHT + 40:
            self.kill()

    def take_damage(self, amount: int) -> bool:
        """
        Deal damage to enemy.
        Returns:
            True if enemy was destroyed, False if still alive.
        """
        self.health -= amount

        # Hit sparks
        if self.particle_group is not None:
            for _ in range(4):
                self.particle_group.add(
                    SparkParticle(self.rect.centerx, self.rect.centery, COLOR_YELLOW, 0.8)
                )

        if self.health <= 0:
            self.explode()
            return True
        return False

    def explode(self):
        """Trigger destruction particle explosion and sound."""
        if self.particle_group is not None:
            spark_count = 24 if self.enemy_type == "cruiser" else 14
            for _ in range(spark_count):
                color = random.choice([self.config["color"], COLOR_ORANGE, COLOR_YELLOW])
                mult = 1.3 if self.enemy_type == "cruiser" else 1.0
                self.particle_group.add(
                    SparkParticle(self.rect.centerx, self.rect.centery, color, mult)
                )

        self.asset_manager.play_sound("explosion")
        self.kill()


class EnemySpawner:
    """Controls dynamic spawning cadence, enemy pool variety, and difficulty scaling."""

    def __init__(self, asset_manager, enemy_group, particle_group):
        self.asset_manager = asset_manager
        self.enemy_group = enemy_group
        self.particle_group = particle_group
        self.last_spawn_time = 0
        self.start_time = pygame.time.get_ticks()

    def reset(self):
        """Reset spawner state for a new game session."""
        self.last_spawn_time = pygame.time.get_ticks()
        self.start_time = pygame.time.get_ticks()

    def update(self, current_score: int):
        """Evaluate timers and spawn enemies scaled to current score and elapsed time."""
        current_time = pygame.time.get_ticks()
        elapsed_sec = (current_time - self.start_time) / 1000.0

        # Difficulty factor increases with both time and score
        # 1.0 at start, progressively scales up
        difficulty = 1.0 + (current_score / 1200.0) + (elapsed_sec / 45.0)

        # Spawn interval decreases dynamically with difficulty
        interval_ms = max(
            ENEMY_SPAWN_INTERVAL_MIN_MS,
            int(ENEMY_SPAWN_INTERVAL_BASE_MS / math.sqrt(difficulty)),
        )

        if current_time - self.last_spawn_time >= interval_ms:
            self.last_spawn_time = current_time
            self._spawn_enemy(current_score, difficulty)

    def _spawn_enemy(self, current_score: int, difficulty: float):
        """Choose enemy archetype based on progression tier and spawn."""
        # Weighted archetype selection
        types = ["scout"]
        weights = [70]

        if current_score >= 250 or difficulty >= 1.5:
            types.append("interceptor")
            weights.append(35)

        if current_score >= 600 or difficulty >= 2.0:
            types.append("cruiser")
            weights.append(25)

        chosen_type = random.choices(types, weights=weights, k=1)[0]

        # Progressive speed boost capped at +60%
        speed_mult = 1.0 + min(0.6, (difficulty - 1.0) * 0.12)

        enemy = Enemy(
            enemy_type=chosen_type,
            asset_manager=self.asset_manager,
            particle_group=self.particle_group,
            speed_multiplier=speed_mult,
        )
        self.enemy_group.add(enemy)
