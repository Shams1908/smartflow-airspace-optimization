import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
from src.layout import EMPTY, WALL

def generate_heatmap(layout, students):
    """
    Generates a KDE density heatmap of student positions over the layout.
    Returns the heatmap as a PIL Image or BytesIO object suitable for st.image().
    """
    rows = len(layout)
    cols = len(layout[0])
    
    # Create the base layout mask (0 for Empty, 1 for walls/obstacles)
    # We use this to mask out areas where agents cannot be
    
    # Initialize a 2D density grid
    grid = np.zeros((rows, cols))
    
    # Simple count-based density (can be smoothed with KDE if needed, but grid count is fast for real-time)
    for s in students:
        r, c = s.position
        if 0 <= r < rows and 0 <= c < cols:
            grid[r, c] += 1
            
    # Apply a light Gaussian blur to the grid to make it look like a smooth heatmap
    try:
        from scipy.ndimage import gaussian_filter
        grid = gaussian_filter(grid, sigma=1.5)
    except ImportError:
        pass # Fallback to blocky if scipy is missing
        
    # Create matplotlib figure
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # Create a custom colormap from Green (Low) -> Yellow (Med) -> Red (High)
    cmap = sns.color_palette("RdYlGn_r", as_cmap=True)
    
    # Mask out areas with 0 density so we can see the layout underneath
    grid_masked = np.ma.masked_where(grid < 0.1, grid)
    
    # Draw simple layout background (walls)
    wall_mask = np.array([[1 if cell == WALL else 0 for cell in row] for row in layout])
    ax.imshow(wall_mask, cmap='Greys', alpha=0.3, origin='upper')
    
    # Overlay the heatmap
    if len(students) > 0:
        cax = ax.imshow(grid_masked, cmap=cmap, alpha=0.8, origin='upper', interpolation='nearest', vmin=0, vmax=max(3.0, np.max(grid)))
        fig.colorbar(cax, ax=ax, fraction=0.046, pad=0.04, label="Congestion Density")
    else:
        ax.text(0.5, 0.5, "No Agents Active", ha='center', va='center', transform=ax.transAxes)
        
    ax.axis('off')
    ax.set_title("Real-Time Crowd Density")
    
    plt.tight_layout()
    
    # Save to BytesIO buffer
    buf = BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', transparent=True)
    plt.close(fig)
    buf.seek(0)
    
    return buf
