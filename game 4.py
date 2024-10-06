import tkinter as tk
import random
import math
import time

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
SHIP_SIZE = 20
STAR_SIZE = 10
OBSTACLE_SIZE = 30
INITIAL_VELOCITY = 0
MAX_VELOCITY = 10
THRUST = 0.5
BOOST_MULTIPLIER = 2
BOOST_DURATION = 3  # seconds
LEVEL_TIME = 30  # seconds per level
NUMBER_OF_STARS = 10
NUMBER_OF_OBSTACLES = 5

class Ship:
    def __init__(self, canvas):
        self.canvas = canvas
        self.x = WINDOW_WIDTH / 2
        self.y = WINDOW_HEIGHT / 2
        self.vx = INITIAL_VELOCITY
        self.vy = INITIAL_VELOCITY
        self.boost = False
        self.boost_end_time = None
        # Draw the ship as a triangle
        self.id = self.canvas.create_polygon(
            self.x, self.y - SHIP_SIZE,  # Top vertex
            self.x - SHIP_SIZE, self.y + SHIP_SIZE,  # Bottom left vertex
            self.x + SHIP_SIZE, self.y + SHIP_SIZE,  # Bottom right vertex
            fill="cyan"
        )

    def apply_thrust(self, direction):
        if direction == 'up':
            self.vy -= THRUST
        elif direction == 'down':
            self.vy += THRUST
        elif direction == 'left':
            self.vx -= THRUST
        elif direction == 'right':
            self.vx += THRUST
        # Limit velocity to MAX_VELOCITY
        self.vx = max(-MAX_VELOCITY, min(MAX_VELOCITY, self.vx))
        self.vy = max(-MAX_VELOCITY, min(MAX_VELOCITY, self.vy))

    def activate_boost(self):
        if not self.boost:
            self.boost = True
            self.vx *= BOOST_MULTIPLIER
            self.vy *= BOOST_MULTIPLIER
            self.boost_end_time = time.time() + BOOST_DURATION

    def update_position(self):
        # Update position based on velocity
        self.x += self.vx
        self.y += self.vy

        # Screen wrapping
        if self.x < 0:
            self.x = WINDOW_WIDTH
        elif self.x > WINDOW_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = WINDOW_HEIGHT
        elif self.y > WINDOW_HEIGHT:
            self.y = 0

        # Update the ship's position on the canvas
        self.canvas.coords(
            self.id,
            self.x, self.y - SHIP_SIZE,  # Top vertex
            self.x - SHIP_SIZE, self.y + SHIP_SIZE,  # Bottom left vertex
            self.x + SHIP_SIZE, self.y + SHIP_SIZE   # Bottom right vertex
        )

        # Handle boost duration
        if self.boost and time.time() >= self.boost_end_time:
            self.vx /= BOOST_MULTIPLIER
            self.vy /= BOOST_MULTIPLIER
            self.boost = False

class Star:
    def __init__(self, canvas):
        self.canvas = canvas
        self.x = random.randint(STAR_SIZE, WINDOW_WIDTH - STAR_SIZE)
        self.y = random.randint(STAR_SIZE, WINDOW_HEIGHT - STAR_SIZE)
        self.points = self.calculate_star_points(self.x, self.y, STAR_SIZE, 5)  # 5-pointed star
        self.id = self.canvas.create_polygon(self.points, fill="yellow")

    def calculate_star_points(self, x, y, size, points):
        """Calculate the coordinates for a star shape."""
        coords = []
        angle = math.pi / points
        for i in range(2 * points):
            radius = size if i % 2 == 0 else size / 2
            offset_x = x + math.cos(i * angle) * radius
            offset_y = y + math.sin(i * angle) * radius
            coords.append(offset_x)
            coords.append(offset_y)
        return coords

