"""
Space Shooter - Settings & Global Constants
Centralizes all game dimensions, colors, gameplay parameters, and asset paths.
"""

import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
IMAGES_DIR = ASSETS_DIR / "images"
SOUNDS_DIR = ASSETS_DIR / "sounds"

# Window & Display
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GAME_TITLE = "Cosmic Vanguard - 2D Space Shooter"

# Color Palette (Futuristic Neon / Sci-Fi Theme)
COLOR_BACKGROUND = (10, 12, 26)       # Deep void navy
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_TEXT = (230, 240, 255)
COLOR_TEXT_MUTED = (140, 160, 190)

# Accent Colors
COLOR_CYAN = (0, 240, 255)            # Player energy / shields
COLOR_GREEN = (0, 255, 128)           # Health / Positive feedback
COLOR_YELLOW = (255, 220, 40)         # Score / Warnings
COLOR_ORANGE = (255, 130, 30)         # Explosions / Boosters
COLOR_RED = (255, 50, 80)             # Enemy laser / Critical damage
COLOR_PURPLE = (180, 70, 255)         # Rare enemies / Power accents
COLOR_GRAY = (60, 65, 85)
COLOR_HEALTH_BG = (40, 20, 25)
COLOR_HEALTH_FG = (0, 230, 110)

# Player Settings
PLAYER_SPEED = 7
PLAYER_START_HEALTH = 100
PLAYER_START_LIVES = 3
PLAYER_FIRE_COOLDOWN_MS = 220
PLAYER_INVULNERABLE_DURATION_MS = 1500  # Mercy invulnerability after damage
PLAYER_SIZE = (54, 50)

# Bullet Settings
BULLET_SPEED = 14
BULLET_SIZE = (6, 18)
BULLET_DAMAGE = 25

# Enemy Settings
ENEMY_SPAWN_INTERVAL_BASE_MS = 1200   # Initial spawn cadence
ENEMY_SPAWN_INTERVAL_MIN_MS = 380     # Hardest spawn cadence
ENEMY_BASE_SPEED_MIN = 2
ENEMY_BASE_SPEED_MAX = 4

# Enemy Types & Attributes
ENEMY_TYPES = {
    "scout": {
        "name": "Scout Raider",
        "health": 25,
        "speed": 3.2,
        "score_value": 100,
        "color": COLOR_RED,
        "size": (42, 38),
        "pattern": "straight",
    },
    "interceptor": {
        "name": "Swift Interceptor",
        "health": 20,
        "speed": 4.8,
        "score_value": 175,
        "color": COLOR_PURPLE,
        "size": (36, 34),
        "pattern": "wave",
    },
    "cruiser": {
        "name": "Armored Cruiser",
        "health": 75,
        "speed": 1.8,
        "score_value": 300,
        "color": COLOR_ORANGE,
        "size": (56, 52),
        "pattern": "descend",
    },
}

# Starfield Background
STAR_LAYERS = [
    {"count": 50, "speed": 0.5, "radius": 1, "color": (120, 130, 160)},  # Slow background
    {"count": 30, "speed": 1.2, "radius": 2, "color": (180, 200, 230)},  # Mid-ground
    {"count": 15, "speed": 2.5, "radius": 2, "color": (255, 255, 255)},  # Fast foreground
]

# Audio Settings
SFX_VOLUME = 0.5
AUDIO_ENABLED = True
