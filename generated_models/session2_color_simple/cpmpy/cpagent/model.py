import cpmpy as cp
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Graph coloring of 6 countries to minimize colors used
# Countries: Belgium(1), Denmark(2), France(3), Germany(4), Netherlands(5), Luxembourg(6)
# Constraint: Adjacent countries must have different colors
# Objective: Minimize number of colors used

# Input data - adjacency relationships
graph = [
    [3, 1],     # France-Belgium
    [3, 6],     # France-Luxembourg  
    [3, 4],     # France-Germany
    [6, 4],     # Luxembourg-Germany
    [6, 1],     # Luxembourg-Belgium
    [1, 5],     # Belgium-Netherlands
    [1, 4],     # Belgium-Germany
    [4, 5],     # Germany-Netherlands
    [4, 2]      # Germany-Denmark
]

# Step 2: Model with CPMpy
n_countries = 6
max_colors = n_countries  # Upper bound: worst case each country different color

# Decision variables: colors[i-1] represents color of country i (0-indexed for 1-indexed countries)
colors = cp.intvar(1, max_colors, shape=n_countries, name="colors")

# Create model
model = cp.Model()

# Constraint: Adjacent countries must have different colors
for edge in graph:
    i, j = edge[0] - 1, edge[1] - 1  # Convert to 0-indexed
    model += colors[i] != colors[j]

# Objective: Minimize maximum color used (minimizes total colors)
max_color_used = cp.intvar(1, max_colors, name="max_color")
for i in range(n_countries):
    model += colors[i] <= max_color_used

# Symmetry breaking: assign color 1 to country 1 (Belgium)
model += colors[0] == 1

# Step 3: Solve and verify
model.minimize(max_color_used)

if model.solve():
    # Extract solution
    color_assignment = colors.value().tolist()
    
    # Verification
    def verify_solution(sol, graph_edges):
        """Verify that the coloring solution is valid"""
        colors_list = sol["colors"]
        
        # Structural verification
        if len(colors_list) != 6:
            return False, f"Expected 6 colors, got {len(colors_list)}"
        
        # Logical verification - check all adjacency constraints
        for edge in graph_edges:
            i, j = edge[0] - 1, edge[1] - 1  # Convert to 0-indexed
            if colors_list[i] == colors_list[j]:
                return False, f"Adjacent countries {i+1} and {j+1} have same color"
        
        return True, "Valid coloring"
    
    solution = {"colors": color_assignment}
    
    # Verify solution
    valid, message = verify_solution(solution, graph)
    assert valid, f"Verification failed: {message}"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))