class Obstacle:
    def __init__(self, canvas):
        self.canvas = canvas
        self.x = random.randint(OBSTACLE_SIZE, WINDOW_WIDTH - OBSTACLE_SIZE)
        self.y = random.randint(OBSTACLE_SIZE, WINDOW_HEIGHT - OBSTACLE_SIZE)
        self.points = self.generate_asteroid_points(self.x, self.y, OBSTACLE_SIZE)
        self.id = self.canvas.create_polygon(self.points, fill="#B22222")  # Reddish color (Firebrick Red)

    def generate_asteroid_points(self, x, y, size):
        """Generate random points for an asteroid-like shape."""
        points = []
        num_vertices = random.randint(8, 12)  # Randomize the number of vertices
        for i in range(num_vertices):
            angle = i * (2 * math.pi / num_vertices)
            # Add some randomness to the radius for jagged edges
            radius = size * random.uniform(0.7, 1.2)
            point_x = x + math.cos(angle) * radius
            point_y = y + math.sin(angle) * radius
            points.extend([point_x, point_y])
        return points

class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("Zero-G Star Collector")
        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg="black")
        self.canvas.pack()

        # Initialize game objects
        self.ship = Ship(self.canvas)
        self.stars = [Star(self.canvas) for _ in range(NUMBER_OF_STARS)]
        self.obstacles = [Obstacle(self.canvas) for _ in range(NUMBER_OF_OBSTACLES)]
        self.score = 0
        self.level = 1
        self.start_time = time.time()
        self.game_over = False

        # Display score and level
        self.score_text = self.canvas.create_text(10, 10, anchor='nw', fill="white",
                                                 font=("Helvetica", 16),
                                                 text=f"Score: {self.score}")
        self.level_text = self.canvas.create_text(10, 40, anchor='nw', fill="white",
                                                 font=("Helvetica", 16),
                                                 text=f"Level: {self.level}")

        # Bind keys
        self.root.bind("<KeyPress-Up>", lambda event: self.ship.apply_thrust('up'))
        self.root.bind("<KeyPress-Down>", lambda event: self.ship.apply_thrust('down'))
        self.root.bind("<KeyPress-Left>", lambda event: self.ship.apply_thrust('left'))
        self.root.bind("<KeyPress-Right>", lambda event: self.ship.apply_thrust('right'))
        self.root.bind("<space>", lambda event: self.ship.activate_boost())

        # Start the game loop
        self.update()

    def update(self):
        if not self.game_over:
            current_time = time.time()
            elapsed_time = current_time - self.start_time

            # Check if level time has passed
            if elapsed_time >= LEVEL_TIME:
                self.level += 1
                self.start_time = current_time
                # Increase difficulty by adding more stars or obstacles
                if self.level % 2 == 0:
                    self.stars.append(Star(self.canvas))
                if self.level % 3 == 0:
                    self.obstacles.append(Obstacle(self.canvas))

            # Update ship position
            self.ship.update_position()

            # Check for collisions with stars
            for star in self.stars[:]:
                if self.check_collision(self.ship.x, self.ship.y, SHIP_SIZE, star.x, star.y, STAR_SIZE):
                    self.score += 1
                    self.canvas.delete(star.id)
                    self.stars.remove(star)
                    # Spawn a new star
                    self.stars.append(Star(self.canvas))
                    # Update score display
                    self.canvas.itemconfig(self.score_text, text=f"Score: {self.score}")

            # Check for collisions with obstacles
            for obstacle in self.obstacles:
                if self.check_collision(self.ship.x, self.ship.y, SHIP_SIZE, obstacle.x, obstacle.y, OBSTACLE_SIZE):
                    self.end_game()

            # Update level display
            self.canvas.itemconfig(self.level_text, text=f"Level: {self.level}")

            # Schedule next update
            self.root.after(20, self.update)  # ~50 FPS

    def check_collision(self, x1, y1, size1, x2, y2, size2):
        distance = math.hypot(x2 - x1, y2 - y1)
        return distance < (size1 + size2)

    def end_game(self):
        self.game_over = True
        self.canvas.create_text(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2,
                                text=f"Game Over!\nFinal Score: {self.score}",
                                fill="white", font=("Helvetica", 24), justify='center')

if __name__ == "__main__":
    root = tk.Tk()
    game = Game(root)
    root.mainloop()
