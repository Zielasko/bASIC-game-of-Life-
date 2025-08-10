import pygame
import numpy as np
from convert_char_to_pixels import char_to_pixels
import random
import matplotlib.colors
import os

# Grid size
GRID_SIZE_X = 64
GRID_SIZE_Y = 48
CELL_SIZE = 15

# Get display resolution and set cell size to fit screen
try:
    pygame.init()
    display_info = pygame.display.Info()
    screen_width = display_info.current_w
    
    if screen_width >= 2560:  # 4K or higher
        CELL_SIZE = 20
    elif screen_width >= 1920:  # Full HD
        CELL_SIZE = 15
    elif screen_width >= 1366:  # HD
        CELL_SIZE = 10
    else:  # Smaller screens
        CELL_SIZE = 8
except:
    # Fallback if display detection fails
    CELL_SIZE = 15

RULE_BUTTON_WIDTH = CELL_SIZE * 4
RULE_BUTTON_HEIGHT = CELL_SIZE * 4
RULE_TEXT_SIZE = CELL_SIZE * 2
RULE_MARGIN = 2
RULE_Y_OFFSET = GRID_SIZE_Y * CELL_SIZE + 20
AGE_LIMIT = 15
LAST_RULE = -1

WINDOW_SIZE_X = GRID_SIZE_X * CELL_SIZE
WINDOW_SIZE_Y = RULE_Y_OFFSET + RULE_BUTTON_HEIGHT * 2 + 20

# Colors
DEAD_COLOR = (30, 30, 30)
BACKGROUND_COLOR = (30, 30, 40)
ALIVE_COLOR = (0, 200, 0)
SPECIAL_COLOR = (0, 0, 200)
SPECIAL2_COLOR = (200, 100, 0)
GRID_COLOR = (50, 50, 50)
TEXT_COLOR = (255, 255, 255)
BUTTON_ON = (0, 180, 180)
BUTTON_OFF = (60, 60, 60)
#FONT = '../../impact.ttf'
# Rule state

RULE_PRESETS = [
    (set([3]), set([2, 3])),          # 0: Conway's Life B3/S23
    (set([0, 8]), set([3, 4, 6,7,8])),   # 1
    (set([3, 6]), set([2, 3])),      # 2: HighLife B36/S23
    (set([0, 7]), set([1,3,4])),   # 3
    (set([0]), set([1, 3, 5,7])),# B0 S1357 
    (set([1, 2, 5]), set([3, 5, 6])),# 5
    (set([2, 4]), set([4, 5, 6])),   # 6
    #(set([3, 6, 8]), set([2, 3, 4])),# 7
    (set([0,5,6]), set([1,9])), 
    (set([3, 4, 5]), set([2, 3, 4])),# 8
    (set([1,2,4,8]), set([0,1,3,8])),# 9
]
#B2467 S45678
AGE_RULE_PRESETS = [
    # 0:
    (set([3]), set([2, 3]), set([1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15]), set([1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 13, 14, 15])),
    
    # 1:
    (set([0, 8]), set([3, 4, 6, 7, 8]), set([1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15]), set([1, 2, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15])),
    
    # 2:
    (set([3, 6]), set([2, 3]), set([1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15]), set([1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15])),
    
    # 3:
    (set([0, 7]), set([1, 3, 4]), set([1, 2, 3, 4, 5, 6, 8, 9, 10, 12, 13, 14, 15]), set([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15])),
    
    # 4:
    (set([0]), set([1, 3, 5, 7]), set([1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 13, 14, 15]), set([1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])),
    
    # 5:
    (set([1, 2, 5]), set([3, 5, 6]), set([1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15]), set([1, 2, 3, 4, 5, 7, 8, 9, 10, 12, 13, 14, 15])),
    
    # 6:
    (set([2, 4]), set([4, 5, 6]), set([1, 2, 3, 4, 5, 6, 8, 9, 11, 12, 13, 14, 15]), set([1, 2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 15])),
    
    # 7:
    (set([0, 5, 6]), set([1, 9]), set([1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 14, 15]), set([2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])),
    
    # 8: gameboy shrinking window
    (set([0,1,2,3,7,8]), set([0,1,2,3,4,5,6]), set([1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]), set([1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15])),
    
    # 9:Droplets preset
    (set([1]), set([1,3,8]), set([1, 4, 6, 7, 8, 9, 11, 13, 14, 15]), set([2, 3, 4, 5, 6, 7, 8, 11, 12, 14])),
]

#Droplets
#Randomized rules: BIRTH=[1], SURVIVE=[1, 3, 8]
#Randomized age rules: BIRTH_AGE=[1, 4, 6, 7, 8, 9, 11, 13, 14, 15], SURVIVE_AGE=[2, 3, 4, 5, 6, 7, 8, 11, 12, 14]

#Randomized rules: BIRTH=[0, 1, 2, 7, 8], SURVIVE=[0, 6]
#Randomized age rules: BIRTH_AGE=[1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15], SURVIVE_AGE=[1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]


BIRTH = {0,8} #0178 #346        #2378  #34
SURVIVE = {3,4,6,7,8} #067 #13678 #34568 #135679
BIRTH_AGE = set() 
SURVIVE_AGE = set() 
BIRTH, SURVIVE = RULE_PRESETS[6]

def update_age_sets():
    """Update BIRTH_AGE and SURVIVE_AGE based on current AGE_LIMIT"""
    global BIRTH_AGE, SURVIVE_AGE
    BIRTH_AGE = set(range(1, AGE_LIMIT + 1))  # Age 0 does not exist
    SURVIVE_AGE = set(range(1, AGE_LIMIT + 1))

# Config menu state
show_config = False
config_font_size = 15
config_font_name = "impact"  # Default font name
config_font_bold = False  # Bold text setting
config_text = "HeiChips"  # Text to display in grid
config_palette = 0  # Selected color palette index
config_palette_reverse = True  # Whether to reverse the color palette
config_grid_x = GRID_SIZE_X
config_grid_y = GRID_SIZE_Y
config_cell_size = CELL_SIZE
config_fps = 10  # Frames per second for simulation
config_flicker_reduction = True  # Whether to enable dead pixel flickering reduction for Birth 0 rules
config_age_influence = False  # Whether to enable age-based influence on birth/survive rules
config_age_resolution = 4  # Number of bits for age attribute
input_active = None  # Track which input field is active
input_text = ""
show_font_popup = False
font_popup_scroll = 0

# prevent clicking multiple times
last_click_time = 0
CLICK_DELAY = 250  # Milliseconds

screen = pygame.display.set_mode((WINDOW_SIZE_X, WINDOW_SIZE_Y))
pygame.display.set_caption("Bag O' Life - Cellular Automaton Design Space Exploration")
clock = pygame.time.Clock()

# Get available system fonts
available_fonts = sorted(pygame.font.get_fonts())
# print(f"Available fonts: {available_fonts}")
if not available_fonts:
    print("[ERROR] No system fonts found.")
    available_fonts = ["arial", "helvetica", "times", "courier"]  # Fallback fonts

