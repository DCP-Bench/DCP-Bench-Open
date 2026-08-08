
import cpmpy as cp
import json

# Prices in GBP thousands (integers)
g_prices = [730, 1280, 3880]  # goalkeepers
d_prices = [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570]  # defenders
m_prices = [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130]  # midfielders
s_prices = [4460, 6470, 7780, 8390, 9500]  # strikers

# Decision variables: 0/1 whether to buy each player
g = cp.boolvar(shape=len(g_prices), name="g")
d = cp.boolvar(shape=len(d_prices), name="d")
m = cp.boolvar(shape=len(m_prices), name="m")
s = cp.boolvar(shape=len(s_prices), name="s")

# Total price variable (in thousands)
z = cp.intvar(0, 30000, name="z")  # cannot exceed 30,000 (i.e., 30 million)

# Build model
model = cp.Model()

# Group constraints
model += (cp.sum(g) == 1)       # exactly 1 goalkeeper
model += (cp.sum(d) >= 2)       # at least 2 defenders
model += (cp.sum(m) >= 3)       # at least 3 midfielders
model += (cp.sum(s) >= 2)       # at least 2 strikers

# At least 11 players in total
model += (cp.sum(g) + cp.sum(d) + cp.sum(m) + cp.sum(s) >= 11)

# Total price calculation and budget constraint (<= 30 million => 30000 thousands)
all_prices = g_prices + d_prices + m_prices + s_prices
all_vars = list(g) + list(d) + list(m) + list(s)
model += (z == cp.sum([p * x for p, x in zip(all_prices, all_vars)]))
model += (z <= 30000)

# Objective: maximize spending (z)
model.maximize(z)

# Solve and print
if model.solve():
    solution = {'z': int(z.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
