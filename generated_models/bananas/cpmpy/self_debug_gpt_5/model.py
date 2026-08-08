
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables (at least 1 of each fruit)
bananas = cp.intvar(1, 100, name="bananas")
oranges = cp.intvar(1, 100, name="oranges")
mangoes = cp.intvar(1, 100, name="mangoes")
apples = cp.intvar(1, 100, name="apples")

# Constraints
# Total fruits
model += (cp.sum([bananas, oranges, mangoes, apples]) == 100)

# Total cost: scale prices to integers by multiplying by LCM(5,7,9)=315
# 5 bananas cost 3 dollars  -> per banana 3/5 -> 189 per banana after scaling (3/5 * 315 = 189)
# 7 oranges cost 5 dollars  -> per orange 5/7 -> 225 per orange after scaling (5/7 * 315 = 225)
# 9 mangoes cost 7 dollars  -> per mango 7/9 -> 245 per mango after scaling (7/9 * 315 = 245)
# 3 apples cost 9 dollars   -> per apple 3     -> 945 per apple after scaling (3 * 315 = 945)
model += (189*bananas + 225*oranges + 245*mangoes + 945*apples == 31500)

# Objective: minimize bananas and apples (disliked fruits)
model.minimize(bananas + apples)

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