# Try to use Impact font, fallback to other fonts if not available
font = None
try:
    if config_font_name in available_fonts:
        font = pygame.font.SysFont(config_font_name, 14)
        if pygame.font.match_font(config_font_name) is None:
            print(f"[ERROR] {config_font_name} font is available but could not be loaded.")
    else:
        print(f"[WARNING] {config_font_name} font not found, using default font.")
        # Impact not available, try alternatives
        for fallback_font in ["Impact", "comicsansms", "Arial Black", "Helvetica Bold", "Arial", "Sans"]:
            try:
                font = pygame.font.SysFont(fallback_font, 14)
                config_font_name = fallback_font
                print(f"Using fallback font: {fallback_font}")
                break
            except:
                continue
except Exception as e:
    print(f"[ERROR] Could not load any standard font, please install a font like Impact or Arial. {e}")


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

# Color palettes
COLOR_PALETTES = {
    0: {
        "name": "Rainbow",
        "colors": [
            'FF0000', # Red
            'FF4000', # Red-Orange
            'FF8000', # Orange
            'FFBF00', # Yellow-Orange
            'FFFF00', # Yellow
            'BFFF00', # Yellow-Green
            '80FF00', # Green-Yellow
            '40FF00', # Yellowish Green
            '00FF00', # Green
            '00FF80', # Green-Cyan
            '00FFBF', # Cyan-Green
            '00FFFF', # Cyan
            '0080FF', # Blue-Cyan
            '0000FF', # Blue
            '4B0082', # Indigo
            '8F00FF', # Violet
        ]
    },
    1: {
        "name": "Game Boy",
        "colors": ['9BBC0F', '332c50', '332c50', '8BAC0F', '306230', '0F380F', '0F380F', '2D5A2D', '4F7F4F', '8BAC0F', '9BBC0F', 'ADCFAD', 'e0dbcd', 'a89f94', '706b66', '2b2b26']
    },
    2: {
        "name": "Fire",
        "colors": ['FFBA08', '03073E', '370617', '6A040F', '9D0208', 'D00000', 'DC2F02', 'E85D04', 'F48C06', 'FAA307', 'FFBA08']
    },
    3: {
        "name": "turquoise",
        "colors": ['D9ED92', 'B5E48C', '99D98C', '76C893', '52B69A', '34A0A4', '168AAD', '1A759F', '1E6091', '184E77', '0F4C75', '023E8A', '03045E', '001D3D', '000814', '30FFFF']
    },
    6: {
        "name": "Pastel",
        "colors": ['FBF8CC', 'FDE4CF', 'FFCFD2', 'F1C0E8', 'CFBAF0', 'A3C4F3', '90DBF4', '8EECF5', '98F5E1', 'B9FBC0', 'B9FFC0', 'B9FFDD', 'B9FFEE', 'B9FFFF', '800000', 'FFFFFF']
    },
    4: {
        "name": "Green-Blue",
        "colors": ['D9ED92', 'B5E48C','99D98C','76C893','52B69A','34A0A4','168AAD','1A759F','1E6091','184E77','0F4C75','023E8A','03045E','FFFFFF']
    },
    5: {
        "name": "Gradient",
        "colors": None  # Will use color_gradient function
    },
    7: {
        "name": "Purple", 
        "colors": ['F72585', 'B5179E', '7209B7', '560BAD', '480CA8', '3A0CA3', '3F37C9', '4361EE', '4895EF', '4CC9F0', '7209B7', '480CA8', '3A0CA3', '240046', '10002B', 'FFFF30']
    },
    8: {
        "name": "Watermelon",
        "colors": ['EF476F', 'FFD166', '06D6A0', '118AB2', '073B4C', 'F72C25', 'F8961E', 'F9C74F', '90E0EF', '0077B6', '023047', '8ECAE6', '219EBC', '126782', '0A4D68', 'DDFFFF']
    },
    9: {
        "name": "Ocean Blue",
        "colors": ['03045E', '023E8A', '0077B6', '0096C7', '00B4D8', '48CAE4', '90E0EF', 'ADE8F4', 'CAF0F8', 'E0F4FF', '87CEEB', '5F9EA0', '4682B4', '1E90FF', '0000CD', 'DDFFFF']
    },
    10: {
        "name": "Warm",
        "colors": ['FBF8CC', 'FFF8DC', 'FFF0F5', 'FFE4E1', 'FFDAB9', 'FFC0CB', 'FFA07A', 'FF7F50', 'FF6347', 'FF4500', 'FF0000', 'DC143C', 'B22222', '8B0000', '800000', 'FFFFFF']
    },
}

