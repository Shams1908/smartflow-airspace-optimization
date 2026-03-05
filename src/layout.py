import numpy as np

# Cell types
EMPTY = 0
WALL = 1
COUNTER = 2
TABLE = 3
ENTRY = 4
EXIT = 5

def create_layout():
    """
    Creates a basic canteen layout as a 2D integer numpy array.
    
    0 = empty walkable space
    1 = wall
    2 = counter
    3 = table
    4 = entry
    5 = exit
    
    Returns:
        np.ndarray: The 2D layout grid.
    """
    # Create a 20x20 empty grid
    grid = np.zeros((20, 20), dtype=int)
    
    # Add walls
    grid[0, :] = WALL
    grid[-1, :] = WALL
    grid[:, 0] = WALL
    grid[:, -1] = WALL
    
    # Entries (left wall)
    grid[5:8, 0] = ENTRY
    
    # Exits (right wall)
    grid[15:18, -1] = EXIT
    
    # Counters (top middle)
    grid[2:4, 8:12] = COUNTER
    
    # Tables (scattered in the bottom right area)
    grid[10:12, 12:14] = TABLE
    grid[10:12, 16:18] = TABLE
    grid[14:16, 12:14] = TABLE
    grid[14:16, 16:18] = TABLE
    
    return grid
