import pygame
import numpy as np
from convert_char_to_pixels import char_to_pixels
import random

# Grid size
GRID_SIZE_X = 64
GRID_SIZE_Y = 48
CELL_SIZE = 10

RULE_BUTTON_WIDTH = CELL_SIZE * 4
RULE_BUTTON_HEIGHT = CELL_SIZE * 4
RULE_MARGIN = 2
RULE_Y_OFFSET = GRID_SIZE_Y * CELL_SIZE + 20
LAST_RULE = -1

WINDOW_SIZE_X = GRID_SIZE_X * CELL_SIZE
WINDOW_SIZE_Y = RULE_Y_OFFSET + RULE_BUTTON_HEIGHT * 2 + 20  # room for two rule rows

# Colors
DEAD_COLOR = (30, 30, 30)
ALIVE_COLOR = (0, 200, 0)
SPECIAL_COLOR = (0, 0, 200)
SPECIAL2_COLOR = (200, 100, 0)
GRID_COLOR = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)
BUTTON_ON = (0, 180, 180)
BUTTON_OFF = (60, 60, 60)

# Rule state
BIRTH = {3,4,6} #0178 #346
SURVIVE = {1,3,6,7,8} #067 #13678

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE_X, WINDOW_SIZE_Y))
pygame.display.set_caption("Game of Life with Rules")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 16)

# Initialize grid
grid = np.zeros((GRID_SIZE_Y, GRID_SIZE_X), dtype=int)
running = False

# Initialize color gradient for cell values 0-14
def color_gradient(start_color, end_color, steps):
    gradient = []
    for i in range(steps):
        r = int(start_color[0] + (end_color[0] - start_color[0]) * i / (steps - 1))
        g = int(start_color[1] + (end_color[1] - start_color[1]) * i / (steps - 1))
        b = int(start_color[2] + (end_color[2] - start_color[2]) * i / (steps - 1))
        gradient.append((r, g, b))
    return gradient

# Example: from DEAD_COLOR to ALIVE_COLOR to SPECIAL2_COLOR
COLOR_ARRAY = color_gradient(DEAD_COLOR, ALIVE_COLOR, 8) + color_gradient(ALIVE_COLOR, SPECIAL2_COLOR, 7)[1:]

def draw_grid(surface, grid):
    surface.fill(DEAD_COLOR)
    for y in range(GRID_SIZE_Y):
        for x in range(GRID_SIZE_X):
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            val = grid[y][x]
            if val > 0 and val < len(COLOR_ARRAY):
                pygame.draw.rect(surface, COLOR_ARRAY[val], rect)
            elif val >= len(COLOR_ARRAY):
                pygame.draw.rect(surface, COLOR_ARRAY[-1], rect)
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)

def update_grid(grid):
    new_grid = np.copy(grid)
    for y in range(GRID_SIZE_Y):
        for x in range(GRID_SIZE_X):
            # Count neighbors as cells with value >= 1, excluding the center cell
            neighbors = np.count_nonzero(
                grid[max(y-1, 0):min(y+2, GRID_SIZE_Y),
                     max(x-1, 0):min(x+2, GRID_SIZE_X)] >= 1
            )
            self = grid[y][x]
            # if grid[y][x] >= 1:
            #     neighbors -= 1  # Exclude the center cell if it's alive
            if self > 0:
                new_grid[y][x] = self + 1 if neighbors in SURVIVE else 0
            else:
                new_grid[y][x] = 1 if neighbors in BIRTH else 0
    return new_grid

def initialize_grid_with_text(text, grid_size_x=64, grid_size_y=48, font_path='comic.ttf', font_size=12):
    pixel_array = char_to_pixels(text, path=font_path, fontsize=font_size)
    grid = np.zeros((grid_size_y, grid_size_x), dtype=int)
    h, w = pixel_array.shape
    if h > grid_size_y or w > grid_size_x:
        raise ValueError(f"Text too large to fit in {grid_size_x}x{grid_size_y} grid (got {w}x{h})")
    start_y = (grid_size_y - h) // 2
    start_x = (grid_size_x - w) // 2
    grid[start_y:start_y + h, start_x:start_x + w] = pixel_array
    return grid

def draw_rule_buttons(surface, rule_set, label, y_offset):
    label_surface = font.render(label, True, TEXT_COLOR)
    surface.blit(label_surface, (5, y_offset - 20))
    buttons = []
    for i in range(10):
        rect = pygame.Rect(50 + i * (RULE_BUTTON_WIDTH + RULE_MARGIN), y_offset,
                           RULE_BUTTON_WIDTH, RULE_BUTTON_HEIGHT)
        color = BUTTON_ON if i in rule_set else BUTTON_OFF
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, TEXT_COLOR, rect, 1)
        text = font.render(str(i), True, TEXT_COLOR)
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)
        buttons.append((rect, i))
    return buttons

def handle_rule_click(mouse_pos, buttons, rule_set):
    global LAST_RULE
    for rect, val in buttons:
        if rect.collidepoint(mouse_pos):
            if val == LAST_RULE: 
                return False  # Ignore clicks on the last rule button
            LAST_RULE = val
            if val in rule_set:
                rule_set.remove(val)
            else:
                rule_set.add(val)
            return True
    return False

def randomize_rules():
    global BIRTH, SURVIVE
    BIRTH = set(random.sample(range(9), random.randint(0, 5)))
    SURVIVE = set(random.sample(range(9), random.randint(0, 5)))

# Load initial pattern
grid = initialize_grid_with_text("HeiChips", grid_size_x=64, grid_size_y=48, font_path="comic.ttf", font_size=15)

# Main loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                running = not running
            elif event.key == pygame.K_c:
                grid.fill(0)
            elif event.key == pygame.K_h:
                grid = initialize_grid_with_text("HeiChips", grid_size_x=64, grid_size_y=48, font_path="comic.ttf", font_size=15)
            elif event.key == pygame.K_r:
                randomize_rules()

        elif pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            x, y = mx // CELL_SIZE, my // CELL_SIZE
            if y < GRID_SIZE_Y:
                grid[y][x] = 1
            else:
                # Rule clicks
                if handle_rule_click((mx, my), birth_buttons, BIRTH): pass
                if handle_rule_click((mx, my), survive_buttons, SURVIVE): pass

        elif pygame.mouse.get_pressed()[2]:
            mx, my = pygame.mouse.get_pos()
            x, y = mx // CELL_SIZE, my // CELL_SIZE
            if y < GRID_SIZE_Y:
                grid[y][x] = 0

    if running:
        grid = update_grid(grid)

    draw_grid(screen, grid)
    birth_buttons = draw_rule_buttons(screen, BIRTH, "BIRTH", RULE_Y_OFFSET)
    survive_buttons = draw_rule_buttons(screen, SURVIVE, "SURVIVE", RULE_Y_OFFSET + RULE_BUTTON_HEIGHT + 10)
    pygame.display.flip()
    clock.tick(10)
