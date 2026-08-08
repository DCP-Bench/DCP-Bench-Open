import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Layout:
#   0 1 2
#   3   4  
#   5 6 7
# Circles: positions 0, 2, 5, 7
# Squares: positions 1, 3, 4, 6
# Constraint: Each square equals sum of adjacent circles

# Step 2: Model with CPMpy
# Decision variables: positions[i] = digit at position i (1-8)
positions = cp.intvar(1, 8, shape=8, name="positions")

model = cp.Model()

# Constraint 1: All positions must have different digits (use all digits 1-8)
model += cp.AllDifferent(positions)

# Constraint 2: Each square equals sum of adjacent circles
square_to_circles = {
    1: [0, 2],  # Square 1 = Circle 0 + Circle 2
    3: [0, 5],  # Square 3 = Circle 0 + Circle 5  
    4: [2, 7],  # Square 4 = Circle 2 + Circle 7
    6: [5, 7]   # Square 6 = Circle 5 + Circle 7
}

for square, adj_circles in square_to_circles.items():
    model += positions[square] == cp.sum([positions[c] for c in adj_circles])

# Step 3: Solve & Verify
if model.solve():
    # Extract solution
    solution = {
        "positions": positions.value().tolist()
    }
    
    # Verification
    def verify_solution(sol):
        pos_vals = sol["positions"]
        
        # Structural verification
        if len(pos_vals) != 8:
            return False, f"Expected 8 positions, got {len(pos_vals)}"
        
        # Logical verification
        # Check all digits 1-8 are used exactly once
        if sorted(pos_vals) != list(range(1, 9)):
            return False, f"Not all digits 1-8 used exactly once"
        
        # Check square constraints
        for square, adj_circles in square_to_circles.items():
            expected_sum = sum(pos_vals[c] for c in adj_circles)
            actual_value = pos_vals[square]
            if actual_value != expected_sum:
                return False, f"Square {square} constraint violated"
        
        return True, "All constraints satisfied"
    
    valid, msg = verify_solution(solution)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))