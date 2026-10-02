"""Pac-Man clone built with Tkinter."""

from __future__ import annotations

import math
import random
import tkinter as tk
from dataclasses import dataclass
from tkinter import font as tkfont


TILE = 24
TICK_MS = 16
PAC_SPEED = 2
GHOST_SPEED = 2
FRIGHT_SPEED = 1
FRIGHT_MS = 7000
EATEN_SPEED = 4
LIVES = 3

WALL = "#"
PELLET = "."
POWER = "o"
GATE = "-"
EMPTY = " "
PAC_START = "P"
GHOST_START = "G"

MAZE = [
    "###################",
    "#........#........#",
    "#o##.###.#.###.##o#",
    "#.##.###.#.###.##.#",
    "#.................#",
    "#.##.#.#####.#.##.#",
    "#....#...#...#....#",
    "####.### # ###.####",
    "   #.#   G   #.#   ",
    "####.# ##-## #.####",
    "    .  #GGG#  .    ",
    "####.# ##### #.####",
    "   #.#       #.#   ",
    "####.# ##### #.####",
    "#........#........#",
    "#.##.###.#.###.##.#",
    "#o.#.....P....#..o#",
    "##.#.#.#####.#.#.##",
    "#....#...#...#....#",
    "#.######.#.######.#",
    "#.................#",
    "###################",
]
if len({len(row) for row in MAZE}) != 1:
    raise ValueError("All maze rows must be the same length")

DIRS = {
    "left": (-1, 0),
    "right": (1, 0),
    "up": (0, -1),
    "down": (0, 1),
}

OPPOSITE = {
    "left": "right",
    "right": "left",
    "up": "down",
    "down": "up",
}

GHOST_COLORS = {
    "blinky": "#ff3b3b",
    "pinky": "#ff8ec8",
    "inky": "#4ad6ff",
    "clyde": "#ffb347",
}

SCATTER_TARGETS = {
    "blinky": (18, 0),
    "pinky": (0, 0),
    "inky": (18, 21),
    "clyde": (0, 21),
}


@dataclass
class Entity:
    x: float
    y: float
    direction: str
    speed: float
    next_direction: str | None = None

    @property
    def col(self) -> int:
        return int(math.floor((self.x + 0.001) / TILE))

    @property
    def row(self) -> int:
        return int(math.floor((self.y + 0.001) / TILE))

    def pixel_center(self) -> tuple[float, float]:
        return self.x + TILE / 2, self.y + TILE / 2


