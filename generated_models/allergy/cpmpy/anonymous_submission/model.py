from cpmpy import *
import json
import numpy as np

# Decision Variables
# Friends: Debra=0, Janet=1, Hugh=2, Rick=3
# Allergies: eggs=0, mold=1, nuts=2, ragweed=3
# Surnames: Baxter=0, Lemon=1, Malone=2, Fleet=3

allergies = intvar(0, 3, shape=4, name="allergies")  # allergies[friend] = allergy
surnames = intvar(0, 3, shape=4, name="surnames")    # surnames[friend] = surname

# Model
model = Model()

# All variables must be distinct
model += AllDifferent(allergies)
model += AllDifferent(surnames)

# Constraint 1: Rick is not allergic to mold (Rick=3, mold=1)
model += allergies[3] != 1

# Constraint 2: Baxter is allergic to eggs (Baxter=0, eggs=0)
model += (surnames == 0).implies(allergies == 0)

# Constraint 3: Hugh is neither surnamed Lemon nor Fleet (Hugh=2, Lemon=1, Fleet=3)
model += surnames[2] != 1
model += surnames[2] != 3

# Constraint 4: Debra is allergic to ragweed (Debra=0, ragweed=3)
model += allergies[0] == 3

# Constraint 5: Janet (who isn't Lemon) is neither allergic to eggs nor to mold (Janet=1, Lemon=1, eggs=0, mold=1)
model += surnames[1] != 1
model += allergies[1] != 0
model += allergies[1] != 1

# Solve
model.solve()

# Prepare solution
allergies_val = allergies.value()
surnames_val = surnames.value()

solution = {
    "eggs": int(np.where(allergies_val == 0)[0][0]),
    "mold": int(np.where(allergies_val == 1)[0][0]),
    "nuts": int(np.where(allergies_val == 2)[0][0]),
    "ragweed": int(np.where(allergies_val == 3)[0][0]),
    "baxter": int(np.where(surnames_val == 0)[0][0]),
    "lemon": int(np.where(surnames_val == 1)[0][0]),
    "malone": int(np.where(surnames_val == 2)[0][0]),
    "fleet": int(np.where(surnames_val == 3)[0][0])
}

print(json.dumps(solution))
# End of CPMPy script