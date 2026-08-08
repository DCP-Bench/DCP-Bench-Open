
import cpmpy as cp
import json

# Variables
surname = cp.intvar(0, 3, shape=4, name="surname")  # 0=Baxter,1=Lemon,2=Malone,3=Fleet
allergy = cp.intvar(0, 3, shape=4, name="allergy")  # 0=eggs,1=mold,2=nuts,3=ragweed

model = cp.Model()

# Constraints
model += [cp.AllDifferent(surname), cp.AllDifferent(allergy)]

# Rick (index 3) is not allergic to mold (1)
model += allergy[3] != 1

# Baxter (surname 0) is allergic to eggs (0)
for i in range(4):
    model += (surname[i] == 0).implies(allergy[i] == 0)

# Hugh (index 2) is neither Lemon (1) nor Fleet (3)
model += surname[2] != 1
model += surname[2] != 3

# Debra (index 0) is allergic to ragweed (3)
model += allergy[0] == 3

# Janet (index 1) is not Lemon (1)
model += surname[1] != 1

# Janet (index 1) is neither allergic to eggs (0) nor mold (1)
model += allergy[1] != 0
model += allergy[1] != 1

# Solve and print
if model.solve():
    solution = {
        "food": allergy.value().tolist(),
        "surname": surname.value().tolist()
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
