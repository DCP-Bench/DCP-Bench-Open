
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
small_set = cp.intvar(0, 200, name="small_set")
large_set = cp.intvar(0, 200, name="large_set")

# Constraints
# Lathe-hours: 3 hours per small set, 2 hours per large set, total 160 hours
model += (3 * small_set + 2 * large_set <= 160)
# Boxwood: 1 kg per small set, 3 kg per large set, total 200 kg
model += (small_set + 3 * large_set <= 200)

# Objective: Maximize profit (5 per small set, 20 per large set)
profit = 5 * small_set + 20 * large_set
model.maximize(profit)

# Solve and print
if model.solve():
    solution = {
        'small_set': int(small_set.value()),
        'large_set': int(large_set.value()),
        'max_profit': int(model.objective_value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
