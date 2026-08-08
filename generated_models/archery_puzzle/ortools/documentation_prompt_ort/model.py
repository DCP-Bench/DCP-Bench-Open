from ortools.sat.python import cp_model
import json

# Targets and the goal
targets = [16, 17, 23, 24, 39, 40]
goal = 100

# Model definition
model = cp_model.CpModel()

# Decision variables: number of hits on each target (non-negative integers)
hits = [model.NewIntVar(0, 1000, f'hits_{i}') for i in range(len(targets))]

# Calculate total score
total_score = sum(hits[i] * targets[i] for i in range(len(targets)))

# Auxiliary variable for absolute difference from goal
diff = model.NewIntVar(0, 1000, 'diff')

# Constraints to define diff = |total_score - goal|
model.Add(diff >= total_score - goal)
model.Add(diff >= goal - total_score)

# Objective: minimize the difference from 100
model.Minimize(diff)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'hits': [solver.Value(h) for h in hits]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")