def update_color_array(log=True):
    """Update COLOR_ARRAY based on selected palette and age resolution"""
    global COLOR_ARRAY, DEAD_COLOR, AGE_LIMIT
    
    # Update AGE_LIMIT based on age resolution
    AGE_LIMIT = (2 ** config_age_resolution) - 1
    
    update_age_sets()
    
    palette = COLOR_PALETTES[config_palette]
    
    if palette["colors"] is None:  # Gradient palette
        COLOR_ARRAY = color_gradient((0,20,0), ALIVE_COLOR, 8) + color_gradient(ALIVE_COLOR, SPECIAL2_COLOR, 7)[1:]
        if AGE_LIMIT > 15:
            COLOR_ARRAY = color_gradient((0,20,0), ALIVE_COLOR, AGE_LIMIT//2) + color_gradient(ALIVE_COLOR, SPECIAL2_COLOR, AGE_LIMIT//2 + 1)[1:]
    else:
        hex_colors = palette["colors"].copy()
        if config_palette_reverse:
            hex_colors.reverse()
        base_colors = [hex_to_rgb(hex_color) for hex_color in hex_colors]
        
        # interpolate colors if AGE_LIMIT exceeds hardcoded palette
        if config_age_influence != 4 and AGE_LIMIT > len(base_colors) - 1:
            COLOR_ARRAY = interpolate_colors(base_colors, AGE_LIMIT)
        else:
            COLOR_ARRAY = base_colors
        
        # If Birth 0 is active and flicker reduction is enabled, set dead color to reduced first color
        # This should reduce flickering when cells toggle each frame
        if log:
            print(f"[INFO] Using color palette: {palette['name']}")
            # Print palette to the console
            for color in COLOR_ARRAY:
                # ANSI escape code for RGB background
                r, g, b = color
                print(f"\033[48;2;{r};{g};{b}m  \033[0m", end="")
            print()
        if 0 in BIRTH and len(COLOR_ARRAY) > 0 and config_flicker_reduction:
            print("[INFO] BIRTH 0 is active, changing dead pixel color to reduce flickering")
            first_color = COLOR_ARRAY[0]
            # Reduce each RGB component by 20% (multiply by 0.8)
            reduced_color = tuple(max(0, int(c * 0.6)) for c in first_color)
            DEAD_COLOR = reduced_color
            r, g, b = reduced_color
            print(f"\033[48;2;{r};{g};{b}m  \033[0m", end="")
            print()
        else:
            DEAD_COLOR = (30, 30, 30)

def interpolate_colors(base_colors, target_count):
    """Interpolate colors to create a palette with target_count colors"""
    print("number of colors in palette do not match AGE_LIMIT -> interpolating colors")
    if target_count <= len(base_colors):
        return base_colors[:target_count]
    
    result = []
    # Calculate how many interpolated colors we need between each pair
    segments = len(base_colors) - 1
    colors_per_segment = target_count // segments
    remaining = target_count % segments
    
    for i in range(segments):
        start_color = base_colors[i]
        end_color = base_colors[i + 1]
        
        # Add extra color to some segments if we have remainder
        segment_colors = colors_per_segment + (1 if i < remaining else 0)
        
        # Generate interpolated colors for this segment
        for j in range(segment_colors):
            if j == 0:
                result.append(start_color)
            else:
                # Interpolate between start and end
                ratio = j / segment_colors
                r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
                g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
                b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
                result.append((r, g, b))
    
    # Add the final color
    if len(result) < target_count:
        result.append(base_colors[-1])
    
    return result[:target_count]

# Initialize with default palette
update_color_array()
#print(COLOR_ARRAY)

def can_click():
    """Check if enough time has passed since the last click to allow a new click"""
    global last_click_time
    current_time = pygame.time.get_ticks()
    if current_time - last_click_time >= CLICK_DELAY:
        last_click_time = current_time
        return True
    return False

def draw_grid(surface, grid):
    surface.fill(BACKGROUND_COLOR)
    
    # Fill only the game area with dead color
    game_area_rect = pygame.Rect(0, 0, GRID_SIZE_X * CELL_SIZE, GRID_SIZE_Y * CELL_SIZE)
    pygame.draw.rect(surface, DEAD_COLOR, game_area_rect)
    
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
            self = grid[y][x]
            
            if config_age_influence:
                # Age-based rule: count neighbors if their age is in BIRTH_AGE and SURVIVE_AGE
                birth_neighbors = 0
                survive_neighbors = 0
                
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        # if dy == 0 and dx == 0:  # Skip center cell
                        #     continue
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < GRID_SIZE_Y and 0 <= nx < GRID_SIZE_X:
                            neighbor_age = grid[ny][nx]
                            if neighbor_age > 0:  # Alive neighbor
                                # Check if neighbor age is in BIRTH_AGE set
                                if neighbor_age in BIRTH_AGE:
                                    birth_neighbors += 1
                                # Check if neighbor age is in SURVIVE_AGE set
                                if neighbor_age in SURVIVE_AGE:
                                    survive_neighbors += 1
                
                if self > 0:
                    # Cell is alive, check survival with age-filtered neighbors
                    new_grid[y][x] = min(self + 1 if survive_neighbors in SURVIVE else 0, AGE_LIMIT)
                else:
                    # Cell is dead, check birth with age-filtered neighbors
                    new_grid[y][x] = 1 if birth_neighbors in BIRTH else 0
            else:
                # Default logic: Count neighbors as cells with value >= 1
                neighbors = np.count_nonzero(
                    grid[max(y-1, 0):min(y+2, GRID_SIZE_Y),
                         max(x-1, 0):min(x+2, GRID_SIZE_X)] >= 1
                )
                # Exclude the center cell from neighbor count
                # if self > 0:
                #     neighbors -= 1
                
                if self > 0:
                    new_grid[y][x] = self + 1 if neighbors in SURVIVE else 0
                else:
                    new_grid[y][x] = 1 if neighbors in BIRTH else 0
    return new_grid

def initialize_grid_with_text(text, grid_size_x=GRID_SIZE_X, grid_size_y=GRID_SIZE_Y, font_size=12, font_name=None, bold=False):
    pixel_array = char_to_pixels(text, fontsize=font_size, font_name=font_name, bold=bold)

    #pixel_array = np.where(pixel_array != 0, 1, 0) # map all nonzero pixels to 1
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
        
        # Use RULE_TEXT_SIZE for the numbers in the buttons
        rule_font = pygame.font.SysFont(config_font_name, RULE_TEXT_SIZE)
        text = rule_font.render(str(i), True, TEXT_COLOR)
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)
        buttons.append((rect, i))
    return buttons

def draw_age_rule_buttons(surface, rule_set, label, x_offset, y_offset, vertical=False):
    """Draw age rule buttons for values 1-15"""
    label_surface = font.render(label, True, TEXT_COLOR)
    
    # Reduce age rule button size by 20%
    age_button_width = int(RULE_BUTTON_WIDTH * 0.8)
    age_button_height = int(RULE_BUTTON_HEIGHT * 0.8)
    age_text_size = int(RULE_TEXT_SIZE * 0.8)
    
    if vertical:
        # Vertical layout: two columns of buttons
        surface.blit(label_surface, (x_offset, y_offset - 20))
        buttons = []
        # Create 16 buttons (1-16) in a 2-column layout for symmetry
        for i in range(1, 17):
            col = (i+1) % 2  # Column 0 or 1
            row = (i-1) // 2  # Row number
            
            rect = pygame.Rect(x_offset + col * (age_button_width + RULE_MARGIN), 
                             y_offset + row * (age_button_height + RULE_MARGIN),
                             age_button_width, age_button_height)
            
            if i == 16:
                # Age 0 is invalid - draw as disabled/empty box
                color = (30, 30, 30)  # Dark gray for disabled
                pygame.draw.rect(surface, BUTTON_ON, rect)
                pygame.draw.rect(surface, TEXT_COLOR, rect, 1)  # Darker border

                rule_font = pygame.font.SysFont(config_font_name, age_text_size)
                # text = rule_font.render("X", True, (100, 100, 100))  # Gray X to show invalid
                # text_rect = text.get_rect(center=rect.center)
                # surface.blit(text, text_rect)
                # Don't add to clickable buttons
            else:
                color = BUTTON_ON if i in rule_set else BUTTON_OFF
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, TEXT_COLOR, rect, 1)
                
                rule_font = pygame.font.SysFont(config_font_name, age_text_size)
                text = rule_font.render(str(i), True, TEXT_COLOR)
                text_rect = text.get_rect(center=rect.center)
                surface.blit(text, text_rect)
                buttons.append((rect, i))
    else:
        # Horizontal layout: spread across width (might need to wrap)
        surface.blit(label_surface, (5, y_offset - 20))
        buttons = []
        
        # Create 16 buttons (0-15) in horizontal rows for symmetry
        buttons_per_row = min(16, (WINDOW_SIZE_X - 100) // (age_button_width + RULE_MARGIN))
        
        for i in range(1, 17):
            col = i % buttons_per_row
            row = i // buttons_per_row
            
            rect = pygame.Rect(50 + col * (age_button_width + RULE_MARGIN), 
                             y_offset + row * (age_button_height + RULE_MARGIN),
                             age_button_width, age_button_height)
            
            if i ==16:
                # Age 0 is invalid - draw as disabled/empty box
                color = (30, 30, 30)  # Dark gray for disabled
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, (60, 60, 60), rect, 1)  # Darker border
                
                rule_font = pygame.font.SysFont(config_font_name, age_text_size)
                text = rule_font.render("X", True, (100, 100, 100))  # Gray X to show invalid
                text_rect = text.get_rect(center=rect.center)
                surface.blit(text, text_rect)
                # Don't add to clickable buttons
            else:
                color = BUTTON_ON if i in rule_set else BUTTON_OFF
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, TEXT_COLOR, rect, 1)
                
                rule_font = pygame.font.SysFont(config_font_name, age_text_size)
                text = rule_font.render(str(i), True, TEXT_COLOR)
                text_rect = text.get_rect(center=rect.center)
                surface.blit(text, text_rect)
                buttons.append((rect, i))
    
    return buttons

