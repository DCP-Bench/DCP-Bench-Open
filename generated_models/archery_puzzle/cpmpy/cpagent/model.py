import cpmpy as cp
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Find the closest possible score to 100 using archery targets
# Available targets: 16, 17, 23, 24, 39, 40
# Can use any number of arrows (including 0) on each target
# Objective: minimize |total_score - 100|
# Output: number of hits on each target

targets = [16, 17, 23, 24, 39, 40]
target_score = 100
n_targets = len(targets)

# Step 2: Model with CPMpy
# Upper bound for arrows per target
max_arrows = target_score // min(targets) + 2

# Decision variables: number of hits on each target
hits = cp.intvar(0, max_arrows, shape=n_targets, name="hits")

# Create the model
model = cp.Model()

# Calculate total score
total_score = cp.sum([hits[i] * targets[i] for i in range(n_targets)])

# Minimize absolute difference from target score
# Use auxiliary variable for |total_score - 100|
diff = cp.intvar(0, target_score, name="diff")

# |total_score - 100| = diff
# This means: total_score - 100 = diff OR total_score - 100 = -diff
model += (total_score == target_score + diff) | (total_score == target_score - diff)

# Minimize the difference (optimization problem)
model.minimize(diff)

# Step 3: Solve and verify
if model.solve():
    # Extract solution
    hits_solution = hits.value()
    
    # Create solution in required JSON format
    solution = {
        "hits": hits_solution.tolist()
    }
    
    # Verification: Check that solution is correct
    def verify_solution(sol, targets, target_score):
        hits_list = sol["hits"]
        
        # Structural check
        if len(hits_list) != len(targets):
            return False
        
        # Logical check: calculate total score
        total_achieved = sum(hits_list[i] * targets[i] for i in range(len(targets)))
        
        # All hits should be non-negative
        if any(h < 0 for h in hits_list):
            return False
            
        return True
    
    assert verify_solution(solution, targets, target_score), "Solution verification failed!"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))