
from ortools.sat.python import cp_model
import json

# Input data
coin_values = [1, 2, 5, 10, 25, 50]  # Values of each coin type
availabilities = [20, 10, 15, 8, 4, 2]  # Number of coins available for each type
target_amount = 199  # Amount of euros to give as change

# Create the model
model = cp_model.CpModel()

# Decision variables: number of coins of each type to give
coin_counts = [
    model.NewIntVar(0, availabilities[i], f'coin_{coin_values[i]}')
    for i in range(len(coin_values))
]

# Constraint: total value of given coins must equal the target amount
model.Add(
    sum(coin_counts[i] * coin_values[i] for i in range(len(coin_values)))
    == target_amount
)

# Objective: minimize the total number of coins used
model.Minimize(sum(coin_counts))

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print the solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'coin_counts': [solver.Value(c) for c in coin_counts]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
