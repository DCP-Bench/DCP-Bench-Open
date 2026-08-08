
import cpmpy as cp
import json

# Data / indexing
# Persons: Debra=0, Janet=1, Hugh=2, Rick=3
# Allergies indices: eggs=0, mold=1, nuts=2, ragweed=3
# Surnames indices: baxter=0, lemon=1, malone=2, fleet=3

# Model definition
model = cp.Model()

# Decision Variables
surname = cp.intvar(0, 3, shape=4, name="surname")    # surname[p] in {0..3}
allergy = cp.intvar(0, 3, shape=4, name="allergy")    # allergy[p] in {0..3}

# Constraints
# All different for surnames and allergies
model += cp.AllDifferent(surname)
model += cp.AllDifferent(allergy)

# Rick is not allergic to mold
model += (allergy[3] != 1)

# Baxter is allergic to eggs:
# for any person p, if their surname is Baxter (0) then their allergy is eggs (0)
for p in range(4):
    model += (surname[p] == 0).implies(allergy[p] == 0)

# Hugh is neither surnamed Lemon nor Fleet
model += (surname[2] != 1)
model += (surname[2] != 3)

# Debra is allergic to ragweed
model += (allergy[0] == 3)

# Janet (who isn't Lemon) is neither allergic to eggs nor to mold
model += (surname[1] != 1)
model += (allergy[1] != 0)
model += (allergy[1] != 1)

# Solve and print
if model.solve():
    surv = surname.value().tolist()
    allv = allergy.value().tolist()

    # For each allergy (eggs=0, mold=1, nuts=2, ragweed=3), find the person index who has it
    eggs = next(i for i in range(4) if allv[i] == 0)
    mold = next(i for i in range(4) if allv[i] == 1)
    nuts = next(i for i in range(4) if allv[i] == 2)
    ragweed = next(i for i in range(4) if allv[i] == 3)

    # For each surname (baxter=0, lemon=1, malone=2, fleet=3), find the person index who has it
    baxter = next(i for i in range(4) if surv[i] == 0)
    lemon = next(i for i in range(4) if surv[i] == 1)
    malone = next(i for i in range(4) if surv[i] == 2)
    fleet = next(i for i in range(4) if surv[i] == 3)

    solution = {
        "eggs": int(eggs),
        "mold": int(mold),
        "nuts": int(nuts),
        "ragweed": int(ragweed),
        "baxter": int(baxter),
        "lemon": int(lemon),
        "malone": int(malone),
        "fleet": int(fleet)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
