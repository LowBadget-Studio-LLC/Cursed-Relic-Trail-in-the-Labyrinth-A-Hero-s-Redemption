# This code is made by LowBadget Studio LLc

import pygame
import numpy as np
import random
from collections import deque

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
# 修改游戏标题
pygame.display.set_caption("Cursed Relic Trail in the Labyrinth A Hero's Redemption")

# Color definitions
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (100, 100, 100)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (128, 0, 128)

# Map dimensions
MAP_WIDTH, MAP_HEIGHT = 80, 60
TILE_SIZE = 10

# Font settings
font = pygame.font.Font(None, 36)

# Sound generation
def generate_sound(frequency, duration):
    sample_rate = 44100
    num_samples = int(duration * sample_rate)
    sound_array = np.zeros((num_samples, 2), dtype=np.int16)
    for i in range(num_samples):
        t = float(i) / sample_rate
        value = int(32767 * np.sin(2 * np.pi * frequency * t))
        sound_array[i][0] = value
        sound_array[i][1] = value
    sound = pygame.sndarray.make_sound(sound_array)
    return sound

coin_sound = generate_sound(880, 0.2)
hurt_sound = generate_sound(220, 0.3)
heal_sound = generate_sound(1320, 0.2)
invincible_sound = generate_sound(1760, 0.2)

# Define the Map class
class Map:
    def __init__(self, level):
        self.level = level
        self.tiles = self.generate_map()
        self.generate_objects()

    def generate_map(self):
        maze = np.ones((MAP_HEIGHT, MAP_WIDTH), dtype=int)
        stack = []
        # 修改随机数范围
        start_x, start_y = random.randint(0, (MAP_WIDTH - 1) // 2) * 2 + 1, random.randint(0, (MAP_HEIGHT - 1) // 2) * 2 + 1
        maze[start_y, start_x] = 0
        stack.append((start_x, start_y))
        while stack:
            x, y = stack[-1]
            directions = [(0, -2), (0, 2), (-2, 0), (2, 0)]
            random.shuffle(directions)
            found = False
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                if 0 < new_x < MAP_WIDTH - 1 and 0 < new_y < MAP_HEIGHT - 1 and maze[new_y, new_x] == 1:
                    maze[y + dy // 2, x + dx // 2] = 0
                    maze[new_y, new_x] = 0
                    stack.append((new_x, new_y))
                    found = True
                    break
            if not found:
                stack.pop()
        return maze

    def generate_objects(self):
        self.gold_coins = []
        self.monsters = []
        self.items = []
        num_gold = random.randint(5 + self.level, 15 + self.level)
        num_monsters = random.randint(3 + self.level, 8 + self.level)
        num_items = random.randint(1, 3)

        while num_gold > 0:
            x, y = random.randint(0, MAP_WIDTH - 1), random.randint(0, MAP_HEIGHT - 1)
            if self.tiles[y, x] == 0 and (x, y) not in [coin for coin in self.gold_coins]:
                self.gold_coins.append((x, y))
                num_gold -= 1

        while num_monsters > 0:
            x, y = random.randint(0, MAP_WIDTH - 1), random.randint(0, MAP_HEIGHT - 1)
            if self.tiles[y, x] == 0 and (x, y) not in [monster for monster in self.monsters]:
                self.monsters.append((x, y))
                num_monsters -= 1

        while num_items > 0:
            x, y = random.randint(0, MAP_WIDTH - 1), random.randint(0, MAP_HEIGHT - 1)
            if self.tiles[y, x] == 0 and (x, y) not in [item for item in self.items]:
                item_type = random.choice(["heal", "invincible"])
                self.items.append((x, y, item_type))
                num_items -= 1

    def draw(self):
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if self.tiles[y, x] == 1:
                    pygame.draw.rect(screen, GREY, rect)
                else:
                    pygame.draw.rect(screen, WHITE, rect)

        for coin in self.gold_coins:
            x, y = coin
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, YELLOW, rect)

        for monster in self.monsters:
            x, y = monster
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, RED, rect)

        for item in self.items:
            x, y, _ = item
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, PURPLE, rect)

    def move_monsters(self):
        new_monsters = []
        for x, y in self.monsters:
            directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT and self.tiles[new_y, new_x] == 0:
                    new_monsters.append((new_x, new_y))
                    break
            else:
                new_monsters.append((x, y))
        self.monsters = new_monsters

