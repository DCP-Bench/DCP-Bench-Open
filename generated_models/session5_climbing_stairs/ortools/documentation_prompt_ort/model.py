from ortools.sat.python import cp_model
import json

# Input data
n = 20  # total steps in the stair
m1 = 3  # minimum steps per move
m2 = 5  # maximum steps per move

# Model definition
model = cp_model.CpModel()

# Decision Variables
# steps[i] represents the number of steps taken at move i (0 if no move)
# We allow up to n moves (worst case: all moves are 1 step, but here min step is 3, so n moves is safe upper bound)
steps = [model.NewIntVar(0, m2, f'steps_{i}') for i in range(n)]

# Constraints
# Each step must be either 0 or between m1 and m2 inclusive
for i in range(n):
    # steps[i] == 0 or steps[i] in [m1, m2]
    # We enforce this by: steps[i] == 0 or steps[i] >= m1
    # So steps[i] in {0} U [m1..m2]
    model.AddBoolOr([steps[i] == 0, steps[i] >= m1])
    # Also steps[i] <= m2 is already ensured by variable domain

# The sum of all steps must be exactly n
model.Add(sum(steps) == n)

# Once a zero step is taken, all subsequent steps must be zero (no moves after reaching top)
for i in range(n - 1):
    # If steps[i] == 0 then steps[i+1] == 0
    zero_i = model.NewBoolVar(f'zero_{i}')
    zero_i_plus_1 = model.NewBoolVar(f'zero_{i+1}')
    model.Add(steps[i] == 0).OnlyEnforceIf(zero_i)
    model.Add(steps[i] != 0).OnlyEnforceIf(zero_i.Not())
    model.Add(steps[i+1] == 0).OnlyEnforceIf(zero_i)
    # No constraint if zero_i is false

# Objective: no objective, just find any feasible solution

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'steps': [solver.Value(s) for s in steps]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")