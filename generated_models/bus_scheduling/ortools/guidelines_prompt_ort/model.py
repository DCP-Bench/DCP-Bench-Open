
from ortools.sat.python import cp_model
import json

# Input data
demands = [4, 8, 10, 7, 12, 4]
num_slots = len(demands)

# Model definition
model = cp_model.CpModel()

# Decision Variables
# y[t]: number of buses starting a shift at slot t (covering t and t+1)
y = [model.NewIntVar(0, sum(demands), f'y[{t}]') for t in range(num_slots - 1)]
# x[t]: number of buses scheduled in slot t
x = [model.NewIntVar(0, sum(demands), f'x[{t}]') for t in range(num_slots)]

# Constraints: link x and y
# For slot 0: only y[0] covers
model.Add(x[0] == y[0])
# For slots 1 to num_slots-2: covered by y[t-1] and y[t]
for t in range(1, num_slots - 1):
    model.Add(x[t] == y[t - 1] + y[t])
# For last slot: only y[num_slots-2]
model.Add(x[num_slots - 1] == y[num_slots - 2])

# Demand constraints: each slot must meet its demand
for t in range(num_slots):
    model.Add(x[t] >= demands[t])

# Objective: minimize total buses (each bus runs one 8-hour shift y)
model.Minimize(sum(y))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'x': [solver.Value(x[t]) for t in range(num_slots)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
