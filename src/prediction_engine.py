import random

class PredictionEngine:
    """
    Mock AI Prediction Engine that forecasts potential congestion or conflict zones.
    It observes simulation state but does NOT control agents.
    """
    def __init__(self, feature_extractor):
        self.feature_extractor = feature_extractor
        self.predicted_zones = []  # List of dicts: {'pos': (r,c), 'prob': float, 'time_horizon': int}
        
    def run_prediction(self, snapshot):
        """Runs the prediction model on the current state features."""
        if not snapshot or snapshot.tick_count % 5 != 0:
            return self.predicted_zones  # Only run every few ticks to save compute
            
        features = self.feature_extractor.extract_features(snapshot)
        self.predicted_zones = []
        
        rows, cols = features.shape
        
        # Simple heuristic "model": identify high density areas from features
        # In a real scenario, this would be model.predict(features)
        for r in range(rows):
            for c in range(cols):
                val = features[r, c]
                if val >= 2.5:  # High congestion threshold
                    # Generate a prediction zone
                    prob = min(0.99, 0.5 + (val * 0.1))
                    horizon = random.randint(5, 15)  # 5-15 seconds ahead
                    self.predicted_zones.append({
                        "pos": (r, c),
                        "prob": prob,
                        "time_horizon": horizon
                    })
                    
        # Sort by highest probability
        self.predicted_zones.sort(key=lambda x: x["prob"], reverse=True)
        # Limit to top 3 zones
        self.predicted_zones = self.predicted_zones[:3]
        
        return self.predicted_zones
        
    def get_current_predictions(self):
        return self.predicted_zones
