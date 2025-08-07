import pygame
import numpy as np
from convert_char_to_pixels import char_to_pixels
import random
import matplotlib.colors

# Grid size
GRID_SIZE_X = 64 * 2
GRID_SIZE_Y = 48
CELL_SIZE = 30

RULE_BUTTON_WIDTH = CELL_SIZE * 4
RULE_BUTTON_HEIGHT = CELL_SIZE * 4
RULE_MARGIN = 2
RULE_Y_OFFSET = GRID_SIZE_Y * CELL_SIZE + 20
LAST_RULE = -1

WINDOW_SIZE_X = GRID_SIZE_X * CELL_SIZE
WINDOW_SIZE_Y = RULE_Y_OFFSET + RULE_BUTTON_HEIGHT * 2 + 20

# Colors
DEAD_COLOR = (30, 30, 30)
ALIVE_COLOR = (0, 200, 0)
SPECIAL_COLOR = (0, 0, 200)
SPECIAL2_COLOR = (200, 100, 0)
GRID_COLOR = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)
BUTTON_ON = (0, 180, 180)
BUTTON_OFF = (60, 60, 60)
FONT = '../../impact.ttf'
# Rule state
BIRTH = {3,4,6} #0178 #346        #2378  #34
SURVIVE = {1,3,6,7,8} #067 #13678 #34568 #135679
# 08 - 34678

pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE_X, WINDOW_SIZE_Y))
pygame.display.set_caption("Game of Life with Rules")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 14)

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

def hex_to_rgb(hex):
  return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

# Example: from DEAD_COLOR to ALIVE_COLOR to SPECIAL2_COLOR
COLOR_ARRAY = color_gradient((0,20,0), ALIVE_COLOR, 8) + color_gradient(ALIVE_COLOR, SPECIAL2_COLOR, 7)[1:]
#HEX_ARRAY = ['FBF8CC', 'FFF8DC', 'FFF0F5', 'FFE4E1', 'FFDAB9', 'FFC0CB', 'FFA07A', 'FF7F50', 'FF6347', 'FF4500', 'FF0000', 'DC143C', 'B22222', '8B0000', '800000', 'FFFFFF']
#HEX_ARRAY = ['FBF8CC', 'FDE4CF', 'FFCFD2', 'F1C0E8', 'CFBAF0', 'A3C4F3', '90DBF4', '8EECF5', '98F5E1', 'B9FBC0', 'B9FFC0', 'B9FFDD', 'B9FFEE', 'B9FFFF', '800000', 'FFFFFF']
#HEX_ARRAY = ['D9ED92', 'B5E48C','99D98C','76C893','52B69A','34A0A4','168AAD','1A759F','1E6091','184E77','0F4C75','023E8A','03045E','FFFFFF']
HEX_ARRAY = ['FFBA08', '03073E', '370617', '6A040F', '9D0208', 'D00000', 'DC2F02', 'E85D04', 'F48C06', 'FAA307', 'FFBA08']
HEX_ARRAY.reverse()        
COLOR_ARRAY = [hex_to_rgb(hex_color) for hex_color in HEX_ARRAY]
print(COLOR_ARRAY)

def draw_grid(surface, grid):
    surface.fill(DEAD_COLOR)
    for y in range(GRID_SIZE_Y):    
        for x in range(GRID_SIZE_X):
            rect = pygame.Rect(x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE)
            val = grid[y][x]
            if val > 0 and val < len(COLOR_ARRAY):
                pygame.draw.rect(surface, COLOR_ARRAY[val-1], rect)
            elif val >= len(COLOR_ARRAY):
                pygame.draw.rect(surface, COLOR_ARRAY[-1], rect)
                # print(f"Value {val} exceeds color array bounds.")
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

def initialize_grid_with_text(text, grid_size_x=GRID_SIZE_X, grid_size_y=GRID_SIZE_Y, font_path=FONT, font_size=12):
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
grid = initialize_grid_with_text("HeiChips", grid_size_x=GRID_SIZE_X, grid_size_y=GRID_SIZE_Y, font_path=FONT, font_size=15)

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
                grid = initialize_grid_with_text("HeiChips", grid_size_x=GRID_SIZE_X, grid_size_y=GRID_SIZE_Y, font_path=FONT, font_size=15)
            elif event.key == pygame.K_r:
                randomize_rules()

        elif pygame.mouse.get_pressed()[0]:
            mx, my = pygame.mouse.get_pos()
            x, y = mx // CELL_SIZE, my // CELL_SIZE
            if y < GRID_SIZE_Y:
                grid[y][x] = 1
            else:
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