def handle_rule_click(mouse_pos, birth_buttons, survive_buttons, birth_age_buttons=None, survive_age_buttons=None):
    global LAST_RULE, BIRTH, SURVIVE, BIRTH_AGE, SURVIVE_AGE
    
    if not can_click():
        return False
    
    for rect, val in birth_buttons:
        if rect.collidepoint(mouse_pos):
            if val in BIRTH:
                BIRTH.remove(val)
            else:
                BIRTH.add(val)
            return True
    
    # Check survive buttons if no birth button was clicked
    for rect, val in survive_buttons:
        if rect.collidepoint(mouse_pos):
            if val in SURVIVE:
                SURVIVE.remove(val)
            else:
                SURVIVE.add(val)
            return True
    
    # Check birth age buttons if provided
    if birth_age_buttons:
        for rect, val in birth_age_buttons:
            if rect.collidepoint(mouse_pos):
                if val in BIRTH_AGE:
                    BIRTH_AGE.remove(val)
                else:
                    BIRTH_AGE.add(val)
                return True
    
    # Check survive age buttons if provided
    if survive_age_buttons:
        for rect, val in survive_age_buttons:
            if rect.collidepoint(mouse_pos):
                if val in SURVIVE_AGE:
                    SURVIVE_AGE.remove(val)
                else:
                    SURVIVE_AGE.add(val)
                return True
    
    return False

def randomize_rules():
    global BIRTH, SURVIVE, BIRTH_AGE, SURVIVE_AGE
    BIRTH = set(random.sample(range(9), random.randint(0, 5)))
    SURVIVE = set(random.sample(range(9), random.randint(0, 5)))
    
    # Also randomize age rules if age influence is enabled
    if config_age_influence:
        # Randomize age sets with ages 1-15 with high probability of keeping most ages
        age_range = list(range(1, 16))  # Use full 1-15 range
        
        # High chance (80%) to keep almost all ages (remove only 0-3 random ages)
        if random.random() < 0.8:
            # Keep most ages, remove only 0-3 random ones
            ages_to_remove = random.randint(0, 3)
            BIRTH_AGE = set(age_range)
            SURVIVE_AGE = set(age_range)
            
            if ages_to_remove > 0:
                birth_remove = random.sample(age_range, min(ages_to_remove, len(age_range)))
                survive_remove = random.sample(age_range, min(ages_to_remove, len(age_range)))
                BIRTH_AGE -= set(birth_remove)
                SURVIVE_AGE -= set(survive_remove)
        else:
            # Lower chance (20%) for more selective age rules (keep 5-10 ages)
            birth_count = random.randint(5, 10)
            survive_count = random.randint(5, 10)
            BIRTH_AGE = set(random.sample(age_range, birth_count))
            SURVIVE_AGE = set(random.sample(age_range, survive_count))
        
        print(f"Randomized rules: BIRTH={sorted(BIRTH)}, SURVIVE={sorted(SURVIVE)}")
        print(f"Randomized age rules: BIRTH_AGE={sorted(BIRTH_AGE)}, SURVIVE_AGE={sorted(SURVIVE_AGE)}")
    else:
        print(f"Randomized rules: BIRTH={sorted(BIRTH)}, SURVIVE={sorted(SURVIVE)}")
    
    #update COLOR_ARRAY to handle cases where BIRTH 0 is an active rule
    update_color_array(False)

def update_window_size():
    global screen, WINDOW_SIZE_X, WINDOW_SIZE_Y, RULE_Y_OFFSET
    WINDOW_SIZE_X = GRID_SIZE_X * CELL_SIZE
    RULE_Y_OFFSET = GRID_SIZE_Y * CELL_SIZE + 20
    
    # Calculate space needed for age rule buttons if age influence is enabled
    if config_age_influence:
        # Age rule buttons are 20% smaller
        age_button_width = int(RULE_BUTTON_WIDTH * 0.8)
        age_button_height = int(RULE_BUTTON_HEIGHT * 0.8)
        
        # Calculate horizontal layout requirements (16 buttons in a row)
        horizontal_width_needed = 50 + 16 * (age_button_width + RULE_MARGIN) + 50
        
        # Calculate height for horizontal layout (2 rows of age buttons + existing rules)
        horizontal_height_needed = RULE_Y_OFFSET + RULE_BUTTON_HEIGHT * 2 + 40 + age_button_height * 2 + 60  # existing rules + age rules + margins
        
        # Get display height to check if window would fit on screen
        try:
            display_info = pygame.display.Info()
            display_height = display_info.current_h
        except:
            display_height = 1080  # Fallback
        
        # Check if horizontal layout is feasible
        horizontal_fits_width = WINDOW_SIZE_X >= horizontal_width_needed
        horizontal_fits_height = horizontal_height_needed <= (display_height - 100)  # 100px margin for taskbar/decorations
        
        if horizontal_fits_width and horizontal_fits_height:
            # Use horizontal layout at the bottom
            WINDOW_SIZE_Y = horizontal_height_needed
        else:
            # Use vertical layout on the right side
            min_width_for_vertical = GRID_SIZE_X * CELL_SIZE + 200  # Need space for 2 columns of buttons
            WINDOW_SIZE_X = max(WINDOW_SIZE_X, min_width_for_vertical)
            WINDOW_SIZE_Y = RULE_Y_OFFSET + RULE_BUTTON_HEIGHT * 2 + 20
    else:
        WINDOW_SIZE_Y = RULE_Y_OFFSET + RULE_BUTTON_HEIGHT * 2 + 20
    
    # Center the window on screen
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    screen = pygame.display.set_mode((WINDOW_SIZE_X, WINDOW_SIZE_Y))

def update_font():
    global font
    font = pygame.font.SysFont(config_font_name, 15)

