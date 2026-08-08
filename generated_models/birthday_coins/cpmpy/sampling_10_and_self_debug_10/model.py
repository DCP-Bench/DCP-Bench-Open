
import cpmpy as cp
import json

# Data
total_coins = 15
# Total amount in pence: £1 5s 6d = 1*240 + 5*12 + 6 = 240 + 60 + 6 = 306 pence
total_pence = 306

# Values of coins in pence
half_crown_value = 2 * 12 + 6  # 30 pence
shilling_value = 12            # 12 pence
sixpence_value = 6             # 6 pence

# Model definition
model = cp.Model()

# Decision Variables
# Number of half-crowns, shillings, sixpences
half_crowns = cp.intvar(0, total_coins, name="half_crowns")
shillings = cp.intvar(0, total_coins, name="shillings")
sixpences = cp.intvar(0, total_coins, name="sixpences")

# Constraints
# Total number of coins is 15
model += (half_crowns + shillings + sixpences == total_coins)

# Total value in pence is 306
model += (half_crowns * half_crown_value + shillings * shilling_value + sixpences * sixpence_value == total_pence)

# Solve and print
if model.solve():
    solution = {'half_crowns': int(half_crowns.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
