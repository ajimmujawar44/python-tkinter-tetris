"""
Automated Unit and Integration Tests for Cosmic Vanguard Space Shooter
Runs headlessly without requiring a physical monitor or audio hardware.
"""

import os
import unittest

# Configure headless SDL drivers before importing Pygame
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    PLAYER_START_HEALTH,
    PLAYER_START_LIVES,
    ENEMY_TYPES,
)
from assets import AssetManager
from bullet import Bullet
from player import Player
from enemy import Enemy, EnemySpawner
from game import Game


class TestSpaceShooter(unittest.TestCase):
    """Test suite verifying game logic, entities, collisions, and state transitions."""

    @classmethod
    def setUpClass(cls):
        pygame.init()
        pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    def setUp(self):
        self.screen = pygame.display.get_surface()
        self.assets = AssetManager()
        self.bullet_group = pygame.sprite.Group()
        self.particle_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        self.player = Player(
            x=SCREEN_WIDTH // 2,
            y=SCREEN_HEIGHT - 60,
            asset_manager=self.assets,
            bullet_group=self.bullet_group,
            particle_group=self.particle_group,
        )

    def test_assets_loaded(self):
        """Ensure all required image and sound assets exist in AssetManager."""
        for key in ["player", "scout", "interceptor", "cruiser", "bullet_player", "bullet_enemy"]:
            self.assertIsNotNone(self.assets.get_image(key), f"Image asset '{key}' missing")

        for key in ["laser", "explosion", "hit", "game_over", "start"]:
            self.assertIn(key, self.assets.sounds, f"Sound asset '{key}' missing")

    def test_player_initial_state(self):
        """Verify player starts with correct health, lives, and bounds."""
        self.assertEqual(self.player.health, PLAYER_START_HEALTH)
        self.assertEqual(self.player.lives, PLAYER_START_LIVES)
        self.assertFalse(self.player.invulnerable)
        self.assertTrue(0 <= self.player.rect.centerx <= SCREEN_WIDTH)

    def test_player_shooting(self):
        """Verify player shooting creates dual bullets with appropriate attributes."""
        # Initial shot
        fired = self.player.shoot()
        self.assertTrue(fired)
        self.assertEqual(len(self.bullet_group), 2)

        # Immediate second shot should be throttled by cooldown
        fired_again = self.player.shoot()
        self.assertFalse(fired_again)
        self.assertEqual(len(self.bullet_group), 2)

    def test_bullet_movement_and_culling(self):
        """Verify bullets move upward and despawn when exceeding screen top."""
        bullet = Bullet(x=100, y=10, speed_y=-20)
        self.bullet_group.add(bullet)

        bullet.update()
        self.assertLess(bullet.rect.bottom, 0)
        # Bullet should be killed and removed from group
        self.assertNotIn(bullet, self.bullet_group)

    def test_enemy_spawning_and_attributes(self):
        """Verify each enemy archetype initializes with correct config values."""
        for enemy_type, expected_conf in ENEMY_TYPES.items():
            enemy = Enemy(
                enemy_type=enemy_type,
                asset_manager=self.assets,
                particle_group=self.particle_group,
            )
            self.assertEqual(enemy.health, expected_conf["health"])
            self.assertEqual(enemy.score_value, expected_conf["score_value"])
            self.assertEqual(enemy.pattern, expected_conf["pattern"])

            # Test movement
            init_y = enemy.rect.centery
            enemy.update()
            self.assertGreater(enemy.rect.centery, init_y)

    def test_enemy_damage_and_destruction(self):
        """Verify enemy takes damage and explodes when health reaches 0."""
        enemy = Enemy(
            enemy_type="scout",
            asset_manager=self.assets,
            particle_group=self.particle_group,
        )
        self.enemy_group.add(enemy)

        # Inflict non-lethal damage
        survived = enemy.take_damage(10)
        self.assertFalse(survived)
        self.assertEqual(enemy.health, 15)

        # Inflict lethal damage
        destroyed = enemy.take_damage(20)
        self.assertTrue(destroyed)
        self.assertNotIn(enemy, self.enemy_group)

    def test_player_damage_and_respawn(self):
        """Verify player loses life on lethal hit, respawns with shield, and dies at 0 lives."""
        self.player.take_damage(60)
        self.assertEqual(self.player.health, 40)
        self.assertEqual(self.player.lives, 3)

        # Clear invulnerability to test next hit
        self.player.invulnerable = False

        # Hit that depletes remaining health
        res = self.player.take_damage(50)
        self.assertEqual(res, "life_lost")
        self.assertEqual(self.player.lives, 2)
        self.assertEqual(self.player.health, PLAYER_START_HEALTH)
        self.assertTrue(self.player.invulnerable)

        # Deplete remaining lives
        self.player.invulnerable = False
        self.player.take_damage(100)
        self.player.invulnerable = False
        res_dead = self.player.take_damage(100)
        self.assertEqual(res_dead, "dead")
        self.assertEqual(self.player.lives, 0)

    def test_game_full_flow(self):
        """Verify Game state transitions: START -> PLAYING -> GAME_OVER -> RESTART."""
        game = Game(self.screen)
        self.assertEqual(game.state, Game.STATE_START)

        # Simulate Spacebar to start
        event_start = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
        game.handle_event(event_start)
        self.assertEqual(game.state, Game.STATE_PLAYING)

        # Simulate player killed
        game.player.lives = 1
        game.player.take_damage(100)
        # Verify transition to Game Over
        # Collision simulation
        enemy = Enemy("scout", game.assets, game.particle_group)
        game.enemy_group.add(enemy)
        enemy.rect.center = game.player.rect.center
        game._handle_collisions()

        self.assertEqual(game.state, Game.STATE_GAME_OVER)

        # Simulate Restart with R key
        event_restart = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)
        game.handle_event(event_restart)
        self.assertEqual(game.state, Game.STATE_PLAYING)
        self.assertEqual(game.score, 0)
        self.assertEqual(game.player.lives, PLAYER_START_LIVES)

    def test_bullet_enemy_collision_scoring(self):
        """Verify bullet hits enemy, scores points, and updates high score."""
        game = Game(self.screen)
        game.state = Game.STATE_PLAYING

        enemy = Enemy("scout", game.assets, game.particle_group)
        bullet = Bullet(x=100, y=100, damage=100)  # Lethal one-hit bullet

        game.enemy_group.add(enemy)
        game.bullet_group.add(bullet)
        enemy.rect.center = (100, 100)

        initial_score = game.score
        game._handle_collisions()

        self.assertEqual(game.score, initial_score + enemy.score_value)
        self.assertEqual(game.enemies_defeated, 1)
        self.assertEqual(game.high_score, game.score)
        self.assertNotIn(enemy, game.enemy_group)
        self.assertNotIn(bullet, game.bullet_group)


if __name__ == "__main__":
    unittest.main()
