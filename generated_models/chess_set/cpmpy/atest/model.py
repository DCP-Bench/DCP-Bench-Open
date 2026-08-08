from cpmpy import *
import json

# Decision variables
small_set = intvar(0, 200, name="small_set")
large_set = intvar(0, 200, name="large_set")
max_profit = intvar(0, 4000, name="max_profit")

# Model
model = Model()

# Objective: maximize profit
model.maximize(5 * small_set + 20 * large_set)

# Constraints
# Lathe hours constraint: 3 * small_set + 2 * large_set <= 160
model += [3 * small_set + 2 * large_set <= 160]

# Boxwood constraint: 1 * small_set + 3 * large_set <= 200
model += [small_set + 3 * large_set <= 200]

# Profit calculation
model += [max_profit == 5 * small_set + 20 * large_set]

# Solve the model
model.solve()

# Print the solution in the correct order
solution = {
    "small_set": small_set.value(),
    "large_set": large_set.value(),
    "max_profit": max_profit.value()
}
print(json.dumps(solution))