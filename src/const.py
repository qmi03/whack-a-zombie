"""Game constants and configuration."""

# Display settings
WIDTH = 1280
HEIGHT = 720

# Color palette
BG_COLOR = (12, 20, 28)
ZOMBIE_COLOR = (95, 175, 85)
HIT_COLOR = (220, 50, 50)
WHITE = (240, 245, 255)
RED = (255, 50, 50)

# Grid configuration
# Creates a 3-row staggered grid pattern
GRID_POSITIONS = []

# Row positions (y-coordinates)
ROW_Y_POSITIONS = [210, 410, 610]

# Column positions (x-coordinates)
# Rows 1 and 3 use odd multiples: 90, 270, 450, 630, 810, 990, 1170
ROW_ODD_X = [90 * n for n in range(1, 14, 2)]
# Row 2 uses even multiples: 180, 360, 540, 720, 900, 1080
ROW_EVEN_X = [90 * n for n in range(2, 13, 2)]

# Build grid: row 1 (odd), row 2 (even), row 3 (odd)
for x in ROW_ODD_X:
    GRID_POSITIONS.append((x, ROW_Y_POSITIONS[0]))
for x in ROW_EVEN_X:
    GRID_POSITIONS.append((x, ROW_Y_POSITIONS[1]))
for x in ROW_ODD_X:
    GRID_POSITIONS.append((x, ROW_Y_POSITIONS[2]))

# Difficulty settings
SPAWN_INTERVAL_BASE = 1000  # Base time between zombie spawns (ms)
SHOW_DURATION_BASE = 950  # Base time zombies stay visible (ms)
SPAWN_INTERVAL_DECREASE_PER_LEVEL = 65  # How much faster spawns get per level
SHOW_DURATION_DECREASE_PER_LEVEL = 55  # How much shorter visibility gets per level
MIN_SPAWN_INTERVAL = 500  # Fastest possible spawn rate
MIN_SHOW_DURATION = 1500  # Shortest possible visibility time
BASE_SPAWN_CHANCE = 0.60  # Starting probability of spawn attempt succeeding
SPAWN_CHANCE_INCREASE = 0.06  # Spawn chance increase per level
MAX_SPAWN_CHANCE = 0.92  # Maximum spawn probability

# Scoring
POINTS_PER_HIT = 10
COMBO_BONUS_DIVISOR = 3  # Extra points = combo // 3
POINTS_PER_LEVEL = 40  # Score needed to advance to next level

# Game settings
STARTING_LIVES = 5
ZOMBIE_RISE_DURATION = 300  # Time for zombie to fully emerge (ms)
HIT_DISPLAY_DURATION = 2000  # How long squashed zombie shows (ms)

# UI settings
COMBO_DISPLAY_THRESHOLD = 3  # Minimum combo to show combo counter
