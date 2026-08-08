
import cpmpy as cp
import json

# We have 4 friends: Debra=0, Janet=1, Hugh=2, Rick=3
# Allergies: eggs=0, mold=1, nuts=2, ragweed=3
# Surnames: baxter=0, lemon=1, malone=2, fleet=3

n = 4

# Model definition
model = cp.Model()

# Decision variables:
# allergy[i] is the allergy of friend i
allergy = cp.intvar(0, n-1, shape=n, name="allergy")
# surname[i] is the surname of friend i
surname = cp.intvar(0, n-1, shape=n, name="surname")

# Constraints:

# All allergies are different
model += cp.AllDifferent(allergy)
# All surnames are different
model += cp.AllDifferent(surname)

# - Rick is not allergic to mold
model += allergy[3] != 1

# - Baxter is allergic to eggs
# If surname[i] == 0 then allergy[i] == 0
for i in range(n):
    model += (surname[i] == 0).implies(allergy[i] == 0)

# - Hugh is neither surnamed Lemon nor Fleet
model += surname[2] != 1  # Lemon
model += surname[2] != 3  # Fleet

# - Debra is allergic to ragweed
model += allergy[0] == 3

# - Janet (who isn't Lemon) is neither allergic to eggs nor to mold
model += surname[1] != 1
model += allergy[1] != 0
model += allergy[1] != 1

# Solve and print
if model.solve():
    solution = {}
    allergy_names = ['eggs', 'mold', 'nuts', 'ragweed']
    surname_names = ['baxter', 'lemon', 'malone', 'fleet']

    # For each allergy, find friend index
    for a in range(n):
        friend_with_allergy = next(i for i in range(n) if allergy[i].value() == a)
        solution[allergy_names[a]] = int(friend_with_allergy)

    # For each surname, find friend index
    for s in range(n):
        friend_with_surname = next(i for i in range(n) if surname[i].value() == s)
        solution[surname_names[s]] = int(friend_with_surname)

    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
