from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Constants for coin values in pence
HALF_CROWN_VALUE = 30  # 2 shillings 6 pence = 2*12 + 6 = 30 pence
SHILLING_VALUE = 12    # 1 shilling = 12 pence
SIXPENCE_VALUE = 6     # 6 pence

# Total coins and total value in pence
TOTAL_COINS = 15
TOTAL_VALUE_PENCE = 1 * 240 + 5 * 12 + 6  # £1 5s 6d = 240 + 60 + 6 = 306 pence

# Decision variables: number of each coin
half_crowns = model.NewIntVar(0, TOTAL_COINS, 'half_crowns')
shillings = model.NewIntVar(0, TOTAL_COINS, 'shillings')
sixpences = model.NewIntVar(0, TOTAL_COINS, 'sixpences')

# Constraints
# Total number of coins is 15
model.Add(half_crowns + shillings + sixpences == TOTAL_COINS)

# Total value in pence is 306
model.Add(half_crowns * HALF_CROWN_VALUE + shillings * SHILLING_VALUE + sixpences * SIXPENCE_VALUE == TOTAL_VALUE_PENCE)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'half_crowns': solver.Value(half_crowns)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")