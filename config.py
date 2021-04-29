# The configuration
cell_size = 18
cols = 8
rows = 16
maxfps = 30

colors = [
    (0, 0, 0),
    (255, 85, 85),
    (100, 200, 115),
    (120, 108, 245),
    (255, 140, 50),
    (50, 120, 52),
    (146, 202, 73),
    (150, 161, 218),
    (35, 35, 35)  # Helper color for background grid
]

# Define the shapes of the single parts
tetris_shapes = [
    [[1]],
    [[1, 1]],
    [[1, 1],
     [1, 1]],
    [[1, 1],
     [0, 1]]
]