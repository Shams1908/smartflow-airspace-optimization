import random

def resolve_movements(students):
    """
    Two-phase movement resolution to prevent collisions and deadlocks.
    Phase 1: Students propose next positions from their active path.
    Phase 2: Conflicts are resolved by priority, path length, and random fallback.

    Args:
        students (list): List of all active students requesting a move.

    Returns: 
        list: List of approved students who are allowed to step forward.
    """
    proposed_positions = {}

    # ----------------------------------------------------
    # Phase 1: Students propose next positions
    # ----------------------------------------------------
    for student in students:
        # Skip students that have no ongoing path
        if not getattr(student, 'path', None) or len(student.path) == 0:
            continue

        # Propose the very next step on their routing path
        next_pos = student.path[0]

        if next_pos not in proposed_positions:
            proposed_positions[next_pos] = []
        proposed_positions[next_pos].append(student)

    approved_students = []

    # ----------------------------------------------------
    # Phase 2: Conflicts are resolved
    # ----------------------------------------------------
    for pos, contenders in proposed_positions.items():
        if len(contenders) == 1:
            # No conflict for this cell
            approved_students.append(contenders[0])
        else:
            # Conflict Detected! Applying Tie-breaking logic:
            # 1. Higher priority (descending order)
            # 2. Shorter remaining path (ascending order)
            # 3. Random fallback (resolved by initial shuffle)
            
            # Apply random fallback first (least significant tie-breaker)
            random.shuffle(contenders)
            
            # Python's sort is stable, applying secondary criteria
            contenders.sort(key=lambda s: len(getattr(s, 'path', [])))
            
            # Primary criteria: priority outranks everything else
            contenders.sort(key=lambda s: getattr(s, 'priority', 0), reverse=True)

            # Extract the ultimate winner for that grid cell
            winner = contenders[0]
            approved_students.append(winner)

            # The other contenders must wait this tick, block their movement.
            # (In simulation code, their delay naturally triggers `wait_timer` incrementing)

    return approved_students
