class StudentState:
    ENTER = "ENTER"
    GO_COUNTER = "GO_COUNTER"
    QUEUE = "QUEUE"
    GO_TABLE = "GO_TABLE"
    EAT = "EAT"
    EXIT = "EXIT"
    DONE = "DONE"


class Student:
    """
    Represents an agent moving through the canteen.
    """
    def __init__(self, student_id, start_pos, priority=1):
        self.id = student_id
        
        # Spatial attributes
        self.position = start_pos
        self.goal_position = None
        
        # Optimizer / Movement Resolver integration attributes
        self.path = []
        self.priority = priority
        
        # Lifecycle state
        self.state = StudentState.ENTER
        
        # Targets
        self.target_counter = None
        self.target_table = None
        
        # State timers and metrics
        self.wait_timer = 0
        self.steps_taken = 0
        self.remaining_eat_time = 0
        self.has_food = False
        
        # Resource Manager integration flags
        self.assigned_table = False
        self.is_waiting_for_table = False
        self.is_in_queue = False

    def __repr__(self):
        return f"Student({self.id}, pos={self.position}, state={self.state})"
