
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# number of half-crowns, shillings, sixpences (non-negative integers, at most 15 coins each)
half_crowns = cp.intvar(0, 15, name="half_crowns")
shillings = cp.intvar(0, 15, name="shillings")
sixpence = cp.intvar(0, 15, name="sixpence")

# Constraints
# Total coins = 15
model += (half_crowns + shillings + sixpence == 15)

# Values in pence: half-crown = 30, shilling = 12, sixpence = 6
# Total value = £1 5s 6d = 306 pence
model += (30 * half_crowns + 12 * shillings + 6 * sixpence == 306)

# Solve and print
if model.solve():
    solution = {'half_crowns': int(half_crowns.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
