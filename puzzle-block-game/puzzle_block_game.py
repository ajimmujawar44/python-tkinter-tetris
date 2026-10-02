import tkinter as tk
import random

class PuzzleBlockGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Puzzle Block Game")
        self.root.geometry("500x650")
        
        # Game settings
        self.cols = 10
        self.rows = 20
        self.cell_size = 25
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        
        # Tetromino shapes and colors
        self.shapes = {
            'I': {'shape': [(0,0), (0,1), (0,2), (0,3)], 'color': '#00f0f0'},
            'O': {'shape': [(0,0), (0,1), (1,0), (1,1)], 'color': '#f0f000'},
            'T': {'shape': [(0,1), (1,0), (1,1), (1,2)], 'color': '#a000f0'},
            'S': {'shape': [(0,1), (0,2), (1,0), (1,1)], 'color': '#00f000'},
            'Z': {'shape': [(0,0), (0,1), (1,1), (1,2)], 'color': '#f00000'},
            'J': {'shape': [(0,0), (1,0), (1,1), (1,2)], 'color': '#0000f0'},
            'L': {'shape': [(0,2), (1,0), (1,1), (1,2)], 'color': '#f0a000'}
        }
        
        self.current_piece = None
        self.current_pos = None
        self.current_shape = None
        self.score = 0
        self.game_over = False
        self.game_running = False
        
        self.setup_ui()
    
    def setup_ui(self):
        # Create main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Score display
        self.score_label = tk.Label(
            main_frame,
            text=f"Score: {self.score}",
            font=("Arial", 16, "bold")
        )
        self.score_label.pack(pady=(0, 10))
        
        # Canvas for the game
        canvas_width = self.cols * self.cell_size
        canvas_height = self.rows * self.cell_size
        self.canvas = tk.Canvas(
            main_frame,
            width=canvas_width,
            height=canvas_height,
            bg="black",
            relief=tk.RAISED,
            borderwidth=2
        )
        self.canvas.pack(pady=10)
        
        # Control buttons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            button_frame,
            text="Start Game",
            command=self.start_game,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Pause",
            command=self.pause_game,
            bg="#f39c12",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Reset",
            command=self.reset_game,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 10, "bold")
        ).pack(side=tk.LEFT, padx=5)
        
        # Instructions
        instructions = tk.Label(
            main_frame,
            text="Controls: ← → Move | ↓ Drop | ↑ Rotate",
            font=("Arial", 9),
            fg="#7f8c8d"
        )
        instructions.pack(pady=5)
        
        # Bind keyboard controls
        self.root.bind("<Left>", lambda e: self.move_piece(-1, 0))
        self.root.bind("<Right>", lambda e: self.move_piece(1, 0))
        self.root.bind("<Down>", lambda e: self.move_piece(0, 1))
        self.root.bind("<Up>", lambda e: self.rotate_piece())
        
        # Draw empty grid
        self.draw_grid()
    
    def draw_grid(self):
        """Draw the game grid"""
        self.canvas.delete("all")
        
        # Draw grid lines
        for row in range(self.rows + 1):
            y = row * self.cell_size
            self.canvas.create_line(
                0, y, self.cols * self.cell_size, y,
                fill="#333333",
                width=1
            )
        
        for col in range(self.cols + 1):
            x = col * self.cell_size
            self.canvas.create_line(
                x, 0, x, self.rows * self.cell_size,
                fill="#333333",
                width=1
            )
        
        # Draw placed blocks
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col]:
                    self.draw_block(row, col, self.grid[row][col])
        
        # Draw current piece
        if self.current_piece and self.current_pos:
            for block in self.current_shape:
                row = self.current_pos[0] + block[0]
                col = self.current_pos[1] + block[1]
                if 0 <= row < self.rows and 0 <= col < self.cols:
                    self.draw_block(row, col, self.current_piece['color'])
    
    def draw_block(self, row, col, color):
        """Draw a single block"""
        x1 = col * self.cell_size + 1
        y1 = row * self.cell_size + 1
        x2 = (col + 1) * self.cell_size - 1
        y2 = (row + 1) * self.cell_size - 1
        
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=color,
            outline="black",
            width=1
        )
    
    def start_game(self):
        """Start the game"""
        if not self.game_running:
            self.game_running = True
            self.game_over = False
            self.spawn_piece()
            self.game_loop()
    
    def pause_game(self):
        """Pause the game"""
        self.game_running = not self.game_running
        if self.game_running and not self.game_over:
            self.game_loop()
    
    def reset_game(self):
        """Reset the game"""
        self.game_running = False
        self.game_over = False
        self.score = 0
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.current_piece = None
        self.current_pos = None
        self.current_shape = None
        self.score_label.config(text=f"Score: {self.score}")
        self.draw_grid()
    
    def spawn_piece(self):
        """Spawn a new random piece"""
        piece_type = random.choice(list(self.shapes.keys()))
        self.current_piece = self.shapes[piece_type]
        self.current_shape = self.current_piece['shape'].copy()
        
        # Start position (top center)
        self.current_pos = [0, (self.cols - 4) // 2]
        
        # Check if game over
        if not self.is_valid_position(self.current_pos, self.current_shape):
            self.game_over = True
            self.game_running = False
            self.canvas.create_text(
                self.cols * self.cell_size // 2,
                self.rows * self.cell_size // 2,
                text="GAME OVER",
                fill="red",
                font=("Arial", 24, "bold")
            )
    
    def is_valid_position(self, pos, shape):
        """Check if a position is valid for the current shape"""
        for block in shape:
            row = pos[0] + block[0]
            col = pos[1] + block[1]
            
            # Check boundaries
            if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
                return False
            
            # Check collision with placed blocks
            if row >= 0 and self.grid[row][col]:
                return False
        
        return True
    
    def move_piece(self, dx, dy):
        """Move the current piece"""
        if not self.game_running or self.game_over or not self.current_piece:
            return
        
        new_pos = [self.current_pos[0] + dy, self.current_pos[1] + dx]
        
        if self.is_valid_position(new_pos, self.current_shape):
            self.current_pos = new_pos
            self.draw_grid()
        elif dy > 0:  # Moving down and hit something
            self.lock_piece()
    
    def rotate_piece(self):
        """Rotate the current piece"""
        if not self.game_running or self.game_over or not self.current_piece:
            return
        
        # Rotate shape 90 degrees clockwise
        new_shape = [(block[1], -block[0]) for block in self.current_shape]
        
        if self.is_valid_position(self.current_pos, new_shape):
            self.current_shape = new_shape
            self.draw_grid()
    
    def lock_piece(self):
        """Lock the current piece in place"""
        for block in self.current_shape:
            row = self.current_pos[0] + block[0]
            col = self.current_pos[1] + block[1]
            if 0 <= row < self.rows and 0 <= col < self.cols:
                self.grid[row][col] = self.current_piece['color']
        
        self.clear_lines()
        self.spawn_piece()
        self.draw_grid()
    
    def clear_lines(self):
        """Clear completed lines"""
        lines_cleared = 0
        
        for row in range(self.rows - 1, -1, -1):
            if all(self.grid[row]):
                # Remove the line
                del self.grid[row]
                # Add empty line at top
                self.grid.insert(0, [0 for _ in range(self.cols)])
                lines_cleared += 1
                row += 1  # Check the same row again
        
        if lines_cleared > 0:
            self.score += lines_cleared * 100
            self.score_label.config(text=f"Score: {self.score}")
    
    def game_loop(self):
        """Main game loop"""
        if self.game_running and not self.game_over:
            self.move_piece(0, 1)  # Move down
            self.root.after(500, self.game_loop)

def main():
    root = tk.Tk()
    game = PuzzleBlockGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()
