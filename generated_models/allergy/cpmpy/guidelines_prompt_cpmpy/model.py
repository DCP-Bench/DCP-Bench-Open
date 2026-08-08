
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# allergy[p] = 0: eggs, 1: mold, 2: nuts, 3: ragweed
allergy = cp.intvar(0, 3, shape=4, name="allergy")
# surname[p] = 0: Baxter, 1: Lemon, 2: Malone, 3: Fleet
surname = cp.intvar(0, 3, shape=4, name="surname")

# All different constraints
model += [cp.AllDifferent(allergy), cp.AllDifferent(surname)]

# Constraints
# Rick = person 3 is not allergic to mold (1)
model += (allergy[3] != 1)
# Debra = person 0 is allergic to ragweed (3)
model += (allergy[0] == 3)
# Janet = person 1 is neither allergic to eggs (0) nor to mold (1)
model += (allergy[1] != 0)
model += (allergy[1] != 1)

# Baxter (surname 0) is allergic to eggs (0).
# Enforce equivalence: surname[p]==0 <=> allergy[p]==0
for p in range(4):
    model += cp.implies(surname[p] == 0, allergy[p] == 0)
    model += cp.implies(allergy[p] == 0, surname[p] == 0)

# Hugh = person 2 is neither surnamed Lemon (1) nor Fleet (3)
model += (surname[2] != 1)
model += (surname[2] != 3)
# Janet = person 1 is not surnamed Lemon (1)
model += (surname[1] != 1)

# Solve the model
if model.solve():
    # Retrieve solutions
    allergy_vals = allergy.value().tolist()
    surname_vals = surname.value().tolist()
    # Invert mappings for output
    eggs    = allergy_vals.index(0)
    mold    = allergy_vals.index(1)
    nuts    = allergy_vals.index(2)
    ragweed = allergy_vals.index(3)
    baxter  = surname_vals.index(0)
    lemon   = surname_vals.index(1)
    malone  = surname_vals.index(2)
    fleet   = surname_vals.index(3)

    solution = {
        "eggs": eggs,
        "mold": mold,
        "nuts": nuts,
        "ragweed": ragweed,
        "baxter": baxter,
        "lemon": lemon,
        "malone": malone,
        "fleet": fleet
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
