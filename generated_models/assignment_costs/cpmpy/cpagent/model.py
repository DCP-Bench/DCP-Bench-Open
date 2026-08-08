import cpmpy as cp
import numpy as np
import json

# Step 1: Problem Analysis
# - 4 tasks, 5 people
# - Each task must be assigned to exactly one person
# - Not all people need to be assigned
# - Minimize total assignment cost
# - Output: binary matrix x[task][person]

# Input data
cost = [
    [14, 5, 8, 7, 15],   # Task 0 costs
    [2, 12, 6, 5, 3],    # Task 1 costs  
    [7, 8, 3, 9, 7],     # Task 2 costs
    [2, 4, 6, 10, 1]     # Task 3 costs
]

n_tasks = len(cost)      # 4 tasks
n_people = len(cost[0])  # 5 people

# Step 2: Model with CPMpy
# Decision variables: x[i][j] = 1 if task i is assigned to person j
x = cp.boolvar(shape=(n_tasks, n_people), name="x")

model = cp.Model()

# Constraint: Each task must be assigned to exactly one person
for i in range(n_tasks):
    model += cp.sum(x[i, :]) == 1

# Objective: Minimize total assignment cost
cost_array = cp.cpm_array(cost)
total_cost = cp.sum(x * cost_array)
model.minimize(total_cost)

# Step 3: Solve and verify
if model.solve():
    # Extract solution
    x_solution = x.value()
    
    # Verification
    def verify_solution(x_matrix):
        # Check structural correctness
        if x_matrix.shape != (n_tasks, n_people):
            return False
        
        # Check logical correctness: each task assigned to exactly one person
        task_assignments = np.sum(x_matrix, axis=1)
        if not np.all(task_assignments == 1):
            return False
        
        # Check objective calculation
        calculated_cost = 0
        for i in range(n_tasks):
            for j in range(n_people):
                if x_matrix[i][j] == 1:
                    calculated_cost += cost[i][j]
        
        return calculated_cost == total_cost.value()
    
    assert verify_solution(x_solution), "Solution verification failed!"
    
    # Step 4: Output in required format
    solution = {
        "x": [[int(val) for val in row] for row in x_solution]
    }
    
    print(json.dumps(solution))
    
else:
    print(json.dumps({"error": "No solution found"}))