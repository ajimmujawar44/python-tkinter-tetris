# Python Desktop Games and Calculator

A small collection of Python desktop projects built with Tkinter and Pygame:

- **Calculator**: a dark-themed desktop calculator.
- **Pac-Man**: a maze game with pellets, power pellets, and ghosts.
- **Puzzle Block Game**: a Tetris-style game with seven tetromino shapes, line clearing, and score tracking.
- **Space Shooter**: an arcade shooter with a lightweight Tkinter edition and an enhanced Pygame edition.

## Requirements

- Python 3.10 or later is recommended.
- Tkinter is used by the calculator, Pac-Man, puzzle block game, and Tkinter Space Shooter. It is included with most Python installations. On some Linux distributions, install the operating system's `python3-tk` package if Tkinter is missing.
- Pygame is needed only for the Pygame Space Shooter edition.

Install the Pygame dependency from the repository root:

```bash
python -m pip install -r requirements.txt
```

The other apps use only Python's standard library and do not need packages from `requirements.txt`.

## Run an App

Run each command from the repository root:

```bash
# Calculator
python calculator-app/calculator.py

# Pac-Man
python calculator-app/pacman.py

# Puzzle Block Game
python puzzle-block-game/puzzle_block_game.py

# Space Shooter, Tkinter edition (no extra package)
python space-shooter/main.py

# Space Shooter, Pygame edition (requires Pygame)
python space-shooter/main_pygame.py
```

On Windows, the Space Shooter folder also contains `start_game.bat` and `start_pygame.bat` launchers.

## Controls

- **Calculator**: use the on-screen buttons or keyboard. `Enter` / `=` evaluates, `Backspace` deletes, and `Esc` clears.
- **Puzzle Block Game**: arrow keys move and rotate the falling piece; use the in-game buttons to start, pause, or reset.
- **Space Shooter**: `A` / `Left Arrow` and `D` / `Right Arrow` move, `Space` fires, `R` restarts, and `Esc` opens the menu or pauses. The Pygame edition also supports `W` / `S` or `Up` / `Down` for vertical movement.
- **Pac-Man**: use the arrow keys to navigate the maze.

## Project Layout

```text
AI-Games/
├── calculator-app/       # Calculator and Pac-Man (Tkinter)
├── puzzle-block-game/    # Falling-block puzzle game (Tkinter)
├── space-shooter/        # Tkinter and Pygame shooter editions
├── README.md             # Workspace overview and instructions
└── requirements.txt      # Third-party Python dependencies
```