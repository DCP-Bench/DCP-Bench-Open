
import cpmpy as cp
import numpy as np
import json

# Data
GK_PRICES = np.array([730, 1280, 3880])  # in GBP thousands
D_PRICES = np.array([920, 1310, 1620, 2410, 2790, 3280, 3910, 4570])
M_PRICES = np.array([1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130])
S_PRICES = np.array([4460, 6470, 7780, 8390, 9500])

BUDGET = 30000  # GBP thousands

# Model definition
model = cp.Model()

# Decision Variables (1 if the player is selected, else 0)
gk = cp.boolvar(shape=len(GK_PRICES), name="gk")
defs = cp.boolvar(shape=len(D_PRICES), name="defs")
mid = cp.boolvar(shape=len(M_PRICES), name="mid")
strk = cp.boolvar(shape=len(S_PRICES), name="strk")

# Total spend variable (in GBP thousands)
z = cp.intvar(0, BUDGET, name="z")

# Constraints
model += (cp.sum(gk) == 1)          # exactly 1 goalkeeper
model += (cp.sum(defs) >= 2)        # at least 2 defenders
model += (cp.sum(mid) >= 3)         # at least 3 midfielders
model += (cp.sum(strk) >= 2)        # at least 2 strikers

total_players = cp.sum(gk) + cp.sum(defs) + cp.sum(mid) + cp.sum(strk)
model += (total_players >= 11)      # at least 11 players in total

total_cost = cp.sum(gk * GK_PRICES) + cp.sum(defs * D_PRICES) + cp.sum(mid * M_PRICES) + cp.sum(strk * S_PRICES)
model += (total_cost == z)          # define z as the total spend
model += (z <= BUDGET)              # cannot exceed the budget

# Objective: spend as much as possible without exceeding the budget
model.maximize(z)

# Solve and print
if model.solve():
    solution = {'z': int(z.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
