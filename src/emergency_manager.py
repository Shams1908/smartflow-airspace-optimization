import random

class EmergencyManager:
    """
    Manages emergency scenarios and system-wide overrides for the SmartFlow simulation.
    Exposes functions to alter agent behaviors and layout constraints dynamically.
    """
    def __init__(self):
        self.active_emergency = None
        self.original_states = {}  # Store baseline states if recovery is needed

    def trigger_evacuation(self, students, exit_locations):
        """
        Forces all active agents to evacuate to the nearest/random exit immediately.
        """
        self.active_emergency = "EVACUATION"
        for student in students:
            # Save their original state in case we implement a "resume" logic later
            self.original_states[student.id] = {
                "goal": student.goal_position,
                "state": student.state,
                "priority": student.priority
            }
            
            # Override behavior
            if exit_locations:
                student.goal_position = random.choice(exit_locations)
            
            student.state = "EXIT"
            student.priority = 3  # Max priority for evacuation routing
            
            # Clear resource locks
            student.is_waiting_for_table = False
            student.is_in_queue = False
            student.assigned_table = False
            
            # The optimizer module will recalculate paths on the next tick because goal changed

    def trigger_table_failure(self, resource_manager, failed_tables):
        """
        Reduces table capacity in the resource manager to simulate failures.
        """
        self.active_emergency = "TABLE_FAILURE"
        # Safely reduce capacity, ensuring it doesn't drop below 0
        new_capacity = max(0, resource_manager.capacity - failed_tables)
        resource_manager.capacity = new_capacity

    def block_walkway(self, layout, cell):
        """
        Converts a specific walkable layout cell into an obstacle/wall.
        The optimizer will automatically route around it on the next graph build.
        """
        self.active_emergency = "PATH_BLOCKAGE"
        r, c = cell
        if 0 <= r < len(layout) and 0 <= c < len(layout[0]):
            self.original_states[f"cell_{r}_{c}"] = layout[r][c]
            layout[r][c] = 1  # Assuming 1 is WALL/Obstacle based on layout.py

    def clear_emergency(self, layout=None, resource_manager=None, original_table_capacity=None):
        """
        Resets the emergency state and attempts to restore modified layout/resources.
        Agents will simply continue with their overridden goals rather than teleporting back.
        """
        self.active_emergency = None
        
        # Restore layout blocks if provided
        if layout is not None:
            for key, val in self.original_states.items():
                if str(key).startswith("cell_"):
                    _, r, c = key.split("_")
                    layout[int(r)][int(c)] = val
                    
        # Restore resource capacity if provided
        if resource_manager and original_table_capacity is not None:
            resource_manager.capacity = original_table_capacity
            
        self.original_states.clear()
