# Import libraries
from cpmpy import *
import json

# Decision Variables
small_set = intvar(0, 200, name="small_set")  # Number of small chess sets
large_set = intvar(0, 200, name="large_set")  # Number of large chess sets
max_profit = intvar(0, 100000, name="max_profit")  # Maximum profit

# Model
model = Model()

# Constraints
# Lathe-hours constraint: 3*small_set + 2*large_set <= 160
model += (3 * small_set + 2 * large_set) <= 160

# Boxwood constraint: 1*small_set + 3*large_set <= 200
model += (1 * small_set + 3 * large_set) <= 200

# Profit calculation: max_profit = 5*small_set + 20*large_set
model += max_profit == (5 * small_set + 20 * large_set)

# Objective: maximize profit
model.maximize(max_profit)

# Solve
model.solve()

# Print solution
solution = {
    "small_set": small_set.value(),
    "large_set": large_set.value(),
    "max_profit": max_profit.value()
}
print(json.dumps(solution))
# End of CPMPy script