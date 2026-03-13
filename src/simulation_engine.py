from src.simulation import Simulation

class SimulationEngine:
    """
    Wraps the core Simulation to provide a stable interface
    without modifying the underlying mathematical/logical models.
    """
    def __init__(self, layout, spawn_rate=0.3):
        self.core_sim = Simulation(layout, spawn_rate=spawn_rate)
        self.is_running = False
        
    def step(self):
        """Advances the simulation by one tick."""
        if self.is_running:
            self.core_sim.update()
            
    def play(self):
        self.is_running = True
        
    def pause(self):
        self.is_running = False
        
    def reset(self, layout, spawn_rate=0.3):
        self.core_sim = Simulation(layout, spawn_rate=spawn_rate)
        self.is_running = False
        
    def trigger_emergency_evacuation(self):
        if self.simulation_ref:
            self.simulation_ref.trigger_emergency_evacuation()
            
    def trigger_table_failure(self):
        if self.simulation_ref:
            self.simulation_ref.trigger_table_failure()
            
    def block_walkway(self):
        if self.simulation_ref:
            return self.simulation_ref.block_random_walkway()
        return None
        
    def clear_emergencies(self):
        if self.simulation_ref:
            self.simulation_ref.clear_emergencies()
        
    @property
    def tick_count(self):
        return self.core_sim.tick_count
        
    @property
    def active_agents(self):
        return self.core_sim.active_students
        
    @property
    def completed_agents(self):
        return self.core_sim.completed_students
        
    @property
    def simulation_ref(self):
        """Returns the underlying simulation instance for the state manager."""
        return self.core_sim
