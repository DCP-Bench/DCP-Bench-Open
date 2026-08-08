from ortools.sat.python import cp_model
import json

# Input data
coin_values = [1, 2, 5, 10, 25, 50]
available_coins = [20, 10, 15, 8, 4, 2]
total_change = 199

# Model definition
model = cp_model.CpModel()

# Decision Variables: number of coins of each type to give to Bob
coin_counts = [model.NewIntVar(0, available_coins[i], f'coin_{coin_values[i]}') for i in range(len(coin_values))]

# Constraint: total value of coins must be equal to the change amount
model.Add(sum(coin_counts[i] * coin_values[i] for i in range(len(coin_values))) == total_change)

# Objective: minimize the total number of coins used
model.Minimize(sum(coin_counts))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'coin_counts': [solver.Value(c) for c in coin_counts]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")