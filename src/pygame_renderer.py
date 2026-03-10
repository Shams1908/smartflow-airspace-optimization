import pygame
import numpy as np
from src.layout import EMPTY, WALL, COUNTER, TABLE, ENTRY, EXIT

class PygameRenderer:
    def __init__(self, layout, cell_size=20):
        # Initialize pygame explicitly for headless surface rendering
        pygame.init()
        
        self.layout = layout
        self.rows = len(layout)
        self.cols = len(layout[0])
        self.cell_size = cell_size
        
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size
        
        # Create a surface instead of a display window
        self.surface = pygame.Surface((self.width, self.height))
        
        # Define Color Palette
        self.colors = {
            EMPTY: (245, 245, 245),      # Light Gray Background
            WALL: (45, 52, 54),          # Dark Gray Walls
            COUNTER: (9, 132, 227),      # Blue
            TABLE: (214, 162, 232),      # Light Purple (or brown)
            ENTRY: (0, 184, 148),        # Mint Green
            EXIT: (214, 48, 49),         # Red Exit
        }
        
    def _draw_grid(self):
        """Draws the static layout map onto the surface"""
        self.surface.fill(self.colors[EMPTY])
        
        for r in range(self.rows):
            for c in range(self.cols):
                cell_type = self.layout[r][c]
                if cell_type != EMPTY:
                    rect = pygame.Rect(
                        c * self.cell_size,
                        r * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )
                    pygame.draw.rect(self.surface, self.colors[cell_type], rect)
                    
                    # Draw a subtle border for tables
                    if cell_type == TABLE:
                        pygame.draw.rect(self.surface, (150, 150, 150), rect, 1)

    def _draw_agents(self, students):
        """Renders agents as smooth circles with optional direction/path indicators"""
        for student in students:
            # Map grid position to pixel coordinates (center of the cell)
            center_x = int(student.position[1] * self.cell_size + self.cell_size / 2)
            center_y = int(student.position[0] * self.cell_size + self.cell_size / 2)
            
            # Agent Color (Default: Orange/Coral)
            agent_color = (253, 121, 168) # Pinkish
            if student.has_food:
                agent_color = (108, 92, 231) # Purple
                
            # Draw Agent Circle
            radius = int(self.cell_size * 0.4)
            pygame.draw.circle(self.surface, agent_color, (center_x, center_y), radius)
            
            # Draw Path/Direction indicator if they are moving
            if getattr(student, 'path', None) and len(student.path) > 0:
                next_pos = student.path[0]
                next_x = int(next_pos[1] * self.cell_size + self.cell_size / 2)
                next_y = int(next_pos[0] * self.cell_size + self.cell_size / 2)
                
                # Draw small line pointing to next position
                pygame.draw.line(self.surface, (255, 255, 255), (center_x, center_y), (next_x, next_y), 2)
                
                # Draw full predicted path as a thin line
                path_points = [(center_x, center_y)]
                for p in student.path[:5]: # Show up to 5 steps ahead to avoid clutter
                    px = int(p[1] * self.cell_size + self.cell_size / 2)
                    py = int(p[0] * self.cell_size + self.cell_size / 2)
                    path_points.append((px, py))
                    
                if len(path_points) > 1:
                    pygame.draw.lines(self.surface, (253, 203, 110), False, path_points, 1) # Yellow-ish subtle path

    def render_frame(self, students):
        """
        Renders the current simulation frame and returns it as an RGB array.
        This array is compatible with Streamlit's st.image()
        """
        self._draw_grid()
        self._draw_agents(students)
        
        # Convert pygame surface to 3D numpy array [Height, Width, RGB]
        # pygame.surfarray.array3d returns (Width, Height, RGB), so we transpose it
        view = pygame.surfarray.array3d(self.surface)
        view = np.transpose(view, (1, 0, 2))
        
        return view
