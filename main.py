import time
from src.layout import create_layout
from src.simulation import Simulation
from src.visualization import Visualizer

def main():
    print("Initializing Smartflow Spatial Simulation...")
    # Generate Canteen Layout
    layout = create_layout()
    
    # Initialize Engine
    sim = Simulation(layout, spawn_rate=0.3)
    
    # Initialize Visualizer
    viz = Visualizer(layout)
    
    # Run loop
    total_steps = 100
    print(f"Running for {total_steps} steps...")
    
    for step in range(1, total_steps + 1):
        # Update logic
        sim.update()
        
        # Draw frame
        viz.render(sim.active_students, tick=sim.tick_count)
        
    print("\n--- Simulation Complete ---")
    
    # Generate report via Person 2's module
    report = sim.analytics.report()
    
    print("\nFinal Performance Report:")
    for key, value in report.items():
        print(f" - {key}: {value}")

if __name__ == "__main__":
    main()
