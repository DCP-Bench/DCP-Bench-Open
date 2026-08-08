import cpmpy as cp
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Find subset of dummies whose numbers sum to exactly 50
# Constraints:
# 1. Each dummy can be knocked down (1) or not (0)
# 2. Sum of knocked down dummy values must equal exactly 50

# Given data
dummy_values = [15, 9, 30, 21, 19, 3, 12, 6, 25, 27]
target_sum = 50
n_dummies = len(dummy_values)

# Step 2: Model with CPMpy
# Decision variables: binary variables for each dummy
# dummies[i] = 1 if dummy i is knocked down, 0 otherwise
dummies = cp.boolvar(shape=n_dummies, name="dummies")

# Create model
model = cp.Model()

# Constraint: Sum of knocked down dummy values must equal exactly 50
model += cp.sum([dummies[i] * dummy_values[i] for i in range(n_dummies)]) == target_sum

# Step 3: Solve & Verify
if model.solve():
    # Extract solution
    solution_values = dummies.value()
    
    # Convert to boolean list for JSON output
    solution_bools = [bool(val) for val in solution_values]
    
    # Create the required JSON format
    solution = {"dummies": solution_bools}
    
    # Verification - independent check
    def verify_solution(sol):
        dummies_knocked = sol["dummies"]
        
        # 1. Structural Verification
        if len(dummies_knocked) != n_dummies:
            return False, f"Wrong length: got {len(dummies_knocked)}, expected {n_dummies}"
        
        if not all(isinstance(d, bool) for d in dummies_knocked):
            return False, "All elements must be boolean"
        
        # 2. Logical Verification
        total = sum(dummy_values[i] for i in range(n_dummies) if dummies_knocked[i])
        if total != target_sum:
            return False, f"Sum is {total}, expected {target_sum}"
        
        return True, "All constraints satisfied"
    
    valid, msg = verify_solution(solution)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))