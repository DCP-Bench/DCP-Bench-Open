import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# This is a Set Cover problem:
# - Select minimum cost set of workers to cover all tasks
# - Each worker has a hiring cost and can perform certain tasks
# - Goal: Minimize total cost while ensuring all tasks are performed

# Input data
nb_workers = 32
num_tasks = 15

# Which worker is qualified for each task (1-based indexing)
Qualified = [
    [1, 9, 19, 22, 25, 28, 31],
    [2, 12, 15, 19, 21, 23, 27, 29, 30, 31, 32],
    [3, 10, 19, 24, 26, 30, 32],
    [4, 21, 25, 28, 32],
    [5, 11, 16, 22, 23, 27, 31],
    [6, 20, 24, 26, 30, 32],
    [7, 12, 17, 25, 30, 31],
    [8, 17, 20, 22, 23],
    [9, 13, 14, 26, 29, 30, 31],
    [10, 21, 25, 31, 32],
    [14, 15, 18, 23, 24, 27, 30, 32],
    [18, 19, 22, 24, 26, 29, 31],
    [11, 20, 25, 28, 30, 32],
    [16, 19, 23, 31],
    [9, 18, 26, 28, 31, 32]
]

Cost = [
    1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5,
    5, 6, 6, 6, 7, 8, 9
]

# Step 2: Model with CPMpy
# Decision variables: select[i] = 1 if worker i is selected
select = cp.boolvar(shape=nb_workers, name="select")

model = cp.Model()

# Constraints: Each task must be covered by at least one selected worker
for task_id in range(num_tasks):
    # Find all workers qualified for this task
    qualified_workers = Qualified[task_id]
    # Convert to 0-based indexing and create constraint
    qualified_indices = [w - 1 for w in qualified_workers]
    model += cp.sum([select[w] for w in qualified_indices]) >= 1

# Objective: Minimize total hiring cost
total_cost = cp.sum([select[i] * Cost[i] for i in range(nb_workers)])
model.minimize(total_cost)

# Step 3: Solve & Verify
if model.solve():
    # Extract solution
    selected_workers = select.value()
    optimal_cost = total_cost.value()
    
    solution = {
        "total_cost": int(optimal_cost),
        "workers": [int(x) for x in selected_workers]
    }
    
    # Verification: Check that all tasks are covered
    def verify_solution(sol):
        workers_selected = sol["workers"]
        
        # 1. Structural verification
        if len(workers_selected) != nb_workers:
            return False, f"Wrong number of workers: {len(workers_selected)} vs {nb_workers}"
        
        if not all(w in [0, 1] for w in workers_selected):
            return False, "Workers array should contain only 0s and 1s"
        
        # 2. Logical verification: Check all tasks are covered
        for task_id in range(num_tasks):
            qualified_workers = Qualified[task_id]
            task_covered = False
            for worker_1based in qualified_workers:
                worker_0based = worker_1based - 1
                if workers_selected[worker_0based] == 1:
                    task_covered = True
                    break
            
            if not task_covered:
                return False, f"Task {task_id} is not covered by any selected worker"
        
        # 3. Verify cost calculation
        calculated_cost = sum(Cost[i] for i in range(nb_workers) if workers_selected[i] == 1)
        if calculated_cost != sol["total_cost"]:
            return False, f"Cost mismatch: calculated {calculated_cost} vs reported {sol['total_cost']}"
        
        return True, "All constraints satisfied"
    
    valid, msg = verify_solution(solution)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    print(json.dumps(solution))
    
else:
    print(json.dumps({"error": "No solution found"}))