import random
from src.layout import ENTRY, COUNTER, TABLE, EXIT, create_layout
from src.agents import Student, StudentState
from src.optimizer import build_graph, find_path, update_congestion_weights
from src.movement_resolver import resolve_movements
from src.resource_manager import ResourceManager
from src.analytics import PerformanceAnalytics

class Simulation:
    def __init__(self, layout, spawn_rate=0.2):
        self.layout = layout
        self.rows = len(layout)
        self.cols = len(layout[0])
        self.spawn_rate = spawn_rate
        
        # Spatial Graph initialization (provided by Person 2)
        # Using a layout mask where 0 is walkable, anything else is obstacle
        # Actually optimizer building graph expects: 0=Walkable, 1=Obstacle.
        # So we need to create a mask for it
        walkable_mask = [[0 if cell in [0, 4, 5, 2] else 1 for cell in row] for row in layout] 
        self.graph = build_graph(walkable_mask)
        
        # We also need to add tables to walkable after they are assigned or maybe they are always walkable?
        # A simpler mask: walls are 1, everything else is 0 so agents can route there
        simple_mask = [[1 if cell == 1 else 0 for cell in row] for row in layout]
        self.graph = build_graph(simple_mask)
        
        # Identifying POIs from layout
        self.entries = self._find_cells(ENTRY)
        self.counters = self._find_cells(COUNTER)
        self.tables = self._find_cells(TABLE)
        self.exits = self._find_cells(EXIT)
        
        # Simulation state
        self.active_students = []
        self.completed_students = []
        self.tick_count = 0
        self.next_student_id = 1
        
        # Initialize Person 2 modules
        total_tables = len(self.tables)
        self.resource_manager = ResourceManager(capacity=total_tables)
        self.analytics = PerformanceAnalytics()

    def _find_cells(self, cell_type):
        cells = []
        for r in range(self.rows):
            for c in range(self.cols):
                if self.layout[r][c] == cell_type:
                    cells.append((r, c))
        return cells

    def update(self):
        """
        Main simulation step. Updates state, routes agents, resolves movement.
        """
        self.tick_count += 1
        
        # 1. Spawn new students
        self.spawn_student()
        
        # 2. Update agent states (Wait timers, Eating timers, State transitions)
        self.handle_state_transitions()
        
        # 3. Pathfinding / Routing
        self.update_routing()
        
        # 4. Resolve Movements and apply them
        self.move_students()
        
        # 5. Remove exited students
        self.remove_completed_students()
        
        # 6. Update global analytics
        self.analytics.record_tick(active_congestion=len(self.active_students))

    def spawn_student(self):
        """Randomly spawns a student at an entry point."""
        if random.random() < self.spawn_rate and self.entries:
            start_pos = random.choice(self.entries)
            # Give random priority 1-3
            priority = random.randint(1, 3)
            student = Student(student_id=self.next_student_id, start_pos=start_pos, priority=priority)
            
            # Initialize lifecycle
            student.target_counter = random.choice(self.counters)
            student.goal_position = student.target_counter
            student.state = StudentState.GO_COUNTER
            
            self.active_students.append(student)
            self.next_student_id += 1

    def handle_state_transitions(self):
        for student in self.active_students:
            # Increment wait timer if they are stuck or queued
            if student.is_waiting_for_table or student.state == StudentState.QUEUE:
                student.wait_timer += 1
                
            # Handle reaching goals
            if student.position == student.goal_position:
                if student.state == StudentState.GO_COUNTER:
                    student.state = StudentState.QUEUE
                    student.has_food = True
                    
                    # Request table allocation from Person 2's module
                    self.resource_manager.request_table(student)
                    
                elif student.state == StudentState.GO_TABLE:
                    student.state = StudentState.EAT
                    student.remaining_eat_time = random.randint(10, 20)
                    
                elif student.state == StudentState.EXIT:
                    student.state = StudentState.DONE
                    
            # Handle eating duration
            if student.state == StudentState.EAT:
                student.remaining_eat_time -= 1
                if student.remaining_eat_time <= 0:
                    # Finished eating, free the table and go to exit
                    self.resource_manager.free_table(student)
                    student.state = StudentState.EXIT
                    student.goal_position = random.choice(self.exits)
            
            # Transition from queue to go table if table assigned
            if student.state == StudentState.QUEUE and student.assigned_table:
                student.state = StudentState.GO_TABLE
                student.target_table = random.choice(self.tables) # Simplified: pick any table coord
                student.goal_position = student.target_table

    def update_routing(self):
        """Calculates dynamic routing for all moving students using optimizer.py"""
        # Create a density map of current positions to penalize crowded areas
        density_map = {}
        for s in self.active_students:
            density_map[s.position] = density_map.get(s.position, 0) + 1
            
        update_congestion_weights(self.graph, density_map)
        
        for student in self.active_students:
            if student.state in (StudentState.GO_COUNTER, StudentState.GO_TABLE, StudentState.EXIT):
                if student.goal_position:
                    # Retrieve shortest path via Person 2's code
                    full_path = find_path(self.graph, student.position, student.goal_position)
                    
                    # Path includes current position at index 0, so slice from 1
                    if full_path and len(full_path) > 1:
                        student.path = full_path[1:]
                    else:
                        student.path = []

    def move_students(self):
        """Passes active moving students to Person 2's movement resolver and applies approved moves."""
        moving_students = [s for s in self.active_students if s.path and len(s.path) > 0]
        
        if not moving_students:
            return
            
        # Let movement_resolver handle conflicts
        approved_students = resolve_movements(moving_students)
        
        for student in approved_students:
            next_pos = student.path[0]
            student.position = next_pos
            student.steps_taken += 1
            # Path shrinks naturally
            student.path.pop(0)

    def remove_completed_students(self):
        completed = [s for s in self.active_students if s.state == StudentState.DONE]
        
        for s in completed:
            self.analytics.record_student_exit(s)
            self.completed_students.append(s)
            self.active_students.remove(s)
