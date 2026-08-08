
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
small_set = cp.intvar(0, 200, name="small_set")
large_set = cp.intvar(0, 200, name="large_set")

# Constraints
model += (3 * small_set + 2 * large_set <= 160)
model += (small_set + 3 * large_set <= 200)

# Objective
model.maximize(5 * small_set + 20 * large_set)

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
