
from ortools.sat.python import cp_model
import json

# Denominations in cents
denoms = [1, 2, 5, 10, 20, 50]
max_amount = 99  # we need to cover all amounts from 1 to 99 cents

# Create the CP model
model = cp_model.CpModel()

# Decision variables: number of coins of each denomination
# Upper bound for each coin type is max_amount // denomination
x = []
for i, d in enumerate(denoms):
    ub = max_amount // d
    x_var = model.NewIntVar(0, ub, f'x[{i}]')
    x.append(x_var)

# Auxiliary variables y[i,t]: how many coins of type i are used to pay amount t
# Domain 0..ub and constrained by y[i,t] <= x[i]
y = {}
for i, d in enumerate(denoms):
    ub = max_amount // d
    for t in range(1, max_amount + 1):
        y_var = model.NewIntVar(0, ub, f'y[{i},{t}]')
        model.Add(y_var <= x[i])
        y[(i, t)] = y_var

# For each amount t, the sum of coins used must equal t
for t in range(1, max_amount + 1):
    model.Add(
        sum(y[(i, t)] * denoms[i] for i in range(len(denoms)))
        == t
    )

# Objective: minimize total number of coins
model.Minimize(sum(x))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'x': [solver.Value(x[i]) for i in range(len(denoms))]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
