import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
from src.layout import EMPTY, WALL, COUNTER, TABLE, ENTRY, EXIT

class Visualizer:
    def __init__(self, layout):
        self.layout = layout
        self.fig, self.ax = plt.subplots(figsize=(8, 8))
        
        # Color mapping: Empty(White), Wall(Black), Counter(Blue), Table(Brown), Entry(Green), Exit(Red)
        colors = ['white', 'black', 'blue', 'saddlebrown', 'green', 'red']
        self.cmap = ListedColormap(colors)
        
        # Create persistent image plot
        self.img = self.ax.imshow(self.layout, cmap=self.cmap, vmin=0, vmax=5)
        
        # Create persistent scatter plot wrapper for agents
        self.scatter, = self.ax.plot([], [], 'o', color='magenta', markersize=6)
        
        self.ax.set_title("Canteen Simulation")
        self.ax.axis('off')

    def render(self, students, tick):
        """
        Updates the visual representation based on agent positions.
        """
        self.ax.set_title(f"Canteen Simulation | Step: {tick} | Active Students: {len(students)}")
        
        if students:
            # Extract x, y coordinates
            # Note: numpy [row, col] maps to scatter [y, x]
            x_coords = [s.position[1] for s in students]
            y_coords = [s.position[0] for s in students]
            self.scatter.set_data(x_coords, y_coords)
        else:
            self.scatter.set_data([], [])

        plt.pause(0.1) # Brief pause creates animation effect
        self.fig.canvas.draw()