def draw_help_box(surface):
    # Calculate position to the right of the rule buttons
    help_x = 50 + 10 * (RULE_BUTTON_WIDTH + RULE_MARGIN) + 20  # Right of the last rule button + margin
    
    help_y = RULE_Y_OFFSET
    help_height = RULE_BUTTON_HEIGHT * 2 + 10  # Same height as both rule sections
    help_width = max(100, help_height)
    
    # Only draw if there's enough space
    if help_width > 100:  # Minimum width check
        # Draw background box
        pygame.draw.rect(surface, (40, 40, 40), (help_x, help_y, help_width, help_height))
        pygame.draw.rect(surface, TEXT_COLOR, (help_x, help_y, help_width, help_height), 2)
        
        # Help text
        help_texts = [
            "CONTROLS:",
            "",
            "ESC - Menu",
            "SPACE - Play/Pause",
            "C - Clear grid",
            "H - Reset to text",
            "R - Random rules",
            "0-9 - Rule presets",
            "",
            "Age Rules: " + ("ON" if config_age_influence else "OFF"),
        ]
        
        # Render text lines
        line_height = 15
        total_text_height = len([t for t in help_texts if t != ""]) * line_height  # Count non-empty lines
        start_y = help_y + (help_height - total_text_height + line_height) // 2  # Center vertically
        
        # Pre-render all text surfaces and find the widest line
        max_width = 0
        help_font = pygame.font.SysFont(config_font_name, 12)
        rendered_lines = []
        
        for text_line in help_texts:
            if text_line != "":
                if text_line == "CONTROLS:":
                    text_surface = help_font.render(text_line, True, (255, 255, 0))
                else:
                    text_surface = help_font.render(text_line, True, TEXT_COLOR)
                rendered_lines.append(text_surface)
                max_width = max(max_width, text_surface.get_width())
            else:
                rendered_lines.append(None)  # Placeholder for empty lines
        
        # Calculate left-aligned start position that centers the text block
        text_start_x = help_x + (help_width - max_width) // 2
        text_y = start_y
        
        for i, text_surface in enumerate(rendered_lines):
            if text_y + line_height < help_y + help_height - 10:  # Check if text fits
                if text_surface is None:
                    # Skip empty lines but still advance position
                    text_y += line_height // 2
                    continue
                else:
                    # Use the pre-rendered surface
                    surface.blit(text_surface, (text_start_x, text_y))
                    text_y += line_height

