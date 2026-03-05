import heapq

class ResourceManager:
    """
    Manages limited spatial resources like seating tables.
    Tracks capacity, allocates resources dynamically, and maintains waiting queues.
    """
    def __init__(self, capacity):
        self.capacity = capacity
        self.available = capacity
        # Min-heap queue for prioritization
        self.wait_queue = []
        # Fallback counter to preserve entry-time ordering on tie-breaks
        self.arrival_counter = 0

    def request_table(self, student):
        """
        Process a student's request for a table.
        
        Args:
            student: Student object containing priority and state.
            
        Returns: 
            bool: True if table is allocated, False if they must wait in queue.
        """
        if self.available > 0:
            self.available -= 1
            student.assigned_table = True
            student.is_waiting_for_table = False
            student.is_in_queue = False
            return True
        else:
            self.arrival_counter += 1
            # Priority queue: tuple of (-priority, arrival_counter, student)
            # Negating priority because heapq is a min-heap; higher priority processed first.
            heapq.heappush(self.wait_queue, (-student.priority, self.arrival_counter, student))
            student.is_waiting_for_table = True
            student.is_in_queue = True
            return False

    def free_table(self, student):
        """
        Free a table when a student leaves.
        Checks queue and allocates table to the next student if anyone is waiting.
        """
        if getattr(student, 'assigned_table', False):
            student.assigned_table = False
            self.available += 1
            return self.update_queue()
        return []

    def update_queue(self):
        """
        Assigns newly freed tables to waiting students based on priority.
        
        Returns:
            list: List of students who were just allocated a table.
        """
        newly_allocated = []
        while self.available > 0 and self.wait_queue:
            priority, arrival, next_student = heapq.heappop(self.wait_queue)
            self.available -= 1
            next_student.assigned_table = True
            next_student.is_waiting_for_table = False
            next_student.is_in_queue = False
            newly_allocated.append(next_student)
            
        return newly_allocated


#####

if __name__ == "__main__":
    print("===== RESOURCE MANAGER TEST =====")

    # Dummy student class for testing
    class DummyStudent:
        def __init__(self, id, priority):
            self.id = id
            self.priority = priority
            self.assigned_table = False
            self.is_waiting_for_table = False
            self.is_in_queue = False

        def __repr__(self):
            return f"Student(id={self.id}, priority={self.priority})"


    # Create resource manager with only 2 tables
    manager = ResourceManager(capacity=2)

    # Create test students
    s1 = DummyStudent(1, priority=1)
    s2 = DummyStudent(2, priority=2)
    s3 = DummyStudent(3, priority=3)
    s4 = DummyStudent(4, priority=1)

    students = [s1, s2, s3, s4]

    print("\n--- Students requesting tables ---")

    for s in students:
        allocated = manager.request_table(s)
        print(f"Student {s.id} request -> allocated:", allocated)

    print("\nAvailable tables:", manager.available)
    print("Queue contents:", manager.wait_queue)

    print("\n--- Freeing table from Student 1 ---")
    newly_allocated = manager.free_table(s1)

    print("Students who got table:", newly_allocated)
    print("Available tables:", manager.available)
    print("Queue contents:", manager.wait_queue)

    print("\n--- Freeing table from Student 2 ---")
    newly_allocated = manager.free_table(s2)

    print("Students who got table:", newly_allocated)
    print("Available tables:", manager.available)
    print("Queue contents:", manager.wait_queue)