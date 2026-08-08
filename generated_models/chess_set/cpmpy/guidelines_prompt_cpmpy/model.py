
import cpmpy as cp
import json

# Data
lathe_hours = 160  # total available lathe-hours per week
boxwood_kg = 200   # total available boxwood per week
# End of data

# Model definition
model = cp.Model()

# Decision Variables
small_set = cp.IntVar(0, 200, name="small_set")  # number of small chess sets
large_set = cp.IntVar(0, 200, name="large_set")  # number of large chess sets

# Constraints
# 3 hours lathe per small set, 2 hours per large set: total <= 160
model += 3 * small_set + 2 * large_set <= lathe_hours
# 1 kg boxwood per small set, 3 kg per large set: total <= 200
model += 1 * small_set + 3 * large_set <= boxwood_kg

# Objective: maximize profit (5 per small, 20 per large)
profit = 5 * small_set + 20 * large_set
model.maximize(profit)

# Solve and print
if model.solve():
    solution = {
        "small_set": int(small_set.value()),
        "large_set": int(large_set.value()),
        "max_profit": int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
