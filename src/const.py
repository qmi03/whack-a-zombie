GRID = []
# Row 1 & 3: x = 90*n for n=1,3,5,7,9,11,13 → 90,270,450,630,810,990,1170
row1_3_x = [90 * n for n in range(1, 14, 2)]
# Row 2: x = 90*n for n=2,4,6,8,10,12 → 180,360,540,720,900,1080
row2_x = [90 * n for n in range(2, 13, 2)]

# Build grid
for x in row1_3_x:
    GRID.append((x, 210))
for x in row2_x:
    GRID.append((x, 410))
for x in row1_3_x:
    GRID.append((x, 610))

# Difficulty progression
SPAWN_INTERVAL_BASE = 1000
SHOW_DURATION_BASE = 950
