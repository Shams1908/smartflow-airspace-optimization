import pygame
import numpy as np
import time
from src.layout import EMPTY, WALL, COUNTER, TABLE, ENTRY, EXIT

class Renderer:
    def __init__(self, layout, cell_size=20):
        pygame.init()
        self.layout = layout
        self.rows = len(layout)
        self.cols = len(layout[0])
        self.cell_size = cell_size
        self.width = self.cols * self.cell_size
        self.height = self.rows * self.cell_size
        self.surface = pygame.Surface((self.width, self.height))
        
        self.colors = {
            EMPTY: (10, 15, 30),         # Very Dark Navy/Black Space
            WALL: (25, 35, 60),          # Darker Structural Blue
            COUNTER: (0, 229, 255),      # Neon Cyan
            TABLE: (100, 110, 140),      # Metallic Grey
            ENTRY: (0, 200, 83),         # Neon Green
            EXIT: (255, 61, 0),          # Neon Orange
        }
        
        # Track previous agent positions for animation interpolation
        self.prev_positions = {}
        self.current_positions = {}
        self.last_sim_tick = -1

    def _draw_grid(self):
        self.surface.fill(self.colors[EMPTY])
        for r in range(self.rows):
            for c in range(self.cols):
                cell_type = self.layout[r][c]
                if cell_type != EMPTY:
                    rect = pygame.Rect(c * self.cell_size, r * self.cell_size, self.cell_size, self.cell_size)
                    pygame.draw.rect(self.surface, self.colors[cell_type], rect)
                    if cell_type == TABLE:
                        pygame.draw.rect(self.surface, (150, 150, 150), rect, 1)

    def _draw_paths(self, snapshot):
        """Draws thin semi-transparent navigation corridors for all agents."""
        if not snapshot:
            return
            
        # Draw all paths first (underneath agents)
        for agent in snapshot.agents:
            path = agent.get("path", [])
            if not path:
                continue
                
            curr_r, curr_c = agent["position"]
            center_x = int(curr_c * self.cell_size + self.cell_size / 2)
            center_y = int(curr_r * self.cell_size + self.cell_size / 2)
            
            # Semi-transparent blue for navigation corridor
            path_color = (0, 229, 255, 100) # Cyan 
            
            # Draw initial link to next step
            next_pos = path[0]
            next_x = int(next_pos[1] * self.cell_size + self.cell_size / 2)
            next_y = int(next_pos[0] * self.cell_size + self.cell_size / 2)
            
            # To draw transparent lines, we can draw to a temp surface or just draw solid subtle colours.
            # Using a solid subtle color for simplicity in pygame:
            solid_path_color = (15, 100, 150)
            pygame.draw.line(self.surface, solid_path_color, (center_x, center_y), (next_x, next_y), 2)
            
            path_points = [(center_x, center_y)]
            for p in path[:4]:
                px = int(p[1] * self.cell_size + self.cell_size / 2)
                py = int(p[0] * self.cell_size + self.cell_size / 2)
                path_points.append((px, py))
                
            if len(path_points) > 1:
                pygame.draw.lines(self.surface, solid_path_color, False, path_points, 1)

    def _draw_agents(self, snapshot, interpolation_factor=1.0):
        """Draws agents with positions linearly interpolated against previous state."""
        if not snapshot:
            return
            
        current_tick = snapshot.tick_count
        
        # New tick detected: slide positions backward
        if current_tick != self.last_sim_tick:
            self.last_sim_tick = current_tick
            self.prev_positions = self.current_positions.copy()
            
            self.current_positions = {}
            for agent in snapshot.agents:
                aid = agent["id"]
                pos = agent["position"]
                self.current_positions[aid] = pos
                if aid not in self.prev_positions:
                    self.prev_positions[aid] = pos

        for agent in snapshot.agents:
            aid = agent["id"]
            curr_r, curr_c = agent["position"]
            prev_r, prev_c = self.prev_positions.get(aid, (curr_r, curr_c))
            
            # Interpolate
            interp_r = prev_r + (curr_r - prev_r) * interpolation_factor
            interp_c = prev_c + (curr_c - prev_c) * interpolation_factor
            
            center_x = int(interp_c * self.cell_size + self.cell_size / 2)
            center_y = int(interp_r * self.cell_size + self.cell_size / 2)
            
            # Normal: Green, Rerouted/Eating/Wait: Red (as requested)
            agent_color = (0, 255, 100) if not agent["wait_timer"] > 5 else (255, 50, 50)
            if agent.get("priority", 1) == 3:
                agent_color = (255, 200, 0)  # High Priority agent (Yellow/Orange)
                
            pygame.draw.circle(self.surface, agent_color, (center_x, center_y), int(self.cell_size * 0.4))

    def _draw_predictions(self, predictions):
        """Draws pulsing zones around predicted conflict areas."""
        if not predictions:
            return
            
        # Use time to create a pulsing radius effect (0 to 1 cycle)
        pulse = (np.sin(time.time() * 4) + 1) / 2
        
        for pred in predictions:
            r, c = pred["pos"]
            prob = pred["prob"]
            center_x = int(c * self.cell_size + self.cell_size / 2)
            center_y = int(r * self.cell_size + self.cell_size / 2)
            
            # Size pulses based on probability
            base_radius = int(self.cell_size * 1.5)
            pulse_radius = int(base_radius + (base_radius * 0.5 * pulse))
            
            color = (255, 0, 0, 100) if prob > 0.8 else (255, 193, 7, 100)
            
            # Draw alpha surface for transparency
            temp_surface = pygame.Surface((pulse_radius*2, pulse_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(temp_surface, color, (pulse_radius, pulse_radius), pulse_radius)
            # Add thin solid ring
            border_color = (255, 0, 0) if prob > 0.8 else (255, 193, 7)
            pygame.draw.circle(temp_surface, border_color, (pulse_radius, pulse_radius), pulse_radius, 2)
            
            self.surface.blit(temp_surface, (center_x - pulse_radius, center_y - pulse_radius))

    def render_frame(self, snapshot, predictions=None, interpolation_factor=1.0):
        self._draw_grid()
        self._draw_paths(snapshot)
        self._draw_agents(snapshot, interpolation_factor)
        self._draw_predictions(predictions)
        
        view = pygame.surfarray.array3d(self.surface)
        return np.transpose(view, (1, 0, 2))
