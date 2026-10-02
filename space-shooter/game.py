"""
Space Shooter - Core Game Engine
Orchestrates the main game states (Start, Playing, Game Over), sprite pipelines,
collision handling, HUD rendering, and restart mechanics.
"""

import math
import pygame
from settings import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    COLOR_BACKGROUND,
    COLOR_WHITE,
    COLOR_CYAN,
    COLOR_GREEN,
    COLOR_YELLOW,
    COLOR_ORANGE,
    COLOR_RED,
    COLOR_GRAY,
    COLOR_TEXT,
    COLOR_TEXT_MUTED,
    COLOR_HEALTH_BG,
    COLOR_HEALTH_FG,
)
from assets import AssetManager
from particles import Starfield, FloatingText
from player import Player
from enemy import EnemySpawner


class Game:
    """Master controller managing game loop events, state machines, and rendering."""

    STATE_START = "start"
    STATE_PLAYING = "playing"
    STATE_GAME_OVER = "game_over"

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.state = self.STATE_START
        self.score = 0
        self.high_score = 0
        self.enemies_defeated = 0

        # Initialize Fonts
        pygame.font.init()
        self.font_title = pygame.font.SysFont("consolas, segoeui, arial", 44, bold=True)
        self.font_heading = pygame.font.SysFont("consolas, segoeui, arial", 26, bold=True)
        self.font_regular = pygame.font.SysFont("consolas, segoeui, arial", 18, bold=True)
        self.font_small = pygame.font.SysFont("consolas, segoeui, arial", 14, bold=True)

        # Assets & Systems
        self.assets = AssetManager()
        self.starfield = Starfield()

        # Sprite Groups
        self.bullet_group = pygame.sprite.Group()
        self.particle_group = pygame.sprite.Group()
        self.floating_texts = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()

        # Player
        self.player = Player(
            x=SCREEN_WIDTH // 2,
            y=SCREEN_HEIGHT - 60,
            asset_manager=self.assets,
            bullet_group=self.bullet_group,
            particle_group=self.particle_group,
        )

        # Spawner
        self.enemy_spawner = EnemySpawner(
            asset_manager=self.assets,
            enemy_group=self.enemy_group,
            particle_group=self.particle_group,
        )

    def reset_game(self):
        """Prepare fresh game session after game over or from start screen."""
        self.score = 0
        self.enemies_defeated = 0
        self.bullet_group.empty()
        self.enemy_group.empty()
        self.particle_group.empty()
        self.floating_texts.empty()
        self.player.reset(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)
        self.enemy_spawner.reset()
        self.state = self.STATE_PLAYING
        self.assets.play_sound("start")

    def handle_event(self, event: pygame.event.Event):
        """Dispatch user input events depending on the current game state."""
        if event.type == pygame.KEYDOWN:
            if self.state == self.STATE_START:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    self.reset_game()

            elif self.state == self.STATE_PLAYING:
                # In playing state, continuous keys handled in player.update()
                if event.key == pygame.K_ESCAPE:
                    self.state = self.STATE_START

            elif self.state == self.STATE_GAME_OVER:
                if event.key in (pygame.K_r, pygame.K_SPACE, pygame.K_RETURN):
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    self.state = self.STATE_START

    def update(self):
        """Tick game entities and evaluate physics and collisions."""
        # Stars always animate in the background across all states
        self.starfield.update()

        if self.state == self.STATE_PLAYING:
            # Update player and entities
            self.player.update()
            self.bullet_group.update()
            self.enemy_group.update()
            self.particle_group.update()
            self.floating_texts.update()

            # Dynamic Spawning
            self.enemy_spawner.update(self.score)

            # Check Collisions
            self._handle_collisions()

        elif self.state in (self.STATE_START, self.STATE_GAME_OVER):
            # Keep particles and floating text drifting smoothly
            self.particle_group.update()
            self.floating_texts.update()

    def _handle_collisions(self):
        """Detect and resolve interactions between bullets, enemies, and player."""
        # 1. Bullets vs Enemies
        hits = pygame.sprite.groupcollide(
            self.bullet_group, self.enemy_group, True, False
        )
        for bullet, hit_enemies in hits.items():
            for enemy in hit_enemies:
                destroyed = enemy.take_damage(bullet.damage)
                if destroyed:
                    self.score += enemy.score_value
                    self.enemies_defeated += 1
                    if self.score > self.high_score:
                        self.high_score = self.score

                    # Spawn floating combat points indicator
                    self.floating_texts.add(
                        FloatingText(
                            x=enemy.rect.centerx,
                            y=enemy.rect.centery,
                            text=f"+{enemy.score_value}",
                            color=COLOR_YELLOW,
                            font=self.font_small,
                        )
                    )

        # 2. Enemies vs Player
        collided_enemies = pygame.sprite.spritecollide(
            self.player, self.enemy_group, dokill=False
        )
        for enemy in collided_enemies:
            if not self.player.invulnerable:
                enemy.explode()
                result = self.player.take_damage(amount=35)
                if result == "dead":
                    self.state = self.STATE_GAME_OVER
                    self.assets.play_sound("game_over")
                elif result == "life_lost":
                    self.floating_texts.add(
                        FloatingText(
                            x=self.player.rect.centerx,
                            y=self.player.rect.top - 20,
                            text="LIFE LOST!",
                            color=COLOR_RED,
                            font=self.font_regular,
                        )
                    )

    def draw(self):
        """Render frame elements to display surface."""
        # Clear frame with deep void color
        self.screen.fill(COLOR_BACKGROUND)

        # Background Starfield
        self.starfield.draw(self.screen)

        if self.state == self.STATE_PLAYING:
            # Draw game entities
            self.bullet_group.draw(self.screen)
            self.enemy_group.draw(self.screen)
            self.player.draw(self.screen)

            # Draw particle effects
            for p in self.particle_group:
                p.draw(self.screen)

            for ft in self.floating_texts:
                ft.draw(self.screen)

            # Draw HUD Overlays
            self._draw_hud()

        elif self.state == self.STATE_START:
            for p in self.particle_group:
                p.draw(self.screen)
            self._draw_start_screen()

        elif self.state == self.STATE_GAME_OVER:
            # Draw remaining battlefield behind dark transparent overlay
            self.enemy_group.draw(self.screen)
            for p in self.particle_group:
                p.draw(self.screen)
            self._draw_game_over_screen()

    # -------------------------------------------------------------------------
    # Screen Renderers
    # -------------------------------------------------------------------------

    def _draw_hud(self):
        """Render high-tech cockpit HUD: Health Bar, Lives, Score, Wave."""
        # 1. Health Bar
        bar_x = 20
        bar_y = 20
        bar_w = 180
        bar_h = 16

        # Background & border
        pygame.draw.rect(self.screen, COLOR_HEALTH_BG, (bar_x, bar_y, bar_w, bar_h))
        fill_ratio = max(0.0, self.player.health / self.player.max_health)
        fill_w = int(bar_w * fill_ratio)

        # Dynamic color shifting from green to red when low
        health_color = COLOR_HEALTH_FG if fill_ratio > 0.35 else COLOR_RED
        if fill_w > 0:
            pygame.draw.rect(self.screen, health_color, (bar_x, bar_y, fill_w, bar_h))
        pygame.draw.rect(self.screen, COLOR_CYAN, (bar_x - 1, bar_y - 1, bar_w + 2, bar_h + 2), 1)

        # Numeric Health Text
        hp_label = self.font_small.render(f"HULL {self.player.health}%", True, COLOR_TEXT)
        self.screen.blit(hp_label, (bar_x + bar_w + 10, bar_y))

        # 2. Lives Display
        life_icon = self.assets.get_image("life_icon")
        lives_start_x = 20
        lives_y = bar_y + 26
        for i in range(self.player.lives):
            if life_icon:
                self.screen.blit(life_icon, (lives_start_x + i * 26, lives_y))
            else:
                pygame.draw.circle(self.screen, COLOR_CYAN, (lives_start_x + i * 20 + 8, lives_y + 8), 6)

        # 3. Score & High Score Display
        score_surface = self.font_heading.render(f"SCORE  {self.score:06d}", True, COLOR_YELLOW)
        score_rect = score_surface.get_rect(topright=(SCREEN_WIDTH - 20, 16))
        self.screen.blit(score_surface, score_rect)

        high_surface = self.font_small.render(f"HI-SCORE  {self.high_score:06d}", True, COLOR_TEXT_MUTED)
        high_rect = high_surface.get_rect(topright=(SCREEN_WIDTH - 20, 48))
        self.screen.blit(high_surface, high_rect)

    def _draw_start_screen(self):
        """Render stylish futuristic start menu with gameplay controls and instructions."""
        center_x = SCREEN_WIDTH // 2

        # Title Glow
        title_text = "COSMIC VANGUARD"
        shadow = self.font_title.render(title_text, True, (0, 70, 90))
        self.screen.blit(shadow, shadow.get_rect(center=(center_x + 2, 112)))
        title = self.font_title.render(title_text, True, COLOR_CYAN)
        self.screen.blit(title, title.get_rect(center=(center_x, 110)))

        subtitle = self.font_regular.render("TACTICAL 2D SPACE SHOOTER", True, COLOR_TEXT_MUTED)
        self.screen.blit(subtitle, subtitle.get_rect(center=(center_x, 155)))

        # Instructions / Control Panel Box
        panel_rect = pygame.Rect(center_x - 220, 200, 440, 260)
        panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (20, 26, 45, 220), (0, 0, panel_rect.width, panel_rect.height), border_radius=8)
        pygame.draw.rect(panel_surf, COLOR_CYAN, (0, 0, panel_rect.width, panel_rect.height), width=2, border_radius=8)
        self.screen.blit(panel_surf, panel_rect)

        # Instructions text inside panel
        h_ctrl = self.font_heading.render("PILOT CONTROLS", True, COLOR_YELLOW)
        self.screen.blit(h_ctrl, h_ctrl.get_rect(center=(center_x, 230)))

        controls = [
            ("MOVE LEFT", "A  or  LEFT ARROW"),
            ("MOVE RIGHT", "D  or  RIGHT ARROW"),
            ("FIRE LASERS", "SPACEBAR"),
            ("THRUST PITCH", "W / S  or  UP / DOWN"),
        ]

        for i, (action, keys) in enumerate(controls):
            y = 270 + i * 28
            act_txt = self.font_regular.render(action, True, COLOR_TEXT_MUTED)
            self.screen.blit(act_txt, (center_x - 180, y))
            key_txt = self.font_regular.render(keys, True, COLOR_WHITE)
            self.screen.blit(key_txt, (center_x + 20, y))

        obj_txt = self.font_small.render(
            "Destroy incoming alien hostiles. Survive as difficulty escalates!",
            True,
            COLOR_GREEN,
        )
        self.screen.blit(obj_txt, obj_txt.get_rect(center=(center_x, 420)))

        # Animated Blinking Prompt
        ticks = pygame.time.get_ticks()
        if (ticks // 500) % 2 == 0:
            prompt = self.font_heading.render("PRESS [SPACE] OR [ENTER] TO LAUNCH", True, COLOR_WHITE)
            self.screen.blit(prompt, prompt.get_rect(center=(center_x, 505)))

    def _draw_game_over_screen(self):
        """Render Game Over screen with score breakdown and restart options."""
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 20, 210))
        self.screen.blit(overlay, (0, 0))

        center_x = SCREEN_WIDTH // 2

        # Header
        go_shadow = self.font_title.render("MISSION FAILED", True, (80, 10, 25))
        self.screen.blit(go_shadow, go_shadow.get_rect(center=(center_x + 2, 132)))
        go_title = self.font_title.render("MISSION FAILED", True, COLOR_RED)
        self.screen.blit(go_title, go_title.get_rect(center=(center_x, 130)))

        # Stats Card
        card_rect = pygame.Rect(center_x - 180, 200, 360, 200)
        card_surf = pygame.Surface((card_rect.width, card_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (22, 26, 46, 230), (0, 0, card_rect.width, card_rect.height), border_radius=8)
        pygame.draw.rect(card_surf, COLOR_RED, (0, 0, card_rect.width, card_rect.height), width=2, border_radius=8)
        self.screen.blit(card_surf, card_rect)

        score_lbl = self.font_heading.render(f"FINAL SCORE: {self.score}", True, COLOR_YELLOW)
        self.screen.blit(score_lbl, score_lbl.get_rect(center=(center_x, 240)))

        is_new_high = self.score >= self.high_score and self.score > 0
        hi_color = COLOR_GREEN if is_new_high else COLOR_TEXT_MUTED
        hi_suffix = " (NEW RECORD!)" if is_new_high else ""
        hi_lbl = self.font_regular.render(f"HIGH SCORE: {self.high_score}{hi_suffix}", True, hi_color)
        self.screen.blit(hi_lbl, hi_lbl.get_rect(center=(center_x, 290)))

        kills_lbl = self.font_regular.render(f"HOSTILES DESTROYED: {self.enemies_defeated}", True, COLOR_TEXT)
        self.screen.blit(kills_lbl, kills_lbl.get_rect(center=(center_x, 340)))

        # Restart Call To Action
        ticks = pygame.time.get_ticks()
        if (ticks // 500) % 2 == 0:
            prompt = self.font_heading.render("PRESS [R] OR [SPACE] TO RESTART", True, COLOR_CYAN)
            self.screen.blit(prompt, prompt.get_rect(center=(center_x, 460)))

        esc_note = self.font_small.render("Press [ESC] to return to Main Menu", True, COLOR_TEXT_MUTED)
        self.screen.blit(esc_note, esc_note.get_rect(center=(center_x, 500)))
