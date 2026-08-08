import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# This is a Resource-Constrained Project Scheduling Problem (RCPSP)
# Constraints:
# 1. Precedence constraints: certain jobs must finish before others start
# 2. Resource capacity constraints: limited resources available at any time
# 3. Minimize makespan (total project duration)

# Input data
durations_data = [0, 3, 2, 5, 4, 2, 3, 4, 2, 4, 6, 0]
resource_needs_data = [[0, 0], [5, 1], [0, 4], [1, 4], [1, 3], [3, 2], [3, 1], [2, 4], [4, 0], [5, 2], [2, 5], [0, 0]]
resource_capacities_data = [6, 8]
successors_link_data = [[0, 1], [0, 2], [0, 3], [1, 4], [1, 5], [2, 9], [2, 10], [3, 8], [4, 6], [4, 7], [5, 9], [5, 10], [6, 8], [6, 9], [7, 8], [8, 11], [9, 11], [10, 11]]

# Problem parameters
durations = durations_data
resource_needs = resource_needs_data
resource_capacities = resource_capacities_data
precedences = successors_link_data

n_jobs = len(durations)
n_resources = len(resource_capacities)
max_time = sum(durations)  # Upper bound for makespan

# Step 2: Model with CPMpy
# Decision variables
start_times = cp.intvar(0, max_time, shape=n_jobs, name="start")
makespan = cp.intvar(0, max_time, name="makespan")

# Create model
model = cp.Model()

# Constraint 1: Precedence constraints
# If job i must finish before job j starts: start[i] + duration[i] <= start[j]
for pred, succ in precedences:
    model += start_times[pred] + durations[pred] <= start_times[succ]

# Constraint 2: Makespan definition
# Makespan is the maximum completion time of all jobs
for i in range(n_jobs):
    model += start_times[i] + durations[i] <= makespan

# Constraint 3: Resource capacity constraints
# Use Cumulative constraint for each resource type
for r in range(n_resources):
    # Extract resource demands for resource type r
    demands_r = [resource_needs[i][r] for i in range(n_jobs)]
    end_times = [start_times[i] + durations[i] for i in range(n_jobs)]
    
    # Only add cumulative constraint if there are jobs that use this resource
    if any(demands_r):
        model += cp.Cumulative(start_times, durations, end_times, demands_r, resource_capacities[r])

# Objective: Minimize makespan
model.minimize(makespan)

# Step 3: Solve & Verify
if model.solve():
    # Extract solution
    start_solution = start_times.value()
    makespan_solution = makespan.value()
    
    solution = {
        "start_time": start_solution.tolist() if hasattr(start_solution, 'tolist') else list(start_solution)
    }
    
    # Verification
    def verify_solution(sol):
        """Verify the solution satisfies all constraints"""
        start_times_sol = sol["start_time"]
        
        # 1. Structural Verification
        if len(start_times_sol) != n_jobs:
            return False, f"Wrong number of start times: {len(start_times_sol)}, expected {n_jobs}"
        
        # 2. Logical Verification
        
        # Check precedence constraints
        for pred, succ in precedences:
            pred_completion = start_times_sol[pred] + durations[pred]
            succ_start = start_times_sol[succ]
            if pred_completion > succ_start:
                return False, f"Precedence violation: Job {pred} completes at {pred_completion} but job {succ} starts at {succ_start}"
        
        # Check resource constraints at each time point
        max_completion = max(start_times_sol[i] + durations[i] for i in range(n_jobs))
        
        for t in range(max_completion + 1):
            for r in range(n_resources):
                resource_usage = 0
                for i in range(n_jobs):
                    # Check if job i is active at time t
                    if start_times_sol[i] <= t < start_times_sol[i] + durations[i]:
                        resource_usage += resource_needs[i][r]
                
                if resource_usage > resource_capacities[r]:
                    return False, f"Resource {r} capacity violation at time {t}: usage={resource_usage}, capacity={resource_capacities[r]}"
        
        # 3. Objective verification
        calculated_makespan = max(start_times_sol[i] + durations[i] for i in range(n_jobs))
        if calculated_makespan != makespan_solution:
            return False, f"Makespan mismatch: calculated={calculated_makespan}, solver={makespan_solution}"
        
        return True, "All constraints satisfied"
    
    # Verify the solution
    valid, msg = verify_solution(solution)
    assert valid, f"Verification failed: {msg}"
    
    # Step 4: Output
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))