
import cpmpy as cp
import json

# Data
lathe_hours_per_week = 160
boxwood_kg_per_week = 200
lathe_hours_small = 3
lathe_hours_large = 2
boxwood_small = 1
boxwood_large = 3
profit_small = 5
profit_large = 20

# Model definition
model = cp.Model()

# Decision Variables
# Number of small and large sets produced (non-negative integers)
small_set = cp.intvar(0, boxwood_kg_per_week, name="small_set")
large_set = cp.intvar(0, boxwood_kg_per_week // boxwood_large, name="large_set")

# Constraints
# Lathe hours constraint
model += (lathe_hours_small * small_set + lathe_hours_large * large_set <= lathe_hours_per_week)
# Boxwood constraint
model += (boxwood_small * small_set + boxwood_large * large_set <= boxwood_kg_per_week)

# Objective: maximize profit
model.maximize(profit_small * small_set + profit_large * large_set)

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
