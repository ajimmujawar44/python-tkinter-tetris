"""
Space Shooter - Tkinter Edition
A 2D Space Shooter built using Python's standard Tkinter library.
No external dependencies required.
"""

import math
import random
import tkinter as tk


class SpaceShooterGame:
    """Main game class managing canvas, state, entities, and the Tkinter game loop."""

    WIDTH = 600
    HEIGHT = 700
    FRAME_RATE_MS = 16  # ~60 FPS

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Cosmic Vanguard - Tkinter Space Shooter")
        self.root.resizable(False, False)

        # Game State
        self.score = 0
        self.is_game_over = False
        self.keys_pressed = set()
        self.bullets = []
        self.enemies = []
        self.stars = []

        # Difficulty & Timers
        self.base_enemy_speed = 3.0
        self.enemy_spawn_interval = 70  # Frames between enemy spawns (~1.1s)
        self.spawn_timer = 0
        self.last_shot_time = 0
        self.fire_cooldown_ms = 220

        # UI & Canvas Setup
        self._create_widgets()
        self._init_starfield()
        self._create_player()
        self._bind_events()

        # Start game loop
        self.root.after(self.FRAME_RATE_MS, self.game_loop)

    def _create_widgets(self):
        """Construct the top HUD and the main rendering Canvas."""
        # Top HUD Frame
        self.hud_frame = tk.Frame(self.root, bg="#0d1117", padx=15, pady=8)
        self.hud_frame.pack(fill=tk.X)

        self.score_label = tk.Label(
            self.hud_frame,
            text="SCORE: 0",
            font=("Consolas", 14, "bold"),
            fg="#00e5ff",
            bg="#0d1117",
        )
        self.score_label.pack(side=tk.LEFT)

        self.difficulty_label = tk.Label(
            self.hud_frame,
            text="LEVEL: 1",
            font=("Consolas", 12, "bold"),
            fg="#ffd600",
            bg="#0d1117",
        )
        self.difficulty_label.pack(side=tk.RIGHT)

        # Game Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.WIDTH,
            height=self.HEIGHT,
            bg="#080a14",
            highlightthickness=0,
        )
        self.canvas.pack()

        # Restart Button (hidden initially, shown on Game Over)
        self.restart_button = tk.Button(
            self.root,
            text="PLAY AGAIN",
            font=("Consolas", 12, "bold"),
            bg="#00e5ff",
            fg="#080a14",
            activebackground="#80d8ff",
            activeforeground="#080a14",
            padx=12,
            pady=4,
            relief=tk.FLAT,
            command=self.restart_game,
            cursor="hand2",
        )

    def _init_starfield(self):
        """Populate background stars for depth perception."""
        self.stars.clear()
        for _ in range(55):
            x = random.randint(0, self.WIDTH)
            y = random.randint(0, self.HEIGHT)
            speed = random.choice([1.0, 1.8, 3.0])
            size = 1 if speed < 2.0 else 2
            color = "#546e7a" if speed < 2.0 else "#ffffff"
            star_id = self.canvas.create_oval(
                x, y, x + size, y + size, fill=color, outline=color
            )
            self.stars.append({"id": star_id, "speed": speed, "size": size})

    def _create_player(self):
        """Draw player spaceship on canvas using vector polygons."""
        self.player_x = self.WIDTH // 2
        self.player_y = self.HEIGHT - 60
        self.player_speed = 6.5

        # Spaceship Hull (futuristic delta shape)
        pts = self._get_player_polygon_coords(self.player_x, self.player_y)
        self.player_id = self.canvas.create_polygon(
            pts, fill="#00e5ff", outline="#ffffff", width=2
        )

        # Cockpit Canopy Glass
        self.cockpit_id = self.canvas.create_polygon(
            self.player_x, self.player_y - 12,
            self.player_x + 5, self.player_y + 2,
            self.player_x - 5, self.player_y + 2,
            fill="#ffffff", outline="#80d8ff"
        )

        # Thruster Engine Glow
        self.thruster_id = self.canvas.create_oval(
            self.player_x - 6, self.player_y + 12,
            self.player_x + 6, self.player_y + 20,
            fill="#ff9100", outline="#ffd600"
        )

    def _get_player_polygon_coords(self, x: float, y: float):
        """Calculate vertex coordinates for player delta-wing body."""
        return [
            x, y - 24,           # Nose
            x + 24, y + 14,      # Right wingtip
            x + 12, y + 8,       # Right engine notch
            x + 5, y + 14,       # Right rear
            x - 5, y + 14,       # Left rear
            x - 12, y + 8,       # Left engine notch
            x - 24, y + 14,      # Left wingtip
        ]

    def _bind_events(self):
        """Bind keyboard handlers for fluid non-repeating controls."""
        self.root.bind("<KeyPress>", self._on_key_press)
        self.root.bind("<KeyRelease>", self._on_key_release)
        # Ensure canvas can receive focus
        self.canvas.focus_set()

    def _on_key_press(self, event):
        """Track pressed keys and trigger immediate actions."""
        key = event.keysym
        self.keys_pressed.add(key)

        if key == "space" and not self.is_game_over:
            self._fire_bullet()

        # Keyboard shortcut for restart
        if key in ("r", "R", "Return") and self.is_game_over:
            self.restart_game()

    def _on_key_release(self, event):
        """Remove released keys from active set."""
        key = event.keysym
        self.keys_pressed.discard(key)

    def _fire_bullet(self):
        """Spawn laser projectile from the player's nose cannon."""
        now = self.root.tk.call("clock", "milliseconds") if hasattr(self.root.tk, "call") else int(random.random() * 1000)
        # Standard bullet creation
        bx = self.player_x
        by = self.player_y - 28
        bullet_id = self.canvas.create_rectangle(
            bx - 2, by - 12, bx + 2, by, fill="#ffd600", outline="#ffffff", width=1
        )
        self.bullets.append({"id": bullet_id, "speed": 11.0})

    def _spawn_enemy(self):
        """Spawn an enemy spaceship at a randomized X position above the canvas."""
        ex = random.randint(30, self.WIDTH - 30)
        ey = -25

        # Enemy speed scales smoothly with current score
        speed = self.base_enemy_speed + random.uniform(0.2, 1.2) + (self.score / 200.0)

        # Enemy body (pointed downward)
        enemy_pts = [
            ex, ey + 18,        # Downward front nose
            ex + 18, ey - 12,   # Top right wing
            ex + 6, ey - 4,     # Inner right notch
            ex - 6, ey - 4,     # Inner left notch
            ex - 18, ey - 12,   # Top left wing
        ]
        color = random.choice(["#ff1744", "#d500f9", "#ff5252"])
        enemy_id = self.canvas.create_polygon(
            enemy_pts, fill=color, outline="#ffffff", width=1
        )

        # Core reactor eye
        core_id = self.canvas.create_oval(
            ex - 4, ey - 2, ex + 4, ey + 6, fill="#ffd600", outline="#ff9100"
        )

        self.enemies.append({
            "id": enemy_id,
            "core_id": core_id,
            "speed": speed,
            "x": ex,
            "y": ey,
        })

    def _update_player_movement(self):
        """Move player horizontally based on keyboard input."""
        dx = 0
        if "Left" in self.keys_pressed or "a" in self.keys_pressed or "A" in self.keys_pressed:
            dx -= self.player_speed
        if "Right" in self.keys_pressed or "d" in self.keys_pressed or "D" in self.keys_pressed:
            dx += self.player_speed

        if dx != 0:
            new_x = self.player_x + dx
            # Clamp player inside canvas walls
            if 28 <= new_x <= self.WIDTH - 28:
                self.player_x = new_x
                # Update hull polygon
                pts = self._get_player_polygon_coords(self.player_x, self.player_y)
                self.canvas.coords(self.player_id, *pts)
                # Update cockpit
                self.canvas.coords(
                    self.cockpit_id,
                    self.player_x, self.player_y - 12,
                    self.player_x + 5, self.player_y + 2,
                    self.player_x - 5, self.player_y + 2,
                )
                # Update thruster
                self.canvas.coords(
                    self.thruster_id,
                    self.player_x - 6, self.player_y + 12,
                    self.player_x + 6, self.player_y + 20,
                )

    def _update_stars(self):
        """Scroll background stars downwards with boundary wrapping."""
        for star in self.stars:
            self.canvas.move(star["id"], 0, star["speed"])
            coords = self.canvas.coords(star["id"])
            if coords and coords[1] >= self.HEIGHT:
                new_x = random.randint(0, self.WIDTH)
                size = star["size"]
                self.canvas.coords(star["id"], new_x, 0, new_x + size, size)

    def _update_bullets(self):
        """Move bullets upward and remove ones that travel beyond the top."""
        removals = []
        for bullet in self.bullets:
            self.canvas.move(bullet["id"], 0, -bullet["speed"])
            coords = self.canvas.coords(bullet["id"])
            if not coords or coords[3] < 0:
                self.canvas.delete(bullet["id"])
                removals.append(bullet)

        for b in removals:
            if b in self.bullets:
                self.bullets.remove(b)

    def _update_enemies(self):
        """Move enemies downward and cull those passing the bottom."""
        removals = []
        for enemy in self.enemies:
            self.canvas.move(enemy["id"], 0, enemy["speed"])
            self.canvas.move(enemy["core_id"], 0, enemy["speed"])
            coords = self.canvas.coords(enemy["id"])
            if not coords or coords[1] > self.HEIGHT + 30:
                self.canvas.delete(enemy["id"])
                self.canvas.delete(enemy["core_id"])
                removals.append(enemy)

        for e in removals:
            if e in self.enemies:
                self.enemies.remove(e)

    def _check_collisions(self):
        """Detect bullet-enemy and enemy-player overlaps."""
        player_box = self.canvas.bbox(self.player_id)
        if not player_box:
            return

        # 1. Bullet vs Enemy Collisions
        bullets_to_remove = set()
        enemies_to_remove = set()

        for b in self.bullets:
            b_box = self.canvas.bbox(b["id"])
            if not b_box:
                continue

            for e in self.enemies:
                if e["id"] in enemies_to_remove:
                    continue

                e_box = self.canvas.bbox(e["id"])
                if not e_box:
                    continue

                # Overlap check
                if self._boxes_intersect(b_box, e_box):
                    bullets_to_remove.add(b["id"])
                    enemies_to_remove.add(e["id"])

                    # Create brief explosion flash
                    self._create_explosion(
                        (e_box[0] + e_box[2]) / 2, (e_box[1] + e_box[3]) / 2
                    )

                    # Update Score & Difficulty Level
                    self.score += 10
                    self.score_label.config(text=f"SCORE: {self.score}")
                    level = 1 + self.score // 50
                    self.difficulty_label.config(text=f"LEVEL: {level}")
                    break

        # Cleanup collided bullets
        self.bullets = [
            b for b in self.bullets
            if b["id"] not in bullets_to_remove or self.canvas.delete(b["id"])
        ]

        # Cleanup destroyed enemies
        retained_enemies = []
        for e in self.enemies:
            if e["id"] in enemies_to_remove:
                self.canvas.delete(e["id"])
                self.canvas.delete(e["core_id"])
            else:
                retained_enemies.append(e)
        self.enemies = retained_enemies

        # 2. Enemy vs Player Collisions
        for e in self.enemies:
            e_box = self.canvas.bbox(e["id"])
            if e_box and self._boxes_intersect(player_box, e_box):
                self._trigger_game_over()
                break

    @staticmethod
    def _boxes_intersect(b1, b2) -> bool:
        """Return True if bounding box (x1, y1, x2, y2) overlaps."""
        return not (b1[2] < b2[0] or b1[0] > b2[2] or b1[3] < b2[1] or b1[1] > b2[3])

    def _create_explosion(self, x: float, y: float):
        """Draw small particle sparks that disappear shortly after impact."""
        sparks = []
        for _ in range(8):
            dx = random.uniform(-16, 16)
            dy = random.uniform(-16, 16)
            color = random.choice(["#ffd600", "#ff9100", "#ff1744", "#ffffff"])
            s_id = self.canvas.create_oval(
                x + dx - 2, y + dy - 2, x + dx + 2, y + dy + 2, fill=color, outline=""
            )
            sparks.append(s_id)

        # Remove sparks after 140ms
        self.root.after(140, lambda: [self.canvas.delete(s) for s in sparks])

    def _trigger_game_over(self):
        """Halt gameplay and present the Game Over screen."""
        self.is_game_over = True

        # Ship destruction explosion
        self._create_explosion(self.player_x, self.player_y)
        self.canvas.delete(self.player_id)
        self.canvas.delete(self.cockpit_id)
        self.canvas.delete(self.thruster_id)

        # Semi-transparent dark overlay effect
        overlay_id = self.canvas.create_rectangle(
            0, 0, self.WIDTH, self.HEIGHT, fill="#080a14", stipple="gray50"
        )

        # Game Over Banner
        self.go_title = self.canvas.create_text(
            self.WIDTH // 2,
            self.HEIGHT // 2 - 60,
            text="GAME OVER",
            font=("Consolas", 36, "bold"),
            fill="#ff1744",
        )

        self.go_score = self.canvas.create_text(
            self.WIDTH // 2,
            self.HEIGHT // 2 - 10,
            text=f"FINAL SCORE: {self.score}",
            font=("Consolas", 18, "bold"),
            fill="#00e5ff",
        )

        self.go_hint = self.canvas.create_text(
            self.WIDTH // 2,
            self.HEIGHT // 2 + 30,
            text="Press [R] or click below to play again",
            font=("Consolas", 12),
            fill="#cfd8dc",
        )

        # Attach Restart Button inside Canvas
        self.restart_window = self.canvas.create_window(
            self.WIDTH // 2, self.HEIGHT // 2 + 80, window=self.restart_button
        )

    def restart_game(self):
        """Clear all active entities, reset scores, and restart gameplay."""
        # Clear Canvas items
        self.canvas.delete("all")
        self.bullets.clear()
        self.enemies.clear()
        self.keys_pressed.clear()

        # Reset Stats
        self.score = 0
        self.score_label.config(text="SCORE: 0")
        self.difficulty_label.config(text="LEVEL: 1")
        self.spawn_timer = 0
        self.is_game_over = False

        # Re-initialize Environment
        self._init_starfield()
        self._create_player()
        self.canvas.focus_set()

    def game_loop(self):
        """Single frame tick driving animation, physics, and input."""
        if not self.is_game_over:
            # 1. Update Entities
            self._update_stars()
            self._update_player_movement()
            self._update_bullets()
            self._update_enemies()
            self._check_collisions()

            # 2. Dynamic Spawning
            self.spawn_timer += 1
            # Current spawn interval shortens with score (minimum every 22 frames)
            cur_interval = max(22, int(self.enemy_spawn_interval - (self.score // 30) * 4))
            if self.spawn_timer >= cur_interval:
                self.spawn_timer = 0
                self._spawn_enemy()
        else:
            # Keep stars scrolling even on Game Over screen
            self._update_stars()

        # Schedule next frame
        self.root.after(self.FRAME_RATE_MS, self.game_loop)


def main():
    """Application entry point for Tkinter Space Shooter."""
    root = tk.Tk()
    app = SpaceShooterGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
