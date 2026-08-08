
import cpmpy as cp
import json

# Data
# Coin values in pence
VALUE_HALF_CROWN = 30   # 2 shillings and 6 pence
VALUE_SHILLING = 12
VALUE_SIXPENCE = 6

TOTAL_COINS = 15
TOTAL_PENCE = 240 + 5*12 + 6  # £1 5s 6d = 306 pence

# Model definition
model = cp.Model()

# Decision Variables
half_crowns = cp.intvar(0, TOTAL_COINS, name="half_crowns")
shillings = cp.intvar(0, TOTAL_COINS, name="shillings")
sixpence = cp.intvar(0, TOTAL_COINS, name="sixpence")

# Constraints
# Total count and total value
model += (half_crowns + shillings + sixpence == TOTAL_COINS)
model += (VALUE_HALF_CROWN*half_crowns + VALUE_SHILLING*shillings + VALUE_SIXPENCE*sixpence == TOTAL_PENCE)

# Enforce at least one of each coin type
model += (half_crowns >= 1)
model += (shillings >= 1)
model += (sixpence >= 1)

# Solve and print
if model.solve():
    solution = {'half_crowns': int(half_crowns.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
