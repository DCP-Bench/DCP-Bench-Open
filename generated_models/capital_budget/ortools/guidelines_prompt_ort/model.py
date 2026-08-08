
from ortools.sat.python import cp_model
import json

# Input data
npv = [16000, 22000, 12000, 8000]   # Net present values of investments 1–4
cost = [5000, 7000, 4000, 3000]     # Cash outflow requirements of investments 1–4
budget = 14000                      # Total available cash

# Model definition
model = cp_model.CpModel()

# Decision Variables: x[i] = 1 if investment i+1 is chosen, 0 otherwise
x = [model.NewBoolVar(f'x[{i}]') for i in range(4)]

# Constraint: total cost must not exceed available budget
model.Add(sum(cost[i] * x[i] for i in range(4)) <= budget)

# Objective: maximize total NPV
model.Maximize(sum(npv[i] * x[i] for i in range(4)))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'x': [solver.Value(x[i]) for i in range(4)]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
