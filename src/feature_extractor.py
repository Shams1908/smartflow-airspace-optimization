import numpy as np

class FeatureExtractor:
    """Converts simulation state into features for the prediction engine."""
    def __init__(self, layout):
        self.layout = layout
        self.rows = len(layout)
        self.cols = len(layout[0])
        
    def extract_features(self, snapshot):
        """
        Extracts a spatial grid feature representation from the snapshot.
        Output: A (Rows x Cols) grid representing density/clustering.
        """
        if not snapshot:
            return np.zeros((self.rows, self.cols))
            
        feature_grid = np.zeros((self.rows, self.cols))
        
        for agent in snapshot.agents:
            r, c = agent["position"]
            if 0 <= r < self.rows and 0 <= c < self.cols:
                # Base density
                feature_grid[r, c] += 1
                
                # Incorporate planned path to foresee congestion
                path = agent.get("path", [])
                for i, (pr, pc) in enumerate(path[:3]):  # Look ahead 3 steps
                    if 0 <= pr < self.rows and 0 <= pc < self.cols:
                        # Decay weight for future positions
                        feature_grid[pr, pc] += (0.5 / (i + 1))
                        
        return feature_grid
