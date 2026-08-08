from cpmpy import *
import json

# Parameters
n_friends = 4  # Number of friends

# Decision variables
# Each friend is represented by an index: Debra = 0, Janet = 1, Hugh = 2, Rick = 3
# Allergies: eggs, mold, nuts, ragweed
allergy = intvar(0, 3, shape=n_friends, name="allergy")
# Surnames: baxter, lemon, malone, fleet
surname = intvar(0, 3, shape=n_friends, name="surname")

# Model
model = Model()

# All allergies and surnames are unique (no duplicates)
model += [AllDifferent(allergy)]
model += [AllDifferent(surname)]

# Rick is not allergic to mold
model += [allergy[3] != 1]

# Baxter is allergic to eggs
model += [surname[0] == 0]
model += [allergy[0] == 3]  # Debra is allergic to ragweed

# Hugh is neither surnamed Lemon nor Fleet
model += [surname[2] != 1]
model += [surname[2] != 3]

# Debra is allergic to ragweed
model += [allergy[0] == 3]

# Janet (who isn't Lemon) is neither allergic to eggs nor to mold
model += [surname[1] != 1]
model += [allergy[1] != 0]
model += [allergy[1] != 1]

# Solve the model
model.solve()

# Prepare solution
solution = {
    "eggs": [i for i in range(n_friends) if allergy[i].value() == 0][0],
    "mold": [i for i in range(n_friends) if allergy[i].value() == 1][0],
    "nuts": [i for i in range(n_friends) if allergy[i].value() == 2][0],
    "ragweed": [i for i in range(n_friends) if allergy[i].value() == 3][0],
    "baxter": [i for i in range(n_friends) if surname[i].value() == 0][0],
    "lemon": [i for i in range(n_friends) if surname[i].value() == 1][0],
    "malone": [i for i in range(n_friends) if surname[i].value() == 2][0],
    "fleet": [i for i in range(n_friends) if surname[i].value() == 3][0],
}

print(json.dumps(solution))