
import cpmpy as cp
import json

# Data
# - small set: 3 lathe hours, 1 kg boxwood, profit $5
# - large set: 2 lathe hours, 3 kg boxwood, profit $20
# Resources:
# - 4 lathes * 40 hours = 160 lathe-hours
# - 200 kg boxwood

# Model definition
model = cp.Model()

# Decision Variables
# Bounds chosen reasonably large to let constraints limit them
small_set = cp.intvar(0, 200, name="small_set")
large_set = cp.intvar(0, 200, name="large_set")

# Constraints
# Lathe hours: 3 * small + 2 * large <= 160
model += (3 * small_set + 2 * large_set <= 160)

# Boxwood: 1 * small + 3 * large <= 200
model += (1 * small_set + 3 * large_set <= 200)

# Objective: maximize profit = 5 * small + 20 * large
model.maximize(cp.sum([5 * small_set, 20 * large_set]))

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
