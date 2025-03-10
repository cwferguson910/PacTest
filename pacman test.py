import pygame, random, sys, math
# --- Global Constants ---
CELL_SIZE = 20
ROWS = 15
COLS = 15
# Maze grid dimensions: (2*COLS+1) x (2*ROWS+1)
GRID_WIDTH = COLS * 2 + 1
GRID_HEIGHT = ROWS * 2 + 1
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE
FPS = 60

# Colors
BLACK   = (0, 0, 0)
BLUE    = (0, 0, 255)
WHITE   = (255, 255, 255)
YELLOW  = (255, 255, 0)
RED     = (255, 0, 0)
GREEN   = (0, 255, 0)
PURPLE  = (128, 0, 128)
ORANGE  = (255, 165, 0)
CYAN    = (0, 255, 255)

# --- Maze Generation Classes ---
class Maze:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.width = cols * 2 + 1
        self.height = rows * 2 + 1
        self.grid = self.generate_maze()
        self.add_loops(0.1)
        
    def generate_maze(self):
        # Create a grid filled with walls (1 = wall, 0 = path)
        grid = [[1 for _ in range(self.width)] for _ in range(self.height)]
        start_x, start_y = 1, 1
        grid[start_y][start_x] = 0
        stack = [(start_x, start_y)]
        while stack:
            x, y = stack[-1]
            neighbors = []
            for dx, dy in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.width - 1 and 0 < ny < self.height - 1:
                    if grid[ny][nx] == 1:
                        neighbors.append((nx, ny))
            if neighbors:
                nx, ny = random.choice(neighbors)
                grid[ny][nx] = 0
                grid[y + (ny - y) // 2][x + (nx - x) // 2] = 0
                stack.append((nx, ny))
            else:
                stack.pop()
        return grid

    def add_loops(self, prob):
        # For each wall cell that separates two open cells, sometimes remove it
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.grid[y][x] == 1:
                    # Check horizontal neighbors
                    if self.grid[y][x - 1] == 0 and self.grid[y][x + 1] == 0:
                        if random.random() < prob:
                            self.grid[y][x] = 0
                    # Check vertical neighbors
                    if self.grid[y - 1][x] == 0 and self.grid[y + 1][x] == 0:
                        if random.random() < prob:
                            self.grid[y][x] = 0

# --- Sprite Classes ---
class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect(topleft=(x * CELL_SIZE, y * CELL_SIZE))

class Dot(pygame.sprite.Sprite):
    def __init__(self, x, y, dot_type="dot"):
        super().__init__()
        self.dot_type = dot_type  # "dot" or "power"
        if dot_type == "dot":
            size = CELL_SIZE // 4
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, WHITE, (size // 2, size // 2), size // 2)
        else:
            size = CELL_SIZE // 2
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, WHITE, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2))

