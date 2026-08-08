import cpmpy as cp
import numpy as np
import json

# Step 1: Problem data and analysis
weights = [4, 3, 1, 3, 2, 5, 2]
capacity = 5
num_bins = 5
num_items = len(weights)

# Step 2: Model with CPMpy
# Decision variables: bins[i] = which bin (0-indexed) item i is assigned to
bins = cp.intvar(0, num_bins-1, shape=num_items, name="bins")

model = cp.Model()

# Constraints: Total weight in each bin must not exceed capacity
for j in range(num_bins):
    # Sum weights of items assigned to bin j
    bin_weight = cp.sum([weights[i] * (bins[i] == j) for i in range(num_items)])
    model += bin_weight <= capacity

# Step 3: Solve (satisfaction problem)
if model.solve():
    # Extract solution
    bins_solution = bins.value().tolist()
    
    # Step 4: Verification (independent of CPMpy)
    def verify_solution(bins_assignment, weights, capacity, num_bins):
        # Structural verification
        if len(bins_assignment) != len(weights):
            return False, f"bins list length {len(bins_assignment)} != items count {len(weights)}"
        
        for i, bin_num in enumerate(bins_assignment):
            if not (0 <= bin_num < num_bins):
                return False, f"Item {i} assigned to invalid bin {bin_num}"
        
        # Logical verification - capacity constraints
        bin_weights = [0] * num_bins
        for i, bin_num in enumerate(bins_assignment):
            bin_weights[bin_num] += weights[i]
        
        for j, total_weight in enumerate(bin_weights):
            if total_weight > capacity:
                return False, f"Bin {j} has weight {total_weight} > capacity {capacity}"
        
        return True, "All constraints satisfied"
    
    valid, msg = verify_solution(bins_solution, weights, capacity, num_bins)
    assert valid, f"Verification failed: {msg}"
    
    # Output solution in required JSON format
    solution = {"bins": bins_solution}
    print(json.dumps(solution))
    
else:
    print(json.dumps({"error": "No solution found"}))