def draw_font_popup(surface):
    global show_font_popup, font_popup_scroll
    
    # Font popup dimensions
    popup_width = min(600, int(WINDOW_SIZE_X * 0.9))
    popup_height = min(500, int(WINDOW_SIZE_Y * 0.8))
    popup_x = (WINDOW_SIZE_X - popup_width) // 2
    popup_y = (WINDOW_SIZE_Y - popup_height) // 2
    
    # Semi-transparent overlay
    overlay = pygame.Surface((WINDOW_SIZE_X, WINDOW_SIZE_Y))
    overlay.set_alpha(200)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))
    
    # Popup background
    pygame.draw.rect(surface, (50, 50, 50), (popup_x, popup_y, popup_width, popup_height))
    pygame.draw.rect(surface, TEXT_COLOR, (popup_x, popup_y, popup_width, popup_height), 2)
    
    # Title
    title = font.render("Select Font", True, TEXT_COLOR)
    surface.blit(title, (popup_x + 20, popup_y + 10))
    
    # Close button
    close_rect = pygame.Rect(popup_x + popup_width - 30, popup_y + 5, 25, 25)
    pygame.draw.rect(surface, (180, 0, 0), close_rect)
    pygame.draw.rect(surface, TEXT_COLOR, close_rect, 1)
    close_text = font.render("X", True, TEXT_COLOR)
    close_text_rect = close_text.get_rect(center=close_rect.center)
    surface.blit(close_text, close_text_rect)
    
    # Grid settings
    grid_start_y = popup_y + 50
    grid_height = popup_height - 100
    cols = 3
    rows_visible = 8
    item_width = (popup_width - 60) // cols
    item_height = 35
    
    # Scroll area
    scroll_area_height = rows_visible * item_height
    total_items = len(available_fonts)
    items_per_page = cols * rows_visible
    max_scroll = max(0, (total_items - items_per_page + cols - 1) // cols)
    
    # Scroll buttons
    scroll_up_rect = pygame.Rect(popup_x + popup_width - 40, grid_start_y, 30, 30)
    scroll_down_rect = pygame.Rect(popup_x + popup_width - 40, grid_start_y + scroll_area_height - 30, 30, 30)
    
    pygame.draw.rect(surface, BUTTON_OFF, scroll_up_rect)
    pygame.draw.rect(surface, BUTTON_OFF, scroll_down_rect)
    pygame.draw.rect(surface, TEXT_COLOR, scroll_up_rect, 1)
    pygame.draw.rect(surface, TEXT_COLOR, scroll_down_rect, 1)
    
    up_text = font.render("^", True, TEXT_COLOR)
    down_text = font.render("v", True, TEXT_COLOR)
    up_rect = up_text.get_rect(center=scroll_up_rect.center)
    down_rect = down_text.get_rect(center=scroll_down_rect.center)
    surface.blit(up_text, up_rect)
    surface.blit(down_text, down_rect)
    
    # Font grid
    font_buttons = []
    start_index = font_popup_scroll * cols
    end_index = min(start_index + items_per_page, total_items)
    
    for i, font_name in enumerate(available_fonts[start_index:end_index]):
        col = i % cols
        row = i // cols
        
        x = popup_x + 20 + col * item_width
        y = grid_start_y + row * item_height
        
        # Don't draw beyond visible area
        if row >= rows_visible:
            break
            
        item_rect = pygame.Rect(x, y, item_width - 5, item_height - 2)
        
        # Highlight current selection and hover
        if font_name == config_font_name:
            pygame.draw.rect(surface, BUTTON_ON, item_rect)
        elif item_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.draw.rect(surface, (80, 80, 80), item_rect)
        else:
            pygame.draw.rect(surface, BUTTON_OFF, item_rect)
        
        pygame.draw.rect(surface, TEXT_COLOR, item_rect, 1)
        
        # Font name text (truncate if too long)
        display_name = font_name[:15] + "..." if len(font_name) > 15 else font_name
        
        # Try to render in the actual font, fallback to default if failed
        try:
            actual_font = pygame.font.SysFont(font_name, 12)
            font_text = actual_font.render(display_name, True, TEXT_COLOR)
        except:
            # Fallback to default font if the font can't be loaded
            font_text = font.render(display_name, True, TEXT_COLOR)
            
        text_rect = font_text.get_rect(center=item_rect.center)
        surface.blit(font_text, text_rect)
        
        font_buttons.append((item_rect, font_name))
    
    # Instructions
    instruction_text = "Click a font to select - ESC to close"
    instruction = font.render(instruction_text, True, (180, 180, 180))
    surface.blit(instruction, (popup_x + 20, popup_y + popup_height - 30))
    
    return font_buttons, close_rect, scroll_up_rect, scroll_down_rect

def draw_config_menu(surface):
    global input_active, input_text
    
    # Semi-transparent overlay
    overlay = pygame.Surface((WINDOW_SIZE_X, WINDOW_SIZE_Y))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    surface.blit(overlay, (0, 0))
    
    # Config menu background - responsive to screen size
    menu_width = min(500, int(WINDOW_SIZE_X * 0.8))  # 80% of screen width, max 500px
    menu_height = max(500, int(WINDOW_SIZE_Y * 0.7))
    menu_x = (WINDOW_SIZE_X - menu_width) // 2
    menu_y = (WINDOW_SIZE_Y - menu_height) // 2
    
    pygame.draw.rect(surface, (60, 60, 60), (menu_x, menu_y, menu_width, menu_height))
    pygame.draw.rect(surface, TEXT_COLOR, (menu_x, menu_y, menu_width, menu_height), 2)
    
    # Title
    title = font.render("Configuration Menu", True, TEXT_COLOR)
    surface.blit(title, (menu_x + 20, menu_y + 10))
    
    # Input fields
    fields = [
        ("Font:", config_font_name, "font_name"),
        ("Bold:", "Yes" if config_font_bold else "No", "font_bold"),
        ("Font Size:", str(config_font_size), "font_size"),
        ("Text:", config_text, "text"),
        ("Palette:", COLOR_PALETTES[config_palette]["name"], "palette"),
        ("Reverse Palette:", "Yes" if config_palette_reverse else "No", "palette_reverse"),
        ("Flicker Reduction:", "Yes" if config_flicker_reduction else "No", "flicker_reduction"),
        ("Age Influence:", "Yes" if config_age_influence else "No", "age_influence"),
        ("Age Resolution:", str(config_age_resolution), "age_resolution"),
        ("Grid Width:", str(config_grid_x), "grid_x"),
        ("Grid Height:", str(config_grid_y), "grid_y"),
        ("Cell Size:", str(config_cell_size), "cell_size"),
        ("FPS:", str(config_fps), "fps")
    ]
    
    buttons = []
    y_pos = menu_y + 50
    field_height = 35  # Responsive field height
    input_width = max(180, menu_width - 200)  # Responsive input width
    
    for i, (label, value, field_id) in enumerate(fields):
        # Label
        label_surface = font.render(label, True, TEXT_COLOR)
        surface.blit(label_surface, (menu_x + 20, y_pos))
        
        if field_id == "font_name":
            # Font selection button
            input_rect = pygame.Rect(menu_x + 120, y_pos - 5, input_width, 25)
            
            pygame.draw.rect(surface, BUTTON_OFF, input_rect)
            pygame.draw.rect(surface, TEXT_COLOR, input_rect, 1)
            
            # Display current font
            display_text = config_font_name
            text_surface = font.render(display_text, True, TEXT_COLOR)
            surface.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
            
            # Button indicator
            button_text = font.render("...", True, TEXT_COLOR)
            surface.blit(button_text, (input_rect.right - 25, input_rect.y + 5))
            
            buttons.append((input_rect, field_id))
        elif field_id == "font_bold":
            # Bold toggle button
            input_rect = pygame.Rect(menu_x + 120, y_pos - 5, input_width, 25)
            
            color = BUTTON_ON if config_font_bold else BUTTON_OFF
            pygame.draw.rect(surface, color, input_rect)
            pygame.draw.rect(surface, TEXT_COLOR, input_rect, 1)
            
            # Display current state
            display_text = "Yes" if config_font_bold else "No"
            text_surface = font.render(display_text, True, TEXT_COLOR)
            surface.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
            
            buttons.append((input_rect, field_id))
        elif field_id == "palette":
            # Palette selection button
            input_rect = pygame.Rect(menu_x + 120, y_pos - 5, input_width, 25)
            
            pygame.draw.rect(surface, BUTTON_OFF, input_rect)
            pygame.draw.rect(surface, TEXT_COLOR, input_rect, 1)
            
            # Display current palette
            display_text = COLOR_PALETTES[config_palette]["name"]
            text_surface = font.render(display_text, True, TEXT_COLOR)
            surface.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
            
            # Cycle indicator
            button_text = font.render("<>", True, TEXT_COLOR)
            surface.blit(button_text, (input_rect.right - 25, input_rect.y + 5))
            
            buttons.append((input_rect, field_id))
        elif field_id == "palette_reverse":
            # Palette reverse toggle button
            input_rect = pygame.Rect(menu_x + 120, y_pos - 5, input_width, 25)
            
            color = BUTTON_ON if config_palette_reverse else BUTTON_OFF
            pygame.draw.rect(surface, color, input_rect)
            pygame.draw.rect(surface, TEXT_COLOR, input_rect, 1)
            
            # Display current state
            display_text = "Yes" if config_palette_reverse else "No"
            text_surface = font.render(display_text, True, TEXT_COLOR)
            surface.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
            
            buttons.append((input_rect, field_id))
        elif field_id == "flicker_reduction":
            # Flicker reduction toggle button
            input_rect = pygame.Rect(menu_x + 120, y_pos - 5, input_width, 25)
            
            color = BUTTON_ON if config_flicker_reduction else BUTTON_OFF
            pygame.draw.rect(surface, color, input_rect)
            pygame.draw.rect(surface, TEXT_COLOR, input_rect, 1)
            
            # Display current state
            display_text = "Yes" if config_flicker_reduction else "No"
            text_surface = font.render(display_text, True, TEXT_COLOR)
            surface.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
            
            buttons.append((input_rect, field_id))
        elif field_id == "age_influence":
            input_rect = pygame.Rect(menu_x + 120, y_pos - 5, input_width, 25)
            
            color = (255, 140, 0) if config_age_influence else (255, 180, 0)
            pygame.draw.rect(surface, color, input_rect)
            pygame.draw.rect(surface, TEXT_COLOR, input_rect, 1)
            
            display_text = "Yes" if config_age_influence else "No"
            text_surface = font.render(display_text, True, TEXT_COLOR)
            surface.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
            
            buttons.append((input_rect, field_id))
        else:
            # Regular input box
            input_rect = pygame.Rect(menu_x + 120, y_pos - 5, input_width, 25)
            color = BUTTON_ON if input_active == field_id else BUTTON_OFF
            pygame.draw.rect(surface, color, input_rect)
            pygame.draw.rect(surface, TEXT_COLOR, input_rect, 1)
            
            # Display current value or input text
            display_text = input_text if input_active == field_id else str(value)
            text_surface = font.render(display_text, True, TEXT_COLOR)
            surface.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
            
            buttons.append((input_rect, field_id))
        
        y_pos += field_height
    
    # Buttons - responsive layout
    button_width = max(80, menu_width // 6)
    button_height = 35
    button_y = menu_y + menu_height - 60
    button_spacing = (menu_width - 3 * button_width) // 4  # Space between 3 buttons
    
    # Apply, Cancel, and Quit buttons
    apply_rect = pygame.Rect(menu_x + button_spacing, button_y, button_width, button_height)
    cancel_rect = pygame.Rect(menu_x + button_spacing * 2 + button_width, button_y, button_width, button_height)
    quit_rect = pygame.Rect(menu_x + button_spacing * 3 + button_width * 2, button_y, button_width, button_height)
    
    # Button colors
    pygame.draw.rect(surface, BUTTON_ON, apply_rect)
    pygame.draw.rect(surface, BUTTON_OFF, cancel_rect)
    pygame.draw.rect(surface, (180, 0, 0), quit_rect)  # Red for quit
    pygame.draw.rect(surface, TEXT_COLOR, apply_rect, 1)
    pygame.draw.rect(surface, TEXT_COLOR, cancel_rect, 1)
    pygame.draw.rect(surface, TEXT_COLOR, quit_rect, 1)
    
    # Button text - centered
    apply_text = font.render("Apply", True, TEXT_COLOR)
    cancel_text = font.render("Cancel", True, TEXT_COLOR)
    quit_text = font.render("Quit", True, TEXT_COLOR)
    
    apply_text_rect = apply_text.get_rect(center=apply_rect.center)
    cancel_text_rect = cancel_text.get_rect(center=cancel_rect.center)
    quit_text_rect = quit_text.get_rect(center=quit_rect.center)
    
    surface.blit(apply_text, apply_text_rect)
    surface.blit(cancel_text, cancel_text_rect)
    surface.blit(quit_text, quit_text_rect)
    
    buttons.append((apply_rect, "apply"))
    buttons.append((cancel_rect, "cancel"))
    buttons.append((quit_rect, "quit"))
    
    # Instructions 
    instructions = [
        "ESC - Close menu",
        "Click fields to edit values",
        "Enter - Confirm input",
        "Font button - Select system font",
        "Quit - Exit game"
    ]
    
    instruction_x = menu_x + 20
    instruction_y = button_y + button_height + 10
    
    for i, instruction in enumerate(instructions):
        if instruction_y + i * 15 < menu_y + menu_height - 10:  # Only show if fits
            inst_surface = font.render(instruction, True, (180, 180, 180))
            surface.blit(inst_surface, (instruction_x, instruction_y + i * 15))
    
    return buttons

def handle_config_click(mouse_pos, buttons):
    global input_active, input_text, show_config, show_font_popup
    global config_font_name, config_font_size, config_grid_x, config_grid_y, config_cell_size
    global GRID_SIZE_X, GRID_SIZE_Y, CELL_SIZE, grid
    global config_font_bold, config_text, config_palette, config_palette_reverse, config_fps, config_flicker_reduction
    global config_age_influence, config_age_resolution, BIRTH_AGE, SURVIVE_AGE
    
    # Check click delay to prevent rapid clicking
    if not can_click():
        return False
    
    # Handle main buttons
    for rect, field_id in buttons:
        if rect.collidepoint(mouse_pos):
            if field_id == "apply":
                # Apply changes
                try:
                    GRID_SIZE_X = config_grid_x
                    GRID_SIZE_Y = config_grid_y
                    CELL_SIZE = config_cell_size
                    
                    # Update font
                    update_font()
                    
                    # Update color palette
                    update_color_array()
                    
                    # Recreate grid with new dimensions
                    old_grid = grid.copy()
                    grid = np.zeros((GRID_SIZE_Y, GRID_SIZE_X), dtype=int)
                    
                    # Copy old grid data if it fits
                    copy_h = min(old_grid.shape[0], GRID_SIZE_Y)
                    copy_w = min(old_grid.shape[1], GRID_SIZE_X)
                    grid[:copy_h, :copy_w] = old_grid[:copy_h, :copy_w]
                    
                    update_window_size()
                    
                    # Reinitialize with new font settings and text
                    grid = initialize_grid_with_text(config_text, grid_size_x=GRID_SIZE_X, grid_size_y=GRID_SIZE_Y, 
                                                    font_size=config_font_size, font_name=config_font_name, bold=config_font_bold)
                    
                    show_config = False
                    input_active = None
                    show_font_popup = False
                except Exception as e:
                    print(f"Error applying config: {e}")
                return True
            elif field_id == "cancel":
                show_config = False
                input_active = None
                show_font_popup = False
                return True
            elif field_id == "quit":
                pygame.quit()
                exit()
            elif field_id == "font_name":
                # Open font popup
                show_font_popup = True
                input_active = None
                return True
            elif field_id == "font_bold":
                # Toggle bold setting
                config_font_bold = not config_font_bold
                return True
            elif field_id == "palette":
                # Cycle through color palettes
                palette_names = list(COLOR_PALETTES.keys())
                current_index = palette_names.index(config_palette)
                next_index = (current_index + 1) % len(palette_names)
                config_palette = palette_names[next_index]
                return True
            elif field_id == "palette_reverse":
                # Toggle palette reverse setting
                config_palette_reverse = not config_palette_reverse
                return True
            elif field_id == "flicker_reduction":
                # Toggle flicker reduction setting
                config_flicker_reduction = not config_flicker_reduction
                return True
            elif field_id == "age_influence":
                # Toggle age influence setting
                config_age_influence = not config_age_influence
                return True
            else:
                # Start editing this field
                show_font_popup = False
                input_active = field_id
                if field_id == "font_size":
                    input_text = str(config_font_size)
                elif field_id == "grid_x":
                    input_text = str(config_grid_x)
                elif field_id == "grid_y":
                    input_text = str(config_grid_y)
                elif field_id == "cell_size":
                    input_text = str(config_cell_size)
                elif field_id == "fps":
                    input_text = str(config_fps)
                elif field_id == "age_resolution":
                    input_text = str(config_age_resolution)
                elif field_id == "text":
                    input_text = config_text
                return True
    return False

def handle_font_popup_click(mouse_pos, font_buttons, close_rect, scroll_up_rect, scroll_down_rect):
    global config_font_name, show_font_popup, font_popup_scroll
    
    if not can_click():
        return False
    
    # Check close button
    if close_rect.collidepoint(mouse_pos):
        show_font_popup = False
        return True
    
    # Check scroll buttons
    if scroll_up_rect.collidepoint(mouse_pos):
        font_popup_scroll = max(0, font_popup_scroll - 1)
        return True
    elif scroll_down_rect.collidepoint(mouse_pos):
        max_scroll = max(0, (len(available_fonts) - 24 + 2) // 3)  # 3 cols, 8 rows = 24 items
        font_popup_scroll = min(max_scroll, font_popup_scroll + 1)
        return True
    
    # Check font selection
    for rect, font_name in font_buttons:
        if rect.collidepoint(mouse_pos):
            config_font_name = font_name
            update_font()
            show_font_popup = False
            return True
    
    return False

def handle_config_input(event):
    global input_active, input_text, show_font_popup
    global config_font_name, config_font_size, config_grid_x, config_grid_y, config_cell_size, config_text, config_fps, config_age_resolution
    global BIRTH_AGE, SURVIVE_AGE
    
    if input_active is None:
        return False
    
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN:
            # Confirm input
            try:
                if input_active == "font_size":
                    config_font_size = max(1, int(input_text))
                elif input_active == "grid_x":
                    config_grid_x = max(5, min(600, int(input_text)))
                elif input_active == "grid_y":
                    config_grid_y = max(5, min(600, int(input_text)))
                elif input_active == "cell_size":
                    config_cell_size = max(5, min(50, int(input_text)))
                elif input_active == "fps":
                    config_fps = max(1, min(1000, int(input_text)))  # Limit FPS between 1-1000
                elif input_active == "age_resolution":
                    config_age_resolution = max(1, min(20, int(input_text)))  # Limit to 1-8 bits (2-256 values)
                elif input_active == "text":
                    config_text = input_text if input_text.strip() else "HeiChips"
            except ValueError:
                pass  # Invalid input, ignore
            
            input_active = None
            input_text = ""
            return True
        elif event.key == pygame.K_ESCAPE:
            input_active = None
            input_text = ""
            show_font_popup = False
            return True
        elif event.key == pygame.K_BACKSPACE:
            input_text = input_text[:-1]
            return True
        else:
            # Add character to input
            if event.unicode.isprintable():
                input_text += event.unicode
            return True
    
    return False

# Load initial pattern
grid = initialize_grid_with_text(config_text, grid_size_x=GRID_SIZE_X, grid_size_y=GRID_SIZE_Y, 
                                font_size=config_font_size, font_name=config_font_name, bold=config_font_bold)

# Frame counter for simulation timing (run simulation every 4th frame)
frame_counter = 0

#TODO # Set initial window size
update_window_size()

# Main loop
while True:
    # Handle events that don't need button references first
    mouse_pos = None
    mouse_left_pressed = False
    mouse_right_pressed = False
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

        # Handle config menu input first
        if show_config and handle_config_input(event):
            continue

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if show_font_popup:
                    show_font_popup = False
                elif show_config:
                    show_config = False
                    input_active = None
                else:
                    show_config = True
            elif event.key == pygame.K_SPACE:
                running = not running
            elif event.key == pygame.K_c:
                grid.fill(0)
            elif event.key == pygame.K_h:
                grid = initialize_grid_with_text(config_text, grid_size_x=GRID_SIZE_X, grid_size_y=GRID_SIZE_Y, 
                                                font_size=config_font_size, font_name=config_font_name, bold=config_font_bold)
            elif event.key == pygame.K_r:
                randomize_rules()
            elif pygame.K_0 <= event.key <= pygame.K_9:
                preset = event.key - pygame.K_0
                if config_age_influence:
                    # Handle age rules for presets
                    if preset < len(AGE_RULE_PRESETS):
                        BIRTH, SURVIVE, BIRTH_AGE, SURVIVE_AGE = AGE_RULE_PRESETS[preset]
                        update_color_array(False)
                else:
                    if preset < len(RULE_PRESETS):
                        BIRTH, SURVIVE = map(set, RULE_PRESETS[preset])
                        # Reset age rules to full range when switching rule presets
                        BIRTH_AGE = set(range(1, 16))  # Reset to 1-15
                        SURVIVE_AGE = set(range(1, 16))  # Reset to 1-15
                        update_color_array(False) # Update colors to handle BIRTH 0 rule is/was active
    
    # Check for mouse events
    if pygame.mouse.get_pressed()[0]:
        mouse_left_pressed = True
        mouse_pos = pygame.mouse.get_pos()
    elif pygame.mouse.get_pressed()[2]:
        mouse_right_pressed = True
        mouse_pos = pygame.mouse.get_pos()

    if running and not show_config and not show_font_popup:
        # Only update simulation every 4th frame
        if frame_counter % 4 == 0:
            grid = update_grid(grid)
    
    # Increment frame counter
    frame_counter += 1

    draw_grid(screen, grid)
    
    # Initialize button variables
    birth_buttons = []
    survive_buttons = []
    birth_age_buttons = []
    survive_age_buttons = []
    
    if show_font_popup:
        # Draw font popup on top of everything
        font_buttons, close_rect, scroll_up_rect, scroll_down_rect = draw_font_popup(screen)
        
        # Handle font popup clicks
        if mouse_left_pressed:
            handle_font_popup_click(mouse_pos, font_buttons, close_rect, scroll_up_rect, scroll_down_rect)
            
    elif show_config:
        config_buttons = draw_config_menu(screen)
        
        # Handle config menu clicks
        if mouse_left_pressed:
            handle_config_click(mouse_pos, config_buttons)
            
    else:
        birth_buttons = draw_rule_buttons(screen, BIRTH, "BIRTH", RULE_Y_OFFSET)
        survive_buttons = draw_rule_buttons(screen, SURVIVE, "SURVIVE", RULE_Y_OFFSET + RULE_BUTTON_HEIGHT + 10)
        
        # Draw age rule buttons if age influence is enabled
        if config_age_influence:
            # Age rule buttons are 20% smaller
            age_button_width = int(RULE_BUTTON_WIDTH * 0.8)
            age_button_height = int(RULE_BUTTON_HEIGHT * 0.8)
            
            # Calculate horizontal layout requirements (same logic as window sizing)
            horizontal_width_needed = 50 + 16 * (age_button_width + RULE_MARGIN) + 50
            
            # Calculate height for horizontal layout
            horizontal_height_needed = RULE_Y_OFFSET + RULE_BUTTON_HEIGHT * 2 + 40 + age_button_height * 2 + 60
            
            # Get display height to check if window would fit on screen
            try:
                display_info = pygame.display.Info()
                display_height = display_info.current_h
            except:
                display_height = 1080  # Fallback
            
            # Check if horizontal layout is feasible
            horizontal_fits_width = WINDOW_SIZE_X >= horizontal_width_needed
            horizontal_fits_height = horizontal_height_needed <= (display_height - 100)
            
            if horizontal_fits_width and horizontal_fits_height:
                # Horizontal layout at the bottom
                age_y_start = RULE_Y_OFFSET + RULE_BUTTON_HEIGHT * 2 + 40
                birth_age_buttons = draw_age_rule_buttons(screen, BIRTH_AGE, "BIRTH AGE", 
                                                        0, age_y_start, vertical=False)
                survive_age_buttons = draw_age_rule_buttons(screen, SURVIVE_AGE, "SURVIVE AGE", 
                                                          0, age_y_start + age_button_height + 30, vertical=False)
            else:
                # Vertical layout on the right side
                age_x_offset = GRID_SIZE_X * CELL_SIZE + 20
                birth_age_y_offset = 50
                age_buttons_height = 8 * (age_button_height + RULE_MARGIN)
                survive_age_y_offset = birth_age_y_offset + age_buttons_height + 40
                
                birth_age_buttons = draw_age_rule_buttons(screen, BIRTH_AGE, "BIRTH AGE", 
                                                        age_x_offset, birth_age_y_offset, vertical=True)
                survive_age_buttons = draw_age_rule_buttons(screen, SURVIVE_AGE, "SURVIVE AGE", 
                                                          age_x_offset, survive_age_y_offset, vertical=True)
        
        draw_help_box(screen)  # Draw help box to the right of rule buttons
        
        # Handle mouse clicks on game area and rule buttons
        if mouse_left_pressed:
            mx, my = mouse_pos
            x, y = mx // CELL_SIZE, my // CELL_SIZE
            # Only modify grid if click is within the actual grid bounds
            if 0 <= x < GRID_SIZE_X and 0 <= y < GRID_SIZE_Y:
                grid[y][x] = 1
            else:
                # Click is outside grid area, check for rule button clicks
                if config_age_influence:
                    handle_rule_click(mouse_pos, birth_buttons, survive_buttons, birth_age_buttons, survive_age_buttons)
                else:
                    handle_rule_click(mouse_pos, birth_buttons, survive_buttons)

        elif mouse_right_pressed:
            mx, my = mouse_pos
            x, y = mx // CELL_SIZE, my // CELL_SIZE
            # Only modify grid if click is within the actual grid bounds
            if 0 <= x < GRID_SIZE_X and 0 <= y < GRID_SIZE_Y:
                grid[y][x] = 0
    
    pygame.display.flip()
    clock.tick(config_fps * 4)  # Run display at 4x config_fps, simulation runs every 4th frame
