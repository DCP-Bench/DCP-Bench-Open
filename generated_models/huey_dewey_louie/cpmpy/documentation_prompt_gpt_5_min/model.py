
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: 1 = guilty, 0 = innocent
huey = cp.boolvar(name="huey")
dewey = cp.boolvar(name="dewey")
louie = cp.boolvar(name="louie")

# Constraints from their truthful statements:
# Huey: Dewey and Louie have equal share; if one is guilty so is the other -> dewey == louie
model += (dewey == louie)

# Dewey: If Huey is guilty, then so am I -> huey implies dewey
model += huey.implies(dewey)

# Louie: Dewey and I are not both guilty -> dewey + louie <= 1
model += (dewey + louie <= 1)

# Solve and print
if model.solve():
    solution = {
        'huey': int(huey.value()),
        'dewey': int(dewey.value()),
        'louie': int(louie.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
