class PerformanceAnalytics:
    """
    Measures system performance, tracks lifecycle metrics,
    and provides aggregated analytics reports.
    """
    def __init__(self):
        # Keep detailed records for simulation evaluation
        self.history = []
        self.system_ticks = 0
        self.total_congestion_measured = 0

    def record_tick(self, active_congestion=0):
        """
        Records global system stats per simulation tick.
        
        Args:
            active_congestion (float): The collective amount of congestion penalty on map for the tick.
        """
        self.system_ticks += 1
        self.total_congestion_measured += active_congestion

    def record_student_exit(self, student):
        """
        Called when a student completes their lifecycle and exits the canteen layout.
        Records their individual performance metrics.
        """
        self.history.append({
            "id": getattr(student, 'id', None),
            "wait_time": getattr(student, 'wait_timer', 0),
            "steps_taken": getattr(student, 'steps_taken', 0),
        })

    def report(self):
        """
        Returns a dictionary of aggregated metrics for the final presentation.
        
        Returns:
            dict: Collection of analytics values.
        """
        students_served = len(self.history)

        # Handle zero-division safety check early
        if students_served == 0:
            return {
                "avg_wait_time": 0.0,
                "avg_travel_distance": 0.0,
                "students_served": 0,
                "throughput": 0.0,
                "avg_congestion": 0.0
            }

        # Calculate Totals
        total_wait_time = sum(record["wait_time"] for record in self.history)
        total_travel_distance = sum(record["steps_taken"] for record in self.history)

        # Caculate Averages and KPIs
        avg_wait = total_wait_time / students_served
        avg_dist = total_travel_distance / students_served
        throughput = students_served / self.system_ticks if self.system_ticks > 0 else 0
        avg_congestion = self.total_congestion_measured / self.system_ticks if self.system_ticks > 0 else 0

        return {
            "avg_wait_time": round(avg_wait, 2),
            "avg_travel_distance": round(avg_dist, 2),
            "students_served": students_served,
            "throughput": round(throughput, 4),
            "avg_congestion": round(avg_congestion, 2)
        }

        