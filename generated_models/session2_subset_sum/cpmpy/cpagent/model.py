import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# This is a subset sum problem where we need to find how many bags of each type were stolen
# such that the total coins stolen equals 100
# Constraints:
# - Total coins stolen must equal 100
# - Number of bags for each type must be non-negative integers
# - At least one bag must be stolen

# Problem parameters
bag_types = [16, 17, 23, 24, 39, 40]
target_sum = 100
n_types = len(bag_types)

# Step 2: Model with CPMpy
# Decision variables: number of bags stolen for each type
# Upper bound: if we only steal bags of the smallest type, we need at most target_sum // min(bag_types)
max_bags_per_type = target_sum // min(bag_types) + 1  # Add 1 for safety
bags = cp.intvar(0, max_bags_per_type, shape=n_types, name="bags")

# Create model
model = cp.Model()

# Main constraint: total coins stolen must equal 100
total_coins = cp.sum([bags[i] * bag_types[i] for i in range(n_types)])
model += total_coins == target_sum

# At least one bag must be stolen (otherwise it's trivial)
model += cp.sum(bags) >= 1

# Step 3: Solve & Verify
# This is a satisfaction problem (any valid solution is acceptable), so we use model.solve()

if model.solve():
    # Extract solution
    solution_values = bags.value()
    
    # Create the required JSON format
    solution = {
        "bags": solution_values.tolist() if hasattr(solution_values, 'tolist') else list(solution_values)
    }
    
    # Verification (independent of CPMpy)
    def verify_solution(sol):
        bags_stolen = sol["bags"]
        
        # 1. Structural Verification
        if len(bags_stolen) != len(bag_types):
            return False, f"Wrong number of bag types: got {len(bags_stolen)}, expected {len(bag_types)}"
        
        # 2. Logical Verification
        # Check all values are non-negative integers
        for i, count in enumerate(bags_stolen):
            if not isinstance(count, int) or count < 0:
                return False, f"Invalid bag count for type {i}: {count}"
        
        # Check total coins equals target
        total = sum(bags_stolen[i] * bag_types[i] for i in range(len(bag_types)))
        if total != target_sum:
            return False, f"Total coins {total} != target {target_sum}"
        
        # Check at least one bag was stolen
        if sum(bags_stolen) == 0:
            return False, "No bags were stolen"
        
        return True, "All constraints satisfied"
    
    # Verify the solution
    valid, msg = verify_solution(solution)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))