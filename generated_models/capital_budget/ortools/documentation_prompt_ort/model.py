from ortools.sat.python import cp_model
import json

# Input data
npvs = [16000, 22000, 12000, 8000]  # Net Present Values for investments 1 to 4
costs = [5000, 7000, 4000, 3000]    # Costs for investments 1 to 4
budget = 14000                      # Available budget

# Model definition
model = cp_model.CpModel()

# Decision Variables: x[i] = 1 if investment i is chosen, 0 otherwise
x = [model.NewBoolVar(f'x{i+1}') for i in range(4)]

# Constraint: Total cost of chosen investments must not exceed the budget
model.Add(sum(x[i] * costs[i] for i in range(4)) <= budget)

# Objective: Maximize total NPV of chosen investments
model.Maximize(sum(x[i] * npvs[i] for i in range(4)))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'x': [solver.Value(var) for var in x]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")