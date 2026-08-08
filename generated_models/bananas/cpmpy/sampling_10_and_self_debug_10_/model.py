
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: quantities of each fruit (at least 1 of each)
bananas = cp.intvar(1, 100, name="bananas")
oranges = cp.intvar(1, 100, name="oranges")
mangoes = cp.intvar(1, 100, name="mangoes")
apples = cp.intvar(1, 100, name="apples")

# Constraints:
# 1) Total fruits = 100
model += (bananas + oranges + mangoes + apples == 100)

# 2) Total cost = $100
# Prices:
# 5 bananas cost $3  => cost per banana = 3/5
# 7 oranges cost $5  => cost per orange = 5/7
# 9 mangoes cost $7  => cost per mango = 7/9
# 3 apples cost $9   => cost per apple = 9/3 = 3
# Multiply cost equation by 315 (LCM of 5,7,9) to keep integers:
# 189*b + 225*o + 245*m + 945*a = 31500
model += (189*bananas + 225*oranges + 245*mangoes + 945*apples == 31500)

# Objective: minimize bananas and apples (user dislikes them)
model.minimize(cp.sum([bananas, apples]))

# Solve and print
if model.solve():
    solution = {
        'bananas': int(bananas.value()),
        'oranges': int(oranges.value()),
        'mangoes': int(mangoes.value()),
        'apples': int(apples.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
