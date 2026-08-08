from ortools.sat.python import cp_model
import json

# Coin denominations in cents
denominations = [1, 2, 5, 10, 20, 50]

# Maximum amount to pay (less than one Euro = 99 cents)
max_amount = 99

# Model definition
model = cp_model.CpModel()

# Decision variables: number of each coin type used
x = [model.NewIntVar(0, max_amount, f'x_{d}') for d in denominations]

# For each amount from 1 to 99, we must be able to pay exactly using the chosen coins
# We model this by introducing auxiliary variables for each amount and coin type,
# representing how many coins of each type are used to pay that amount.
# These auxiliary variables must be <= the total coins available of that type.

# Create auxiliary variables: pay[a][c] = number of coins of denomination c used to pay amount a
pay = []
for a in range(1, max_amount + 1):
    pay.append([model.NewIntVar(0, max_amount, f'pay_{a}_{d}') for d in denominations])

# Constraints for each amount:
for a in range(1, max_amount + 1):
    # Sum of coins * denomination = amount a
    model.Add(sum(pay[a-1][i] * denominations[i] for i in range(len(denominations))) == a)
    # For each coin type, the number used to pay amount a cannot exceed total coins available
    for i in range(len(denominations)):
        model.Add(pay[a-1][i] <= x[i])

# Objective: minimize total number of coins
model.Minimize(sum(x))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'x': [solver.Value(coin) for coin in x]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")