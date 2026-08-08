
import cpmpy as cp
import json

target = 20

model = cp.Model()

# Decision variables: counts of 7-packs and 13-packs
x = cp.intvar(0, 100, name="x")  # 7-packs
y = cp.intvar(0, 100, name="y")  # 13-packs

# Constraints: total beers must meet or exceed target
model += (7 * x + 13 * y >= target)

# Objective: minimize the excess (difference above target)
model.minimize(7 * x + 13 * y - target)

if model.solve():
    solution = {
        'counts': [int(x.value()), int(y.value())]
    }
    print(json.dumps(solution))
else:
    print("No solution found.")
