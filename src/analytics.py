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

if __name__ == "__main__":

    print("===== PERFORMANCE ANALYTICS TEST =====")

    # ------------------------------------------------
    # Dummy Student class for testing
    # ------------------------------------------------
    class DummyStudent:
        def __init__(self, id, wait_timer, steps_taken):
            self.id = id
            self.wait_timer = wait_timer
            self.steps_taken = steps_taken

        def __repr__(self):
            return f"Student(id={self.id}, wait={self.wait_timer}, steps={self.steps_taken})"


    analytics = PerformanceAnalytics()

    # ------------------------------------------------
    # Simulate system ticks with congestion
    # ------------------------------------------------
    print("\nRecording simulation ticks...")

    analytics.record_tick(active_congestion=3)
    analytics.record_tick(active_congestion=2)
    analytics.record_tick(active_congestion=4)
    analytics.record_tick(active_congestion=1)

    print("Total ticks:", analytics.system_ticks)
    print("Total congestion:", analytics.total_congestion_measured)

    # ------------------------------------------------
    # Simulate students finishing lifecycle
    # ------------------------------------------------
    print("\nRecording student exits...")

    s1 = DummyStudent(1, wait_timer=5, steps_taken=20)
    s2 = DummyStudent(2, wait_timer=3, steps_taken=15)
    s3 = DummyStudent(3, wait_timer=7, steps_taken=25)

    analytics.record_student_exit(s1)
    analytics.record_student_exit(s2)
    analytics.record_student_exit(s3)

    print("Students recorded:", analytics.history)

    # ------------------------------------------------
    # Generate analytics report
    # ------------------------------------------------
    print("\nGenerating performance report...\n")

    report = analytics.report()

    for key, value in report.items():
        print(f"{key}: {value}")