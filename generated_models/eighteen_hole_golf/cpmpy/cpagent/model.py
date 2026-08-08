import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Generate an 18-hole golf course
# - Each hole has length 3, 4, or 5
# - Total length must be exactly 72
# - This is a satisfaction problem (any valid solution is acceptable)

# Step 2: Model with CPMpy
# Decision variables: 18 holes, each with length 3, 4, or 5
holes = cp.intvar(3, 5, shape=18, name="holes")

# Create the model
model = cp.Model()

# Constraint: total length must be exactly 72
model += cp.sum(holes) == 72

# Step 3: Solve and verify
if model.solve():
    # Extract solution
    solution_values = holes.value()
    
    # Independent verification
    def verify_solution(hole_lengths):
        """Verify the golf course solution independently of CPMpy"""
        
        # 1. Structural Verification
        if len(hole_lengths) != 18:
            return False, f"Wrong number of holes: {len(hole_lengths)}, expected 18"
        
        # 2. Logical Verification
        # Check each hole length is valid (3, 4, or 5)
        for i, length in enumerate(hole_lengths):
            if length not in [3, 4, 5]:
                return False, f"Invalid hole length {length} at hole {i+1}, must be 3, 4, or 5"
        
        # Check total length is exactly 72
        total = sum(hole_lengths)
        if total != 72:
            return False, f"Total length is {total}, expected 72"
        
        return True, "All constraints satisfied"
    
    # Verify our solution
    valid, msg = verify_solution(solution_values)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output in required JSON format
    solution = {
        "holes": solution_values.tolist()
    }
    
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))