# Define the Player class
class Player:
    def __init__(self):
        self.x = MAP_WIDTH // 2
        self.y = MAP_HEIGHT // 2
        self.speed = 1
        self.health = 100
        self.score = 0
        self.invincible = False
        self.invincible_time = 0
        self.path = []
        self.auto_mode = False

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT and game_map.tiles[new_y, new_x] == 0:
            self.x = new_x
            self.y = new_y

    def draw(self):
        rect = pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        if self.invincible:
            pygame.draw.rect(screen, BLUE, rect)
        else:
            pygame.draw.rect(screen, BLACK, rect)

    def check_collision(self, game_map):
        if (self.x, self.y) in game_map.gold_coins:
            game_map.gold_coins.remove((self.x, self.y))
            self.score += 10
            coin_sound.play()
            self.path = []  # Clear the path after picking up a coin
        elif (self.x, self.y) in game_map.monsters and not self.invincible:
            self.health -= 20
            hurt_sound.play()
            self.invincible = True
            self.invincible_time = pygame.time.get_ticks()
        for item in game_map.items:
            x, y, item_type = item
            if self.x == x and self.y == y:
                game_map.items.remove(item)
                if item_type == "heal":
                    self.health = min(100, self.health + 30)
                    heal_sound.play()
                elif item_type == "invincible":
                    self.invincible = True
                    self.invincible_time = pygame.time.get_ticks()
                    invincible_sound.play()

    def update_invincibility(self):
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.invincible_time > 5000:  # 5 - second invincibility time
                self.invincible = False

    def find_path(self, game_map):
        if not game_map.gold_coins:
            return []
        start = (self.x, self.y)
        queue = deque([(start, [])])
        visited = set([start])
        while queue:
            (x, y), path = queue.popleft()
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                new_x, new_y = x + dx, y + dy
                if 0 <= new_x < MAP_WIDTH and 0 <= new_y < MAP_HEIGHT and game_map.tiles[new_y, new_x] == 0:
                    if (new_x, new_y) in game_map.gold_coins:
                        return path + [(new_x, new_y)]
                    if (new_x, new_y) not in visited:
                        visited.add((new_x, new_y))
                        queue.append(((new_x, new_y), path + [(new_x, new_y)]))
        return []

    def auto_move(self, game_map):
        if not self.path:
            self.path = self.find_path(game_map)
        if self.path:
            next_x, next_y = self.path.pop(0)
            dx = next_x - self.x
            dy = next_y - self.y
            self.move(dx, dy)

# Game start screen
def show_start_screen():
    screen.fill(BLACK)
    # 修改开始界面标题文本
    title_text = font.render("Cursed Relic Trail in the Labyrinth A Hero's Redemption", 1, WHITE)
    start_text = font.render("Press any key to start the game", 1, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                waiting = False
    return True

# Game over screen
def show_game_over_screen(score):
    screen.fill(BLACK)
    game_over_text = font.render("Game Over", 1, WHITE)
    score_text = font.render(f"Your final score: {score}", 1, WHITE)
    restart_text = font.render("Press R to restart, press Q to quit", 1, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 100))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 100))
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
                elif event.key == pygame.K_q:
                    pygame.quit()
                    return False

# Main game loop
def main():
    global game_map
    level = 1
    if not show_start_screen():
        return
    while True:
        game_map = Map(level)
        player = Player()
        running = True
        clock = pygame.time.Clock()
        while running:
            clock.tick(10)  # Control the game frame rate
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w:
                        player.move(0, -player.speed)
                        player.auto_mode = False
                    elif event.key == pygame.K_s:
                        player.move(0, player.speed)
                        player.auto_mode = False
                    elif event.key == pygame.K_a:
                        player.move(-player.speed, 0)
                        player.auto_mode = False
                    elif event.key == pygame.K_d:
                        player.move(player.speed, 0)
                        player.auto_mode = False
                    elif event.key == pygame.K_SPACE:
                        player.auto_mode = not player.auto_mode  # Toggle auto - mode by pressing the spacebar

            if player.auto_mode:
                player.auto_move(game_map)

            game_map.move_monsters()
            player.check_collision(game_map)
            player.update_invincibility()

            screen.fill((0, 0, 0))
            game_map.draw()
            player.draw()

            # Display health, score, and level，将颜色改为绿色
            health_text = font.render(f"Health: {player.health}", 1, GREEN)
            score_text = font.render(f"Score: {player.score}", 1, GREEN)
            level_text = font.render(f"Level: {level}", 1, GREEN)
            auto_text = font.render(f"Auto Mode: {'On' if player.auto_mode else 'Off'}", 1, GREEN)
            screen.blit(health_text, (10, 10))
            screen.blit(score_text, (10, 40))
            screen.blit(level_text, (10, 70))
            screen.blit(auto_text, (10, 100))

            pygame.display.flip()

            if player.health <= 0:
                running = False
                if show_game_over_screen(player.score):
                    level = 1
                else:
                    return
            elif len(game_map.gold_coins) == 0:
                level += 1
                break

if __name__ == "__main__":
    main()