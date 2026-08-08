
from ortools.sat.python import cp_model
import json

# Parameters
num_steps = 20  # total number of steps to climb
min_step = 3    # minimum step size
max_step = 5    # maximum step size

# Create the CP-SAT model
model = cp_model.CpModel()

# Decision variables:
# steps[i] is the number of stairs climbed on move i (0 if no move)
steps = [
    model.NewIntVar(0, max_step, f"step_{i}") for i in range(num_steps)
]

# used[i] indicates whether move i is actually used (1) or it's after the climb (0)
used = [
    model.NewBoolVar(f"used_{i}") for i in range(num_steps)
]

# Link steps and used:
for i in range(num_steps):
    # If used[i] == False then steps[i] == 0
    model.Add(steps[i] == 0).OnlyEnforceIf(used[i].Not())
    # If used[i] == True then steps[i] must be between min_step and max_step
    model.Add(steps[i] >= min_step).OnlyEnforceIf(used[i])
    model.Add(steps[i] <= max_step).OnlyEnforceIf(used[i])

# Ensure that once we stop climbing (used[i] == 0), all subsequent moves are 0
for i in range(num_steps - 1):
    model.Add(used[i] >= used[i + 1])

# The sum of all steps must equal the total number of stairs
model.Add(sum(steps) == num_steps)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'steps': [solver.Value(steps[i]) for i in range(num_steps)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
