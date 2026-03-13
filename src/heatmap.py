import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from src.layout import EMPTY, WALL

class HeatmapEngine:
    """Maintains a persistent density grid for optimized heatmap rendering."""
    def __init__(self, layout):
        self.layout = layout
        self.rows = len(layout)
        self.cols = len(layout[0])
        self.grid = np.zeros((self.rows, self.cols))
        self.wall_mask = np.array([[1 if cell == WALL else 0 for cell in row] for row in layout])
        
    def update_density(self, snapshot):
        """Rebuilds density grid from snapshot (optimized for small numbers of agents)."""
        self.grid.fill(0)
        if snapshot:
            for s in snapshot.agents:
                r, c = s["position"]
                if 0 <= r < self.rows and 0 <= c < self.cols:
                    self.grid[r, c] += 1
                    
        # Apply smoothing
        try:
            from scipy.ndimage import gaussian_filter
            self.grid = gaussian_filter(self.grid, sigma=1.5)
        except ImportError:
            pass
            
    def render(self):
        """Renders the current density grid to a BytesIO image buffer."""
        fig, ax = plt.subplots(figsize=(6, 6))
        
        # Draw background
        ax.imshow(self.wall_mask, cmap='Greys', alpha=0.3, origin='upper')
        
        # Overlay heatmap
        grid_masked = np.ma.masked_where(self.grid < 0.1, self.grid)
        if np.max(self.grid) >= 0.1:
            cmap = sns.color_palette("RdYlGn_r", as_cmap=True)
            cax = ax.imshow(grid_masked, cmap=cmap, alpha=0.8, origin='upper', interpolation='nearest', vmin=0, vmax=max(3.0, np.max(self.grid)))
            fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04, label="Traffic Density Scale")
        else:
            ax.text(0.5, 0.5, "No Active Agents", ha='center', va='center', transform=ax.transAxes)
            
        ax.axis('off')
        ax.set_title("Real-Time Traffic Density Matrix")
        
        plt.tight_layout()
        buf = BytesIO()
        fig.savefig(buf, format="png", bbox_inches='tight', transparent=True)
        plt.close(fig)
        buf.seek(0)
        return buf
