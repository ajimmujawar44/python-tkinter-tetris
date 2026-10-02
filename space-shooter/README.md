# 🚀 Cosmic Vanguard - 2D Space Shooter in Python

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/Tkinter-Built--in-00599C?style=for-the-badge&logo=python&logoColor=white)](https://docs.python.org/3/library/tkinter.html)
[![Pygame](https://img.shields.io/badge/Pygame-2.5%2B-green?style=for-the-badge&logo=pygame&logoColor=white)](https://www.pygame.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

A beginner-friendly yet feature-packed 2D Space Shooter built with Python. Features two playable editions:
1. **Tkinter Edition** (`main.py`): Pure standard library, zero external pip installations needed.
2. **Pygame Edition** (`main_pygame.py`): Full-featured retro arcade edition with synthesized audio, particle effects, multi-layer parallax starfields, and modular architecture.

---

## 🎮 Game Editions & Quick Start

### ⚡ 1. Tkinter Edition (Zero Install)
Requires **no external libraries**. Uses Python's built-in `tkinter` Canvas.
```bash
python main.py
```
*(or double-click `start_game.bat` on Windows)*

### 🛸 2. Pygame Edition (Advanced Visuals & Sound)
Includes synthesized 8-bit sound effects, kinetic spark particles, shield domes, and dynamic difficulty waves.
```bash
pip install -r requirements.txt
python main_pygame.py
```
*(or double-click `start_pygame.bat` on Windows)*

---

## 🕹️ Controls

| Action | Primary Key | Secondary Key |
| :--- | :--- | :--- |
| **Move Left** | `A` | `Left Arrow` |
| **Move Right** | `D` | `Right Arrow` |
| **Fire Lasers** | `Spacebar` | — |
| **Maneuver Up / Down** (Pygame) | `W` / `S` | `Up` / `Down` Arrow |
| **Restart Game** | `R` | `Spacebar` |
| **Main Menu / Pause** | `Esc` | — |

---

## 📂 Repository Structure

```
space-shooter/
│
├── main.py                  # Standalone Tkinter Space Shooter (Zero install)
├── main_pygame.py           # Advanced Pygame Space Shooter entry point
├── settings.py              # Global dimensions, colors, and game balance constants
├── player.py                # Player spaceship entity, controls, health, and shields
├── enemy.py                 # Enemy archetypes (Scout, Interceptor, Cruiser) & spawner
├── bullet.py                # Projectile engine & boundary lifecycle
├── particles.py             # Parallax starfield, explosion sparks, and engine trails
├── assets.py                # Procedural sprite generator and retro sound synthesizer
├── game.py                  # Master Pygame state machine (Start, Playing, Game Over)
│
├── assets/
│   ├── images/              # Auto-generated delta-wing ship sprites and projectiles
│   └── sounds/              # Auto-generated 16-bit PCM WAV audio effects
│
├── test_game.py             # Headless automated tests for Pygame mechanics
├── test_tkinter_game.py     # Headless automated tests for Tkinter mechanics
│
├── start_game.bat           # 1-Click launcher for Tkinter edition
├── start_pygame.bat         # 1-Click launcher for Pygame edition
│
├── requirements.txt         # Optional dependency (pygame>=2.5.0)
├── .gitignore               # Standard Python ignores (__pycache__, venv, etc.)
├── LICENSE                  # MIT License
└── README.md                # Project documentation & GitHub guide
```

---

## 🧪 Running Automated Tests

Both editions include headless test suites that run without opening a display window:

```bash
# Test Tkinter Edition
python test_tkinter_game.py

# Test Pygame Edition
python test_game.py
```

---

## 🌟 Future Roadmap

- [ ] Boss Battle encounters (Mothership dreadnought every 2,500 points)
- [ ] Weapon drop power-ups (Spread-shot, homing missiles, EMP bombs)
- [ ] Persistent high-score leaderboard saved to JSON
- [ ] Background chiptune music tracks

---

## 📄 License

This project is licensed under the [MIT License](LICENSE). Contributions, forks, and stars are welcome!
