
import cpmpy as cp
import json

# Data
lathe_hours_per_small = 3
lathe_hours_per_large = 2
num_lathes = 4
hours_per_lathe = 40
total_lathe_hours = num_lathes * hours_per_lathe  # 160 hours

boxwood_per_small = 1
boxwood_per_large = 3
total_boxwood = 200

profit_per_small = 5
profit_per_large = 20

# Model definition
model = cp.Model()

# Decision Variables
# Number of small and large sets produced (non-negative integers)
small_set = cp.intvar(0, total_boxwood, name="small_set")
large_set = cp.intvar(0, total_boxwood // boxwood_per_large, name="large_set")

# Constraints
# Lathe hours constraint
model += (lathe_hours_per_small * small_set + lathe_hours_per_large * large_set <= total_lathe_hours)
# Boxwood constraint
model += (boxwood_per_small * small_set + boxwood_per_large * large_set <= total_boxwood)

# Objective: maximize profit
profit = profit_per_small * small_set + profit_per_large * large_set
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