class Fruit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        size = CELL_SIZE // 2
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(self.image, ORANGE, (0, 0, size, size))
        self.rect = self.image.get_rect(center=(x * CELL_SIZE + CELL_SIZE // 2, y * CELL_SIZE + CELL_SIZE // 2))
        self.spawn_time = pygame.time.get_ticks()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.cell_size = CELL_SIZE
        self.position = pygame.math.Vector2(x, y)
        self.speed = 2.0
        self.direction = pygame.math.Vector2(0, 0)
        self.animations = self.load_animations()
        self.current_frame = 0
        self.image = self.animations[self.current_frame]
        self.rect = self.image.get_rect(center=self.position)
        self.last_update = pygame.time.get_ticks()
        self.animation_delay = 100  # milliseconds per frame
        self.powered_up = False
        self.power_end_time = 0

    def load_animations(self):
        # Create 3 frames simulating an eating/walking cycle.
        frames = []
        for mouth in [20, 40, 0]:  # angles in degrees for the wedge "mouth"
            surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            # Draw full circle (pac-man body)
            pygame.draw.circle(surface, YELLOW, (CELL_SIZE // 2, CELL_SIZE // 2), CELL_SIZE // 2)
            # Compute wedge points to "cut" the mouth
            angle = math.radians(mouth / 2)
            center = (CELL_SIZE // 2, CELL_SIZE // 2)
            point1 = (CELL_SIZE // 2 + CELL_SIZE // 2 * math.cos(angle),
                      CELL_SIZE // 2 - CELL_SIZE // 2 * math.sin(angle))
            point2 = (CELL_SIZE // 2 + CELL_SIZE // 2 * math.cos(-angle),
                      CELL_SIZE // 2 - CELL_SIZE // 2 * math.sin(-angle))
            pygame.draw.polygon(surface, BLACK, [center, point1, point2])
            frames.append(surface)
        return frames

    def update(self, walls):
        keys = pygame.key.get_pressed()
        # Update movement direction based on arrow keys
        if keys[pygame.K_LEFT]:
            self.direction = pygame.math.Vector2(-1, 0)
        elif keys[pygame.K_RIGHT]:
            self.direction = pygame.math.Vector2(1, 0)
        elif keys[pygame.K_UP]:
            self.direction = pygame.math.Vector2(0, -1)
        elif keys[pygame.K_DOWN]:
            self.direction = pygame.math.Vector2(0, 1)
        else:
            self.direction = pygame.math.Vector2(0, 0)
            
        # Attempt to move
        new_position = self.position + self.direction * self.speed
        new_rect = self.image.get_rect(center=new_position)
        collision = any(new_rect.colliderect(wall.rect) for wall in walls)
        if not collision:
            self.position = new_position
            self.rect.center = self.position

        # Update animation frame
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_delay:
            self.current_frame = (self.current_frame + 1) % len(self.animations)
            self.image = self.animations[self.current_frame]
            self.last_update = now

        # Check power-up expiration
        if self.powered_up and now > self.power_end_time:
            self.powered_up = False

class Ghost(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.cell_size = CELL_SIZE
        self.position = pygame.math.Vector2(x, y)
        self.speed = 2.0
        self.direction = pygame.math.Vector2(random.choice([(1,0), (-1,0), (0,1), (0,-1)]))
        self.animations = self.load_animations(color)
        self.current_frame = 0
        self.image = self.animations[self.current_frame]
        self.rect = self.image.get_rect(center=self.position)
        self.last_update = pygame.time.get_ticks()
        self.animation_delay = 150  # milliseconds per frame
        self.vulnerable = False

    def load_animations(self, color):
        # Create 3 animation frames with silly hats
        frames = []
        for i in range(3):
            surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
            # Draw ghost body as an ellipse
            pygame.draw.ellipse(surface, color, (0, 0, CELL_SIZE, CELL_SIZE))
            # Draw eyes
            pygame.draw.circle(surface, WHITE, (CELL_SIZE // 3, CELL_SIZE // 3), CELL_SIZE // 10)
            pygame.draw.circle(surface, WHITE, (2 * CELL_SIZE // 3, CELL_SIZE // 3), CELL_SIZE // 10)
            # Draw a silly hat (its shape/color varies)
            hat_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            pygame.draw.rect(surface, hat_color, (CELL_SIZE // 4, 0, CELL_SIZE // 2, CELL_SIZE // 4))
            frames.append(surface)
        return frames

    def update(self, walls):
        # Move ghost with simple random logic
        new_position = self.position + self.direction * self.speed
        new_rect = self.image.get_rect(center=new_position)
        collision = any(new_rect.colliderect(wall.rect) for wall in walls)
        if collision:
            # If colliding, choose a new random direction
            self.direction = pygame.math.Vector2(random.choice([(1,0), (-1,0), (0,1), (0,-1)]))
        else:
            self.position = new_position
            self.rect.center = self.position

        # Occasionally change direction randomly
        if random.random() < 0.02:
            self.direction = pygame.math.Vector2(random.choice([(1,0), (-1,0), (0,1), (0,-1)]))

        # Update animation frame
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_delay:
            self.current_frame = (self.current_frame + 1) % len(self.animations)
            self.image = self.animations[self.current_frame]
            self.last_update = now

        # If vulnerable, tint the ghost blue
        if self.vulnerable:
            tinted = self.image.copy()
            tinted.fill(CYAN, special_flags=pygame.BLEND_RGB_MULT)
            self.image = tinted

# --- Helper Functions ---
def create_maze_objects(maze, wall_group, dot_group):
    # For every grid cell, create a Wall sprite if it's a wall;
    # otherwise, create a Dot (or occasionally a power pellet).
    for y in range(maze.height):
        for x in range(maze.width):
            if maze.grid[y][x] == 1:
                wall_group.add(Wall(x, y))
            else:
                # Avoid placing a dot at the player start cell (assumed at (1,1))
                if (x, y) != (1, 1):
                    if random.random() < 0.05:
                        dot_group.add(Dot(x, y, "power"))
                    else:
                        dot_group.add(Dot(x, y, "dot"))

def reset_game():
    # (Re)initialize the maze and sprite groups.
    maze = Maze(ROWS, COLS)
    wall_group = pygame.sprite.Group()
    dot_group = pygame.sprite.Group()
    create_maze_objects(maze, wall_group, dot_group)
    # Place the player at cell (1,1)
    player = Player(CELL_SIZE * 1 + CELL_SIZE // 2, CELL_SIZE * 1 + CELL_SIZE // 2)
    # Create three ghosts at various positions (for example, at the maze corners)
    ghost_group = pygame.sprite.Group()
    ghost_group.add(Ghost(CELL_SIZE * (maze.width - 2) + CELL_SIZE // 2, CELL_SIZE * (maze.height - 2) + CELL_SIZE // 2, RED))
    ghost_group.add(Ghost(CELL_SIZE * (maze.width - 2) + CELL_SIZE // 2, CELL_SIZE * 1 + CELL_SIZE // 2, PURPLE))
    ghost_group.add(Ghost(CELL_SIZE * 1 + CELL_SIZE // 2, CELL_SIZE * (maze.height - 2) + CELL_SIZE // 2, GREEN))
    fruit_group = pygame.sprite.Group()
    return maze, wall_group, dot_group, fruit_group, player, ghost_group

# --- Main Game Loop ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Pac-Man Style Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)
    
    # Game state variables
    score = 0
    level = 1
    lives = 3
    game_state = "playing"  # can be "playing", "paused", "game_over"
    
    maze, wall_group, dot_group, fruit_group, player, ghost_group = reset_game()
    
    pause_text = font.render("Paused - Press P to Resume, R to Restart", True, WHITE)
    game_over_text = font.render("Game Over - Press R to Restart", True, WHITE)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if game_state == "playing":
                    if event.key == pygame.K_p:
                        game_state = "paused"
                elif game_state == "paused":
                    if event.key == pygame.K_p:
                        game_state = "playing"
                    elif event.key == pygame.K_r:
                        score = 0
                        level = 1
                        lives = 3
                        maze, wall_group, dot_group, fruit_group, player, ghost_group = reset_game()
                        game_state = "playing"
                elif game_state == "game_over":
                    if event.key == pygame.K_r:
                        score = 0
                        level = 1
                        lives = 3
                        maze, wall_group, dot_group, fruit_group, player, ghost_group = reset_game()
                        game_state = "playing"
                        
        if game_state == "playing":
            # Update game objects
            player.update(wall_group)
            for ghost in ghost_group:
                # Set ghost vulnerability based on player's power-up status
                ghost.vulnerable = player.powered_up
                ghost.update(wall_group)
                
            # Check for dot collisions
            dot_collisions = pygame.sprite.spritecollide(player, dot_group, True)
            for dot in dot_collisions:
                if dot.dot_type == "power":
                    player.powered_up = True
                    player.power_end_time = pygame.time.get_ticks() + 7000  # 7 seconds
                    score += 50
                else:
                    score += 10
                    # Occasionally spawn a fruit where a dot was eaten
                    if random.random() < 0.1:
                        # Convert pixel position to grid cell
                        grid_x = (dot.rect.centerx - CELL_SIZE // 2) // CELL_SIZE
                        grid_y = (dot.rect.centery - CELL_SIZE // 2) // CELL_SIZE
                        fruit_group.add(Fruit(grid_x, grid_y))
            
            # Check for fruit collisions
            fruit_collisions = pygame.sprite.spritecollide(player, fruit_group, True)
            for fruit in fruit_collisions:
                score += 100
            
            # Check for ghost collisions
            ghost_hits = pygame.sprite.spritecollide(player, ghost_group, False)
            for ghost in ghost_hits:
                if player.powered_up:
                    score += 200
                    # Reset ghost to starting position
                    ghost.position = pygame.math.Vector2(CELL_SIZE * (maze.width - 2) + CELL_SIZE // 2,
                                                           CELL_SIZE * (maze.height - 2) + CELL_SIZE // 2)
                    ghost.rect.center = ghost.position
                else:
                    lives -= 1
                    # Reset player position
                    player.position = pygame.math.Vector2(CELL_SIZE * 1 + CELL_SIZE // 2, CELL_SIZE * 1 + CELL_SIZE // 2)
                    player.rect.center = player.position
                    pygame.time.delay(500)
                    if lives <= 0:
                        game_state = "game_over"
            
            # Level complete: when all dots are eaten
            if len(dot_group) == 0:
                level += 1
                # Increase ghost speed slightly for difficulty
                for ghost in ghost_group:
                    ghost.speed += 0.5
                maze, wall_group, dot_group, fruit_group, player, ghost_group = reset_game()
            
            # Remove fruits older than 5 seconds
            now = pygame.time.get_ticks()
            for fruit in list(fruit_group):
                if now - fruit.spawn_time > 5000:
                    fruit_group.remove(fruit)
                        
        # Drawing
        screen.fill(BLACK)
        wall_group.draw(screen)
        dot_group.draw(screen)
        fruit_group.draw(screen)
        ghost_group.draw(screen)
        screen.blit(player.image, player.rect)
        
        # Draw UI (score, level, lives)
        score_text = font.render(f"Score: {score}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        lives_text = font.render(f"Lives: {lives}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(level_text, (10, 30))
        screen.blit(lives_text, (10, 50))
        
        if game_state == "paused":
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))
        if game_state == "game_over":
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()
