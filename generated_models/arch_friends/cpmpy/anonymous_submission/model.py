from cpmpy import *
import json
import numpy as np

# Decision Variables
# Shoes: ecruespadrilles=0, fuchsiaflats=1, purplepumps=2, suedesandals=3
# Stores: footfarm=0, heelsinahandcart=1, theshoepalace=2, tootsies=3

shoes = intvar(0, 3, shape=4, name="shoes")  # shoes[order] = shoe
stores = intvar(0, 3, shape=4, name="stores")  # stores[order] = store

# Model
model = Model()

# All variables must be distinct
model += AllDifferent(shoes)
model += AllDifferent(stores)

# Constraint 1: Harriet bought fuchsia flats at Heels in a Handcart
for i in range(4):
    model += (shoes[i] == 1) == (stores[i] == 1)

# Constraint 2: The store after purple pumps was not Tootsies
for i in range(3):
    model += (shoes[i] == 2).implies(stores[i+1] != 3)

# Constraint 3: Foot Farm was second stop (index 1)
model += stores[1] == 0

# Constraint 4: Two stops after The Shoe Place was suede sandals
for i in range(2):
    model += (stores[i] == 2).implies(shoes[i+2] == 3)

# Solve
model.solve()

# Prepare solution (using 1-based indexing for output)
solution = {
    "ecruespadrilles": int(np.where(shoes.value() == 0)[0][0] + 1),
    "fuchsiaflats": int(np.where(shoes.value() == 1)[0][0] + 1),
    "purplepumps": int(np.where(shoes.value() == 2)[0][0] + 1),
    "suedesandals": int(np.where(shoes.value() == 3)[0][0] + 1),
    "footfarm": int(np.where(stores.value() == 0)[0][0] + 1),
    "heelsinahandcart": int(np.where(stores.value() == 1)[0][0] + 1),
    "theshoepalace": int(np.where(stores.value() == 2)[0][0] + 1),
    "tootsies": int(np.where(stores.value() == 3)[0][0] + 1)
}

print(json.dumps(solution))