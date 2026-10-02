"""
Automated Unit and Integration Tests for Tkinter Space Shooter
Tests player movement, bullet firing, enemy spawning, collisions, and restarts.
"""

import unittest
import tkinter as tk
from main import SpaceShooterGame


class TestTkinterSpaceShooter(unittest.TestCase):
    """Test suite verifying Tkinter game logic and canvas elements."""

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Don't show window during tests
        self.game = SpaceShooterGame(self.root)

    def tearDown(self):
        try:
            self.root.destroy()
        except Exception:
            pass

    def test_initial_state(self):
        """Verify initial score, player placement, and status."""
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.is_game_over)
        self.assertEqual(self.game.player_x, self.game.WIDTH // 2)
        self.assertEqual(self.game.player_y, self.game.HEIGHT - 60)
        self.assertGreater(len(self.game.stars), 0)

    def test_player_movement(self):
        """Verify left and right keyboard input translates player coordinates."""
        init_x = self.game.player_x

        # Simulate Left arrow press
        self.game.keys_pressed.add("Left")
        self.game._update_player_movement()
        self.assertLess(self.game.player_x, init_x)

        # Simulate Right arrow press
        self.game.keys_pressed.clear()
        self.game.keys_pressed.add("Right")
        self.game._update_player_movement()
        self.game._update_player_movement()
        self.assertGreater(self.game.player_x, init_x - self.game.player_speed)

    def test_bullet_firing_and_movement(self):
        """Verify bullet is instantiated and moves upwards."""
        self.assertEqual(len(self.game.bullets), 0)
        self.game._fire_bullet()
        self.assertEqual(len(self.game.bullets), 1)

        bullet = self.game.bullets[0]
        b_box_before = self.game.canvas.bbox(bullet["id"])
        self.game._update_bullets()
        b_box_after = self.game.canvas.bbox(bullet["id"])

        self.assertLess(b_box_after[1], b_box_before[1])

    def test_enemy_spawning_and_despawning(self):
        """Verify enemy is created and moves downwards."""
        self.assertEqual(len(self.game.enemies), 0)
        self.game._spawn_enemy()
        self.assertEqual(len(self.game.enemies), 1)

        enemy = self.game.enemies[0]
        init_coords = self.game.canvas.coords(enemy["id"])
        self.game._update_enemies()
        new_coords = self.game.canvas.coords(enemy["id"])

        self.assertGreater(new_coords[1], init_coords[1])

    def test_bullet_enemy_collision(self):
        """Verify collision destroys enemy, consumes bullet, and scores points."""
        self.game._spawn_enemy()
        enemy = self.game.enemies[0]
        e_box = self.game.canvas.bbox(enemy["id"])

        # Place bullet directly intersecting enemy bounding box
        mid_x = (e_box[0] + e_box[2]) / 2
        mid_y = (e_box[1] + e_box[3]) / 2
        bullet_id = self.game.canvas.create_rectangle(
            mid_x - 2, mid_y - 4, mid_x + 2, mid_y + 4
        )
        self.game.bullets.append({"id": bullet_id, "speed": 10.0})

        init_score = self.game.score
        self.game._check_collisions()

        self.assertEqual(self.game.score, init_score + 10)
        self.assertEqual(len(self.game.enemies), 0)
        self.assertEqual(len(self.game.bullets), 0)

    def test_enemy_player_collision_game_over(self):
        """Verify collision with player triggers Game Over and restart capability."""
        self.game._spawn_enemy()
        enemy = self.game.enemies[0]
        # Reposition enemy right on top of player
        self.game.canvas.coords(
            enemy["id"],
            self.game.player_x, self.game.player_y,
            self.game.player_x + 10, self.game.player_y - 10,
            self.game.player_x - 10, self.game.player_y - 10,
        )

        self.game._check_collisions()
        self.assertTrue(self.game.is_game_over)

        # Test Restart
        self.game.restart_game()
        self.assertFalse(self.game.is_game_over)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(len(self.game.enemies), 0)
        self.assertEqual(len(self.game.bullets), 0)


if __name__ == "__main__":
    unittest.main()
