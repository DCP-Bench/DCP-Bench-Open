
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
# allergy[p] = allergy index (0=eggs,1=mold,2=nuts,3=ragweed) of person p (p: 0=Debra,1=Janet,2=Hugh,3=Rick)
allergy = cp.intvar(0, 3, shape=4, name="allergy")

# surname[p] = surname index (0=baxter,1=lemon,2=malone,3=fleet) of person p
surname = cp.intvar(0, 3, shape=4, name="surname")

# Inverse/channeling arrays:
# allergy_owner[a] = person who has allergy a
allergy_owner = cp.intvar(0, 3, shape=4, name="allergy_owner")
# surname_owner[s] = person who has surname s
surname_owner = cp.intvar(0, 3, shape=4, name="surname_owner")

# Constraints
# AllDifferent for assignments
model += cp.AllDifferent(allergy)
model += cp.AllDifferent(surname)
model += cp.AllDifferent(allergy_owner)
model += cp.AllDifferent(surname_owner)

# Channeling: allergy[p] = a  <=>  allergy_owner[a] = p
model += cp.Inverse(allergy, allergy_owner)

# Channeling: surname[p] = s  <=>  surname_owner[s] = p
model += cp.Inverse(surname, surname_owner)

# Clues:
# - Rick (3) is not allergic to mold (1)
model += allergy[3] != 1

# - Baxter (surname 0) is allergic to eggs (allergy 0)
#   i.e., the person who is Baxter is the same person who has eggs
model += allergy_owner[0] == surname_owner[0]

# - Hugh (2) is neither surnamed Lemon (1) nor Fleet (3)
model += surname[2] != 1
model += surname[2] != 3

# - Debra (0) is allergic to ragweed (3)
model += allergy[0] == 3

# - Janet (1), who isn't Lemon, is neither allergic to eggs (0) nor to mold (1)
model += surname[1] != 1
model += allergy[1] != 0
model += allergy[1] != 1

# Solve and print
if model.solve():
    solution = {
        # allergies: map allergy -> person index
        'eggs': int(allergy_owner[0].value()),
        'mold': int(allergy_owner[1].value()),
        'nuts': int(allergy_owner[2].value()),
        'ragweed': int(allergy_owner[3].value()),
        # surnames: map surname -> person index
        'baxter': int(surname_owner[0].value()),
        'lemon': int(surname_owner[1].value()),
        'malone': int(surname_owner[2].value()),
        'fleet': int(surname_owner[3].value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
