import copy

class StateSnapshot:
    """Represents a frozen snapshot of the simulation state at a specific tick."""
    def __init__(self, tick_count, active_agents, completed_agents):
        self.tick_count = tick_count
        # Deep copy agents' relevant states to prevent mutation
        self.agents = [
            {
                "id": a.id,
                "position": a.position,
                "goal_position": a.goal_position,
                "path": list(a.path),
                "state": a.state,
                "wait_timer": a.wait_timer,
                "priority": a.priority,
                "has_food": getattr(a, 'has_food', False)
            } for a in active_agents
        ]
        self.active_count = len(active_agents)
        self.completed_count = len(completed_agents)

class StateManager:
    """Manages the history of simulation states and provides the current snapshot."""
    def __init__(self):
        self.history = []
        self.current_state = None
        self.max_history = 100

    def capture_state(self, simulation):
        """Captures a snapshot from the simulation and stores it."""
        snapshot = StateSnapshot(
            simulation.tick_count, 
            simulation.active_students, 
            simulation.completed_students
        )
        self.current_state = snapshot
        self.history.append(snapshot)
        
        if len(self.history) > self.max_history:
            self.history.pop(0)
            
        return snapshot

    def get_current_state(self):
        return self.current_state
