import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Find closest combination of 7-packs and 13-packs that meets or exceeds target
# Constraints: 7*sevens + 13*thirteens >= target
# Objective: minimize excess (total - target)

target = 20

# Step 2: Model with CPMpy
# Decision variables: counts of 7-packs and 13-packs
max_sevens = (target // 7) + 2  # Upper bound estimate
max_thirteens = (target // 13) + 2

sevens = cp.intvar(0, max_sevens, name="sevens")
thirteens = cp.intvar(0, max_thirteens, name="thirteens")

model = cp.Model()

# Constraint: total beers must meet or exceed target
total_beers = sevens * 7 + thirteens * 13
model += total_beers >= target

# Objective: minimize the excess (total_beers - target)
excess = total_beers - target
model.minimize(excess)

# Step 3: Solve & Verify
if model.solve():
    sevens_val = sevens.value()
    thirteens_val = thirteens.value()
    
    solution = {
        "counts": [sevens_val, thirteens_val]
    }
    
    # Verification - independent check
    def verify_solution(sol):
        counts = sol["counts"]
        if len(counts) != 2:
            return False, "Solution must have exactly 2 counts"
        
        sevens_count, thirteens_count = counts
        
        # Check non-negative
        if sevens_count < 0 or thirteens_count < 0:
            return False, "Counts must be non-negative"
        
        # Check constraint: meets or exceeds target
        total = sevens_count * 7 + thirteens_count * 13
        if total < target:
            return False, f"Total {total} is less than target {target}"
        
        return True, "Solution verified"
    
    valid, msg = verify_solution(solution)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))