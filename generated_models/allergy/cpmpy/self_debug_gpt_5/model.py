
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: 0/1 integer arrays per person [Debra=0, Janet=1, Hugh=2, Rick=3]
eggs = cp.intvar(0, 1, shape=4, name="eggs")
mold = cp.intvar(0, 1, shape=4, name="mold")
nuts = cp.intvar(0, 1, shape=4, name="nuts")
ragweed = cp.intvar(0, 1, shape=4, name="ragweed")

baxter = cp.intvar(0, 1, shape=4, name="baxter")
lemon = cp.intvar(0, 1, shape=4, name="lemon")
malone = cp.intvar(0, 1, shape=4, name="malone")
fleet = cp.intvar(0, 1, shape=4, name="fleet")

# Constraints

# Each person has exactly one allergy
for i in range(4):
    model += (eggs[i] + mold[i] + nuts[i] + ragweed[i] == 1)

# Each allergy is assigned to exactly one person
model += (cp.sum(eggs) == 1)
model += (cp.sum(mold) == 1)
model += (cp.sum(nuts) == 1)
model += (cp.sum(ragweed) == 1)

# Each person has exactly one surname
for i in range(4):
    model += (baxter[i] + lemon[i] + malone[i] + fleet[i] == 1)

# Each surname is assigned to exactly one person
model += (cp.sum(baxter) == 1)
model += (cp.sum(lemon) == 1)
model += (cp.sum(malone) == 1)
model += (cp.sum(fleet) == 1)

# Clues:
# Rick is not allergic to mold (Rick=3)
model += (mold[3] == 0)

# Baxter is allergic to eggs (same person)
for i in range(4):
    model += (baxter[i] == eggs[i])

# Hugh (2) is neither Lemon nor Fleet
model += (lemon[2] == 0)
model += (fleet[2] == 0)

# Debra (0) is allergic to ragweed
model += (ragweed[0] == 1)

# Janet (1) isn't Lemon and is neither allergic to eggs nor mold
model += (lemon[1] == 0)
model += (eggs[1] == 0)
model += (mold[1] == 0)

# Solve and print
if model.solve():
    solution = {
        'eggs': [int(v) for v in eggs.value().tolist()],
        'mold': [int(v) for v in mold.value().tolist()],
        'nuts': [int(v) for v in nuts.value().tolist()],
        'ragweed': [int(v) for v in ragweed.value().tolist()],
        'baxter': [int(v) for v in baxter.value().tolist()],
        'lemon': [int(v) for v in lemon.value().tolist()],
        'malone': [int(v) for v in malone.value().tolist()],
        'fleet': [int(v) for v in fleet.value().tolist()]
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
