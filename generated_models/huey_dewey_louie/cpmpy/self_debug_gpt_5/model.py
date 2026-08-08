
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables (1 = guilty, 0 = not guilty)
huey = cp.boolvar(name="huey")
dewey = cp.boolvar(name="dewey")
louie = cp.boolvar(name="louie")

# Constraints
# Huey: Dewey and Louie have equal guilt
model += (dewey == louie)
# Dewey: If Huey is guilty, then so is Dewey
model += huey.implies(dewey)
# Louie: Dewey and Louie are not both guilty
model += ~(dewey & louie)

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
