import cpmpy as cp
import numpy as np
import json

# Step 1: Problem Analysis
# - Children sit in a line with given ratings
# - Each child gets at least 1 candy
# - If adjacent children have different ratings, the one with higher rating gets more candies
# - Minimize total candies

# Input data
ratings = [2, 3, 4, 4, 4, 2, 1, 3, 4]
n = len(ratings)

# Step 2: Model with CPMpy
# Decision variables: x[i] = number of candies for child i
# Each child gets at least 1 candy, upper bound is n (worst case)
x = cp.intvar(1, n, shape=n, name="candies")

model = cp.Model()

# Constraints: If adjacent children have different ratings, 
# the one with higher rating must get more candies
for i in range(n-1):
    if ratings[i] > ratings[i+1]:
        # Child i has higher rating than child i+1
        model += x[i] > x[i+1]
    elif ratings[i] < ratings[i+1]:
        # Child i+1 has higher rating than child i
        model += x[i+1] > x[i]
    # If ratings[i] == ratings[i+1], no constraint needed

# Objective: minimize total candies
total_candies = cp.sum(x)
model.minimize(total_candies)

# Step 3: Solve and verify
if model.solve():
    # Extract solution
    candies_solution = x.value()
    total_solution = total_candies.value()
    
    # Create solution in required format
    solution = {
        "z": int(total_solution),
        "x": candies_solution.tolist()
    }
    
    # Verification
    def verify_solution(sol, ratings):
        candies = sol["x"]
        total = sol["z"]
        n = len(candies)
        
        # Structural verification
        if len(candies) != len(ratings):
            return False, f"Length mismatch: {len(candies)} candies vs {len(ratings)} children"
        
        if sum(candies) != total:
            return False, f"Total mismatch: sum={sum(candies)} vs reported={total}"
        
        # Logical verification
        # Check minimum candy constraint
        for i, candy_count in enumerate(candies):
            if candy_count < 1:
                return False, f"Child {i} has {candy_count} candies, but minimum is 1"
        
        # Check adjacent rating constraints
        for i in range(n-1):
            if ratings[i] > ratings[i+1]:
                if candies[i] <= candies[i+1]:
                    return False, f"Child {i} (rating {ratings[i]}) should have more candies than child {i+1} (rating {ratings[i+1]})"
            elif ratings[i] < ratings[i+1]:
                if candies[i] >= candies[i+1]:
                    return False, f"Child {i+1} (rating {ratings[i+1]}) should have more candies than child {i} (rating {ratings[i]})"
        
        return True, "All constraints satisfied"
    
    # Verify the solution
    valid, msg = verify_solution(solution, ratings)
    assert valid, f"Solution verification failed: {msg}"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))