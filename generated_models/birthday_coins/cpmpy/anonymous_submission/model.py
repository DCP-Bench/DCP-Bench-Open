# Import libraries
from cpmpy import *
import json

# Decision Variables
half_crowns = intvar(0, 15, name="half_crowns")  # Number of half-crowns
shillings = intvar(0, 15, name="shillings")  # Number of shillings
sixpence = intvar(0, 15, name="sixpence")  # Number of sixpence coins

# Model
model = Model()

# Constraints
# Total number of coins is 15
model += (half_crowns + shillings + sixpence == 15)

# Total value is £1 5s 6d = 306 pence
model += (30 * half_crowns + 12 * shillings + 6 * sixpence == 306)

# Solve
model.solve()

# Print solution (only half_crowns as requested)
solution = {"half_crowns": half_crowns.value()}
print(json.dumps(solution))
# End of CPMPy script