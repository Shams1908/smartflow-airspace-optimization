class MetricsEngine:
    """Calculates system statistics and analytics based on state snapshots."""
    def __init__(self):
        self.metrics_history = []
        
    def calculate_metrics(self, snapshot):
        """Calculates metrics for the given snapshot."""
        if not snapshot:
            return None
            
        active_count = snapshot.active_count
        total_wait = sum([a["wait_timer"] for a in snapshot.agents])
        throughput = snapshot.completed_count
        
        # Heuristic congestion score based on count and wait times
        congestion_score = active_count * 1.5 + total_wait * 0.1
        
        avg_wait_time = total_wait / max(1, active_count)
        
        metrics = {
            "tick": snapshot.tick_count,
            "active_agents": active_count,
            "total_wait_time": total_wait,
            "avg_wait_time": avg_wait_time,
            "throughput": throughput,
            "congestion_score": congestion_score
        }
        
        self.metrics_history.append(metrics)
        # Keep history bounded
        if len(self.metrics_history) > 1000:
            self.metrics_history.pop(0)
            
        return metrics
        
    def get_latest_metrics(self):
        if not self.metrics_history:
            return {
                "tick": 0,
                "active_agents": 0,
                "total_wait_time": 0,
                "avg_wait_time": 0.0,
                "throughput": 0,
                "congestion_score": 0.0
            }
        return self.metrics_history[-1]
