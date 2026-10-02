"""
Space Shooter - Player Spaceship Entity
Implements player controls (Left/Right/A/D, Space to shoot), health, lives,
invulnerability frames, engine particle emission, and weapon firing.
"""

import pygame
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    PLAYER_SPEED,
    PLAYER_START_HEALTH,
    PLAYER_START_LIVES,
    PLAYER_FIRE_COOLDOWN_MS,
    PLAYER_INVULNERABLE_DURATION_MS,
    PLAYER_SIZE,
    COLOR_CYAN,
    COLOR_RED,
)
from bullet import Bullet
from particles import ThrusterParticle, SparkParticle


class Player(pygame.sprite.Sprite):
    """Player controllable spaceship sprite."""

    def __init__(self, x: int, y: int, asset_manager, bullet_group, particle_group):
        super().__init__()
        self.asset_manager = asset_manager
        self.bullet_group = bullet_group
        self.particle_group = particle_group

        # Base Image & Rect
        self.image = self.asset_manager.get_image("player")
        if self.image is None:
            self.image = pygame.Surface(PLAYER_SIZE, pygame.SRCALPHA)
            pygame.draw.polygon(self.image, COLOR_CYAN, [(27, 2), (52, 48), (2, 48)])
        self.rect = self.image.get_rect(center=(x, y))

        # Shield & UI visual assets
        self.shield_image = self.asset_manager.get_image("shield")
        self.bullet_image = self.asset_manager.get_image("bullet_player")

        # Movement & Gameplay Stats
        self.speed = PLAYER_SPEED
        self.health = PLAYER_START_HEALTH
        self.max_health = PLAYER_START_HEALTH
        self.lives = PLAYER_START_LIVES

        # Firing system
        self.fire_cooldown_ms = PLAYER_FIRE_COOLDOWN_MS
        self.last_shot_time = 0

        # Invulnerability / Hit reaction
        self.invulnerable = False
        self.invulnerable_end_time = 0
        self.visible = True
        self.flash_counter = 0

    def update(self):
        """Handle movement, boundary collisions, invulnerability, and thrusters."""
        self._handle_input()
        self._clamp_to_screen()
        self._update_invulnerability()
        self._emit_thruster_particles()

    def _handle_input(self):
        """Process keyboard state for movement and shooting."""
        keys = pygame.key.get_pressed()

        dx = 0
        dy = 0

        # Left / Right Arrow or A / D (Requirements)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed

        # Up / Down subtle maneuvering (confined to bottom third of screen)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed * 0.75
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed * 0.75

        self.rect.x += int(dx)
        self.rect.y += int(dy)

        # Space to shoot
        if keys[pygame.K_SPACE]:
            self.shoot()

    def _clamp_to_screen(self):
        """Keep spaceship strictly inside playable bounds."""
        if self.rect.left < 5:
            self.rect.left = 5
        if self.rect.right > SCREEN_WIDTH - 5:
            self.rect.right = SCREEN_WIDTH - 5

        # Confine vertical movement to lower flight deck
        min_y = SCREEN_HEIGHT - 170
        max_y = SCREEN_HEIGHT - 20
        if self.rect.top < min_y:
            self.rect.top = min_y
        if self.rect.bottom > max_y:
            self.rect.bottom = max_y

    def _update_invulnerability(self):
        """Track mercy invulnerability countdown and blinking effect."""
        current_time = pygame.time.get_ticks()
        if self.invulnerable:
            if current_time >= self.invulnerable_end_time:
                self.invulnerable = False
                self.visible = True
            else:
                # Rapid blink effect
                self.flash_counter += 1
                self.visible = (self.flash_counter // 5) % 2 == 0
        else:
            self.visible = True

    def _emit_thruster_particles(self):
        """Emit animated engine trails from dual thruster ports."""
        if self.particle_group is not None:
            # Left engine nozzle
            self.particle_group.add(ThrusterParticle(self.rect.centerx - 7, self.rect.bottom - 4))
            # Right engine nozzle
            self.particle_group.add(ThrusterParticle(self.rect.centerx + 7, self.rect.bottom - 4))

    def shoot(self) -> bool:
        """Fire dual laser bolts if cooldown has elapsed."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time >= self.fire_cooldown_ms:
            self.last_shot_time = current_time

            # Dual laser mounts on wingtips
            b_left = Bullet(
                self.rect.centerx - 14,
                self.rect.top + 6,
                is_enemy=False,
                image=self.bullet_image,
            )
            b_right = Bullet(
                self.rect.centerx + 14,
                self.rect.top + 6,
                is_enemy=False,
                image=self.bullet_image,
            )
            self.bullet_group.add(b_left, b_right)

            # Play firing sound
            self.asset_manager.play_sound("laser")
            return True
        return False

    def take_damage(self, amount: int) -> str:
        """
        Apply damage to player.
        Returns:
            'ignored': if currently invulnerable
            'damaged': took hit but survived with health
            'life_lost': health reached 0, consumed 1 life, respawned
            'dead': lives exhausted (Game Over)
        """
        if self.invulnerable:
            return "ignored"

        self.health -= amount

        # Spawn impact sparks
        if self.particle_group is not None:
            for _ in range(12):
                self.particle_group.add(SparkParticle(self.rect.centerx, self.rect.centery, COLOR_RED, 1.2))

        self.asset_manager.play_sound("hit")

        if self.health <= 0:
            self.lives -= 1
            if self.lives > 0:
                self.health = self.max_health
                self.trigger_invulnerability(PLAYER_INVULNERABLE_DURATION_MS)
                # Center ship on respawn
                self.rect.centerx = SCREEN_WIDTH // 2
                self.rect.bottom = SCREEN_HEIGHT - 35
                return "life_lost"
            else:
                self.health = 0
                return "dead"
        else:
            self.trigger_invulnerability(600)  # Brief flinch invulnerability
            return "damaged"

    def trigger_invulnerability(self, duration_ms: int = PLAYER_INVULNERABLE_DURATION_MS):
        """Grant temporary invulnerability with shield protection."""
        self.invulnerable = True
        self.invulnerable_end_time = pygame.time.get_ticks() + duration_ms
        self.flash_counter = 0

    def reset(self, x: int, y: int):
        """Reset player state for a fresh game session."""
        self.health = self.max_health
        self.lives = PLAYER_START_LIVES
        self.invulnerable = False
        self.visible = True
        self.last_shot_time = 0
        self.rect.center = (x, y)

    def draw(self, surface: pygame.Surface):
        """Custom draw method to support blinking and shield aura."""
        if self.visible:
            surface.blit(self.image, self.rect)

            # Draw glowing shield dome when invulnerable
            if self.invulnerable and self.shield_image:
                shield_rect = self.shield_image.get_rect(center=self.rect.center)
                surface.blit(self.shield_image, shield_rect)
