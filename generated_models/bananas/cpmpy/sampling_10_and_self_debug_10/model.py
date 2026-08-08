
import cpmpy as cp
import json

# Data
# Prices and fruit counts per bundle
# 3 dollars for 5 bananas
# 5 dollars for 7 oranges
# 7 dollars for 9 mangoes
# 9 dollars for 3 apples

# Model definition
model = cp.Model()

# Decision variables: number of bundles bought for each fruit type
# Since we want to minimize bananas and apples, but they must be at least 1 bundle each (minimum quantity)
bananas_bundles = cp.intvar(1, 100, name="bananas_bundles")
oranges_bundles = cp.intvar(1, 100, name="oranges_bundles")
mangoes_bundles = cp.intvar(1, 100, name="mangoes_bundles")
apples_bundles = cp.intvar(1, 100, name="apples_bundles")

# Total fruits and total cost
total_fruits = (5 * bananas_bundles) + (7 * oranges_bundles) + (9 * mangoes_bundles) + (3 * apples_bundles)
total_cost = (3 * bananas_bundles) + (5 * oranges_bundles) + (7 * mangoes_bundles) + (9 * apples_bundles)

# Constraints
model += (total_fruits == 100)
model += (total_cost == 100)

# Objective: minimize bananas and apples quantities (in bundles)
# Since the problem states bananas and apples should be minimum quantity,
# we minimize the sum of their bundles
model.minimize(bananas_bundles + apples_bundles)

# Solve and print
if model.solve():
    bananas = 5 * bananas_bundles.value()
    oranges = 7 * oranges_bundles.value()
    mangoes = 9 * mangoes_bundles.value()
    apples = 3 * apples_bundles.value()
    solution = {
        'bananas': int(bananas),
        'oranges': int(oranges),
        'mangoes': int(mangoes),
        'apples': int(apples)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
