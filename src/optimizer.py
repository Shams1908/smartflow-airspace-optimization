import networkx as nx

def build_graph(layout):
    """
    Convert a 2D grid layout into a NetworkX graph.
    Walkable cells are represented as nodes, and adjacent empty cells are edges.
    Assumes layout is a 2D container (list of lists) where:
    0 = Walkable
    1 = Obstacle (Wall/Table/Counter - Not walkable)

    Args:
        layout (list of lists): The map representation.

    Returns:
        nx.Graph: Spatial graph for pathfinding.
    """
    graph = nx.Graph()
    if not layout or not layout[0]:
        return graph

    rows = len(layout)
    cols = len(layout[0])

    # Step 1: Add Walkable Nodes
    for r in range(rows):
        for c in range(cols):
            if layout[r][c] == 0:  # Walkable
                graph.add_node((r, c))

    # Step 2: Add Edges to Adjacent Nodes
    # Up, Down, Left, Right (4-way grid connection)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for r in range(rows):
        for c in range(cols):
            if layout[r][c] == 0:
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    # Check bounds
                    if 0 <= nr < rows and 0 <= nc < cols:
                        if layout[nr][nc] == 0:
                            # Add an edge with default weight
                            graph.add_edge((r, c), (nr, nc), weight=1.0)

    return graph

def find_path(graph, start, goal):
    """
    Uses A* to find the shortest path between start and goal.

    Args:
        graph (nx.Graph): Spatial representation.
        start (tuple): The starting (row, col) coordinate.
        goal (tuple): The goal (row, col) coordinate.

    Returns:
        list: List of coordinates representing the shortest path,
              or an empty list if no path exists.
    """
    def heuristic(u, v):
        # Manhattan distance for grid movement estimation
        return abs(u[0] - v[0]) + abs(u[1] - v[1])

    try:
        path = nx.astar_path(graph, start, goal, heuristic=heuristic, weight='weight')
        return path
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []

def update_congestion_weights(graph, density_map, base_cost=1.0):
    """
    Adjusts edge weights based on real-time congestion data.

    Args:
        graph (nx.Graph): The active routing graph.
        density_map (dict): Maps node coordinates to a congestion penalty score.
        base_cost (float): Default cost of traversal before penalties.
    """
    for u, v, data in graph.edges(data=True):
        # Calculate penalty based on the nodes the edge connects
        penalty_u = density_map.get(u, 0)
        penalty_v = density_map.get(v, 0)
        
        # Average congestion across the transition
        congestion_penalty = (penalty_u + penalty_v) / 2.0
        
        # Update routing cost
        data['weight'] = base_cost + congestion_penalty


############################################

if __name__ == "__main__":

    print("===== TEST 1: Basic Pathfinding =====")

    layout = [
        [0,0,0,0,0],
        [0,1,1,1,0],
        [0,0,0,1,0],
        [0,1,0,0,0],
        [0,0,0,1,0]
    ]

    start = (0,0)
    goal = (4,4)

    graph = build_graph(layout)

    print("Graph nodes:", len(graph.nodes()))
    print("Graph edges:", len(graph.edges()))

    path = find_path(graph,start,goal)

    print("Start:", start)
    print("Goal:", goal)
    print("Path:", path)