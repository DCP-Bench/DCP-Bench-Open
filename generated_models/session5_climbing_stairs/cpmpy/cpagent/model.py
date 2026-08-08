import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# Problem: Climb 20 steps using moves of 3, 4, or 5 steps at a time
# Output: List of 20 integers where each is 3, 4, 5, or 0 (if no move at that position)
# Constraints:
# 1. Each move must be 0, 3, 4, or 5 steps
# 2. Total steps must equal exactly 20
# 3. Once we reach the target (start using 0s), we stay at 0

# Step 2: Model with CPMpy
n_positions = 20
target_steps = 20

# Decision variables: steps[i] is the number of steps taken at position i
steps = cp.intvar(0, 5, shape=n_positions, name="steps")

model = cp.Model()

# Constraint 1: Each step must be 0, 3, 4, or 5
for i in range(n_positions):
    model += (steps[i] == 0) | (steps[i] == 3) | (steps[i] == 4) | (steps[i] == 5)

# Constraint 2: Total steps must equal exactly 20
model += cp.sum(steps) == target_steps

# Constraint 3: Once we stop (use 0), we stay stopped
for i in range(n_positions - 1):
    model += (steps[i] == 0).implies(steps[i+1] == 0)

# Step 3: Solve and verify
if model.solve():
    solution_steps = steps.value().tolist()
    
    # Verification
    def verify_solution(steps_list):
        # Check length
        if len(steps_list) != 20:
            return False
        
        # Check each step is valid
        valid_steps = {0, 3, 4, 5}
        for step in steps_list:
            if step not in valid_steps:
                return False
        
        # Check total equals 20
        if sum(steps_list) != 20:
            return False
        
        # Check "once stopped, stay stopped"
        found_zero = False
        for step in steps_list:
            if step == 0:
                found_zero = True
            elif found_zero:
                return False
        
        return True
    
    assert verify_solution(solution_steps), "Solution verification failed!"
    
    # Step 4: Output
    solution = {"steps": solution_steps}
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))