class PacmanGame(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Pac-Man")
        self.configure(bg="#0b0d12")
        self.resizable(False, False)

        self.rows = len(MAZE)
        self.cols = len(MAZE[0])
        self.width = self.cols * TILE
        self.height = self.rows * TILE

        self.title_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        self.ui_font = tkfont.Font(family="Segoe UI", size=11)
        self.big_font = tkfont.Font(family="Segoe UI", size=22, weight="bold")

        self.hud = tk.Frame(self, bg="#0b0d12")
        self.hud.pack(fill="x", padx=12, pady=(10, 6))
        self.score_var = tk.StringVar()
        self.lives_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Arrow keys or WASD to move")
        tk.Label(self.hud, textvariable=self.score_var, fg="#f7e27c", bg="#0b0d12", font=self.title_font).pack(side="left")
        tk.Label(self.hud, textvariable=self.lives_var, fg="#ff8ec8", bg="#0b0d12", font=self.title_font).pack(side="right")
        tk.Label(self, textvariable=self.status_var, fg="#9aa3ae", bg="#0b0d12", font=self.ui_font).pack(pady=(0, 6))

        self.canvas = tk.Canvas(
            self,
            width=self.width,
            height=self.height,
            bg="#05060a",
            highlightthickness=0,
        )
        self.canvas.pack(padx=12, pady=(0, 12))

        self.bind("<KeyPress>", self._on_key)
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.focus_set()

        self._reset_level(full=True)
        self._tick()

    def _reset_level(self, full: bool) -> None:
        self.walls: set[tuple[int, int]] = set()
        self.gate: set[tuple[int, int]] = set()
        self.pellets: set[tuple[int, int]] = set()
        self.power: set[tuple[int, int]] = set()
        self.ghost_home: list[tuple[int, int]] = []
        pac_pos = (10, 16)
        self.tunnel_rows: set[int] = set()

        for r, line in enumerate(MAZE):
            for c, ch in enumerate(line):
                if ch == WALL:
                    self.walls.add((c, r))
                elif ch == GATE:
                    self.gate.add((c, r))
                elif ch == PELLET:
                    self.pellets.add((c, r))
                elif ch == POWER:
                    self.power.add((c, r))
                elif ch == PAC_START:
                    pac_pos = (c, r)
                elif ch == GHOST_START:
                    self.ghost_home.append((c, r))
                if ch != WALL and (c == 0 or c == self.cols - 1):
                    self.tunnel_rows.add(r)

        if self.ghost_home:
            hx = sum(c for c, _r in self.ghost_home) / len(self.ghost_home)
            hy = sum(r for _c, r in self.ghost_home) / len(self.ghost_home)
            self.house_center = (int(round(hx)), int(round(hy)))
        else:
            self.house_center = (self.cols // 2, self.rows // 2)
        if self.gate:
            gx = sum(c for c, _r in self.gate) / len(self.gate)
            gy = min(r for _c, r in self.gate)
            self.gate_exit = (int(round(gx)), gy - 1)
        else:
            self.gate_exit = (self.house_center[0], self.house_center[1] - 2)

        if full:
            self.score = 0
            self.lives = LIVES
            self.level = 1

        self.pac = Entity(pac_pos[0] * TILE, pac_pos[1] * TILE, "left", PAC_SPEED)
        self.mouth = 0.0
        self.running = True
        self.won = False
        self.paused = False
        self.fright_until = 0
        self.mode = "scatter"
        self.mode_until = self._now() + 7000
        self.ghost_points = 200
        self.message_until = 0

        starts = self.ghost_home + [self.house_center] * 4
        names = ["blinky", "pinky", "inky", "clyde"]
        self.ghosts: list[dict] = []
        for i, name in enumerate(names):
            col, row = starts[i]
            self.ghosts.append(
                {
                    "name": name,
                    "entity": Entity(col * TILE, row * TILE, "left" if i == 0 else "up", GHOST_SPEED),
                    "state": "leaving" if i == 0 else "home",
                    "release_at": self._now() + i * 1800,
                    "color": GHOST_COLORS[name],
                }
            )

        self._refresh_hud()
        self.status_var.set("Arrow keys or WASD  ·  P pause  ·  R restart")

    def _now(self) -> int:
        return int(self.tk.call("clock", "milliseconds"))

    def _refresh_hud(self) -> None:
        self.score_var.set(f"Score  {self.score}")
        self.lives_var.set("♥ " * self.lives + f"  Lv {self.level}")

    def _on_key(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        mapping = {
            "left": "left",
            "right": "right",
            "up": "up",
            "down": "down",
            "a": "left",
            "d": "right",
            "w": "up",
            "s": "down",
        }
        if key in mapping and self.running:
            self.pac.next_direction = mapping[key]
        elif key in {"p", "escape"}:
            if self.running:
                self.paused = not self.paused
                self.status_var.set("Paused" if self.paused else "Arrow keys or WASD  ·  P pause  ·  R restart")
        elif key == "r":
            self._reset_level(full=True)

    def _blocked(self, col: int, row: int, allow_gate: bool = False) -> bool:
        if row < 0 or row >= self.rows:
            return True
        if col < 0 or col >= self.cols:
            return (row not in self.tunnel_rows)
        if (col, row) in self.walls:
            return True
        if (col, row) in self.gate and not allow_gate:
            return True
        return False

    def _wrap(self, col: int, row: int) -> tuple[int, int]:
        if row in self.tunnel_rows:
            if col < 0:
                return self.cols - 1, row
            if col >= self.cols:
                return 0, row
        return col, row

    def _aligned(self, entity: Entity) -> bool:
        return abs(entity.x - entity.col * TILE) < 0.51 and abs(entity.y - entity.row * TILE) < 0.51

    def _can_move(self, entity: Entity, direction: str, allow_gate: bool = False) -> bool:
        dx, dy = DIRS[direction]
        col, row = self._wrap(entity.col + dx, entity.row + dy)
        return not self._blocked(col, row, allow_gate=allow_gate)

    def _step_entity(self, entity: Entity, allow_gate: bool = False, auto_turn: bool = False) -> None:
        if entity.next_direction == OPPOSITE.get(entity.direction) and self._can_move(entity, entity.next_direction, allow_gate):
            entity.direction = entity.next_direction
            entity.next_direction = None
        if self._aligned(entity):
            entity.x = entity.col * TILE
            entity.y = entity.row * TILE
            chosen = None
            if entity.next_direction and self._can_move(entity, entity.next_direction, allow_gate):
                chosen = entity.next_direction
            elif self._can_move(entity, entity.direction, allow_gate):
                chosen = entity.direction
            elif auto_turn:
                for d in DIRS:
                    if self._can_move(entity, d, allow_gate):
                        chosen = d
                        break
            if chosen:
                entity.direction = chosen
            if chosen == entity.next_direction:
                entity.next_direction = None

        if not self._can_move(entity, entity.direction, allow_gate) and self._aligned(entity):
            return

        dx, dy = DIRS[entity.direction]
        entity.x += dx * entity.speed
        entity.y += dy * entity.speed

        max_x = (self.cols - 1) * TILE
        if entity.x < 0:
            entity.x = max_x
        elif entity.x > max_x:
            entity.x = 0
        if entity.y < 0:
            entity.y = 0
        elif entity.y > (self.rows - 1) * TILE:
            entity.y = (self.rows - 1) * TILE

    def _ghost_target(self, ghost: dict) -> tuple[int, int]:
        name = ghost["name"]
        state = ghost["state"]
        pac = self.pac
        pdx, pdy = DIRS[pac.direction]
        if state in {"eaten", "home"}:
            return self.house_center if state == "eaten" else self.gate_exit
        if state == "leaving":
            return self.gate_exit
        if state == "frightened":
            return (random.randint(0, self.cols - 1), random.randint(0, self.rows - 1))
        if self.mode == "scatter":
            return SCATTER_TARGETS[name]
        if name == "blinky":
            return pac.col, pac.row
        if name == "pinky":
            return pac.col + pdx * 4, pac.row + pdy * 4
        if name == "inky":
            blinky = next(g for g in self.ghosts if g["name"] == "blinky")
            ax, ay = pac.col + pdx * 2, pac.row + pdy * 2
            return 2 * ax - blinky["entity"].col, 2 * ay - blinky["entity"].row
        dist = abs(pac.col - ghost["entity"].col) + abs(pac.row - ghost["entity"].row)
        if dist > 8:
            return pac.col, pac.row
        return SCATTER_TARGETS["clyde"]

    def _choose_ghost_dir(self, ghost: dict) -> str:
        entity = ghost["entity"]
        allow_gate = ghost["state"] in {"leaving", "eaten", "home"}
        target = self._ghost_target(ghost)
        options = []
        for d, (dx, dy) in DIRS.items():
            if d == OPPOSITE[entity.direction]:
                continue
            ncol, nrow = self._wrap(entity.col + dx, entity.row + dy)
            if self._blocked(ncol, nrow, allow_gate=allow_gate):
                continue
            dist = (ncol - target[0]) ** 2 + (nrow - target[1]) ** 2
            options.append((dist, d))
        if not options:
            return OPPOSITE[entity.direction]
        if ghost["state"] == "frightened":
            return random.choice([d for _, d in options])
        options.sort(key=lambda item: (item[0], ["up", "left", "down", "right"].index(item[1])))
        return options[0][1]

    def _update_mode(self) -> None:
        now = self._now()
        if now < self.fright_until:
            return
        if now >= self.mode_until:
            if self.mode == "scatter":
                self.mode = "chase"
                self.mode_until = now + 20000
            else:
                self.mode = "scatter"
                self.mode_until = now + 7000
            for ghost in self.ghosts:
                if ghost["state"] == "normal":
                    ghost["entity"].direction = OPPOSITE[ghost["entity"].direction]

    def _update_ghosts(self) -> None:
        now = self._now()
        frightened = now < self.fright_until
        for ghost in self.ghosts:
            entity = ghost["entity"]
            if ghost["state"] == "home":
                if now >= ghost["release_at"]:
                    ghost["state"] = "leaving"
                entity.speed = 1
            elif ghost["state"] == "leaving":
                entity.speed = GHOST_SPEED
                if (entity.col, entity.row) == self.gate_exit and self._aligned(entity):
                    ghost["state"] = "frightened" if frightened else "normal"
                    entity.direction = random.choice(["left", "right"])
            elif ghost["state"] == "eaten":
                entity.speed = EATEN_SPEED
                if abs(entity.col - self.house_center[0]) + abs(entity.row - self.house_center[1]) <= 1 and self._aligned(entity):
                    ghost["state"] = "leaving"
            else:
                if frightened and ghost["state"] != "frightened":
                    ghost["state"] = "frightened"
                    entity.direction = OPPOSITE[entity.direction]
                if not frightened and ghost["state"] == "frightened":
                    ghost["state"] = "normal"
                entity.speed = FRIGHT_SPEED if ghost["state"] == "frightened" else GHOST_SPEED

            if self._aligned(entity):
                entity.next_direction = self._choose_ghost_dir(ghost)
            allow_gate = ghost["state"] in {"leaving", "eaten", "home"}
            self._step_entity(entity, allow_gate=allow_gate)

    def _eat_at_pac(self) -> None:
        cell = (self.pac.col, self.pac.row)
        if cell in self.pellets:
            self.pellets.remove(cell)
            self.score += 10
        if cell in self.power:
            self.power.remove(cell)
            self.score += 50
            self.fright_until = self._now() + FRIGHT_MS
            self.ghost_points = 200
            for ghost in self.ghosts:
                if ghost["state"] in {"normal", "frightened", "leaving"}:
                    if ghost["state"] == "normal":
                        ghost["state"] = "frightened"
                        ghost["entity"].direction = OPPOSITE[ghost["entity"].direction]
        if not self.pellets and not self.power:
            self.won = True
            self.running = False
            self.level += 1
            self.status_var.set("You cleared the maze! Press R to play again.")
        self._refresh_hud()

    def _collisions(self) -> None:
        px, py = self.pac.pixel_center()
        for ghost in self.ghosts:
            gx, gy = ghost["entity"].pixel_center()
            if math.hypot(px - gx, py - gy) > TILE * 0.65:
                continue
            if ghost["state"] == "frightened":
                ghost["state"] = "eaten"
                self.score += self.ghost_points
                self.ghost_points *= 2
                self._refresh_hud()
            elif ghost["state"] in {"normal", "leaving"}:
                self._lose_life()
                break

    def _lose_life(self) -> None:
        self.lives -= 1
        self._refresh_hud()
        if self.lives <= 0:
            self.running = False
            self.status_var.set("Game over. Press R to restart.")
            return
        self.status_var.set("Caught! Extra life remaining.")
        self.message_until = self._now() + 1200
        pac_pos = (10, 16)
        for r, line in enumerate(MAZE):
            for c, ch in enumerate(line):
                if ch == PAC_START:
                    pac_pos = (c, r)
        self.pac = Entity(pac_pos[0] * TILE, pac_pos[1] * TILE, "left", PAC_SPEED)
        starts = self.ghost_home + [self.house_center] * 4
        for i, ghost in enumerate(self.ghosts):
            col, row = starts[i]
            ghost["entity"] = Entity(col * TILE, row * TILE, "up", GHOST_SPEED)
            ghost["state"] = "leaving" if i == 0 else "home"
            ghost["release_at"] = self._now() + i * 1800
        self.fright_until = 0

    def _tick(self) -> None:
        if self.running and not self.paused:
            self.pac.speed = PAC_SPEED
            self._step_entity(self.pac, allow_gate=False)
            self.mouth += 0.22
            self._eat_at_pac()
            self._update_mode()
            self._update_ghosts()
            self._collisions()
            if self._now() > self.message_until and self.running:
                self.status_var.set("Arrow keys or WASD  ·  P pause  ·  R restart")
        self._draw()
        self.after(TICK_MS, self._tick)

    def _draw_maze(self) -> None:
        self.canvas.delete("all")
        for r in range(self.rows):
            for c in range(self.cols):
                x0, y0 = c * TILE, r * TILE
                x1, y1 = x0 + TILE, y0 + TILE
                if (c, r) in self.walls:
                    self.canvas.create_rectangle(x0 + 1, y0 + 1, x1 - 1, y1 - 1, fill="#1b3a8a", outline="#2c5ad4", width=1)
                elif (c, r) in self.gate:
                    self.canvas.create_line(x0 + 2, y0 + TILE / 2, x1 - 2, y0 + TILE / 2, fill="#ffb6d9", width=3)
        for c, r in self.pellets:
            x, y = c * TILE + TILE / 2, r * TILE + TILE / 2
            self.canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="#f8e9a1", outline="")
        pulse = 4 + abs(math.sin(self.mouth / 2)) * 2
        for c, r in self.power:
            x, y = c * TILE + TILE / 2, r * TILE + TILE / 2
            self.canvas.create_oval(x - pulse, y - pulse, x + pulse, y + pulse, fill="#fff3c4", outline="")

    def _draw_pac(self) -> None:
        x0, y0 = self.pac.x + 2, self.pac.y + 2
        x1, y1 = self.pac.x + TILE - 2, self.pac.y + TILE - 2
        opening = 35 + 25 * abs(math.sin(self.mouth))
        start = {
            "right": opening,
            "down": 90 + opening,
            "left": 180 + opening,
            "up": 270 + opening,
        }[self.pac.direction]
        extent = 360 - opening * 2
        self.canvas.create_arc(x0, y0, x1, y1, start=start, extent=extent, fill="#ffe14a", outline="#ffe14a")

    def _draw_ghost(self, ghost: dict) -> None:
        e = ghost["entity"]
        x0, y0 = e.x + 2, e.y + 2
        x1, y1 = e.x + TILE - 2, e.y + TILE - 2
        now = self._now()
        if ghost["state"] == "eaten":
            color = ""
        elif ghost["state"] == "frightened":
            remaining = self.fright_until - now
            color = "#d7d7ff" if remaining < 2000 and int(remaining / 150) % 2 == 0 else "#3b5cff"
        else:
            color = ghost["color"]

        body_top = y0 + 8
        if ghost["state"] != "eaten":
            self.canvas.create_oval(x0, y0, x1, y0 + 18, fill=color, outline=color)
            self.canvas.create_rectangle(x0, body_top, x1, y1 - 4, fill=color, outline=color)
            wave = 4
            pts = [x0, y1 - 4]
            for i in range(4):
                px = x0 + (x1 - x0) * i / 3
                py = y1 if i % 2 == 0 else y1 - wave
                pts.extend([px, py])
            pts.extend([x1, y1 - 4])
            self.canvas.create_polygon(pts, fill=color, outline=color)

        eye_y = y0 + 8
        offsets = {"left": -2, "right": 2, "up": 0, "down": 0}
        ox = offsets.get(e.direction, 0)
        oy = -2 if e.direction == "up" else (2 if e.direction == "down" else 0)
        for ex in (x0 + 6, x1 - 10):
            self.canvas.create_oval(ex, eye_y, ex + 6, eye_y + 7, fill="white", outline="")
            self.canvas.create_oval(ex + 2 + ox / 2, eye_y + 2 + oy / 2, ex + 5 + ox / 2, eye_y + 6 + oy / 2, fill="#1a1a1a", outline="")

    def _draw_overlay(self) -> None:
        if self.running and not self.paused:
            return
        self.canvas.create_rectangle(0, self.height / 2 - 36, self.width, self.height / 2 + 36, fill="#000000", stipple="gray50", outline="")
        text = "Paused"
        if not self.running:
            text = "You win!" if self.won else "Game over"
        self.canvas.create_text(self.width / 2, self.height / 2, text=text, fill="#ffffff", font=self.big_font)

    def _draw(self) -> None:
        self._draw_maze()
        for ghost in self.ghosts:
            self._draw_ghost(ghost)
        self._draw_pac()
        self._draw_overlay()


if __name__ == "__main__":
    PacmanGame().mainloop()
