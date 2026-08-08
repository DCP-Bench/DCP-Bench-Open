
import cpmpy as cp
import json

# Constants for indexing
friends = ["Debra", "Janet", "Hugh", "Rick"]
allergies = ["eggs", "mold", "nuts", "ragweed"]
surnames = ["baxter", "lemon", "malone", "fleet"]

# Model definition
model = cp.Model()

# Decision variables
# allergy[i] = allergy index for friend i
allergy = cp.intvar(0, 3, shape=4, name="allergy")
# surname[i] = surname index for friend i
surname = cp.intvar(0, 3, shape=4, name="surname")

# Constraints

# All allergies are different
model += cp.AllDifferent(allergy)
# All surnames are different
model += cp.AllDifferent(surname)

# Rick is not allergic to mold
model += allergy[3] != allergies.index("mold")

# Baxter is allergic to eggs
# Find the friend whose surname is Baxter, that friend's allergy is eggs
for i in range(4):
    model += (surname[i] == surnames.index("baxter")).implies(allergy[i] == allergies.index("eggs"))

# Hugh is neither surnamed Lemon nor Fleet
model += surname[2] != surnames.index("lemon")
model += surname[2] != surnames.index("fleet")

# Debra is allergic to ragweed
model += allergy[0] == allergies.index("ragweed")

# Janet (who isn't Lemon) is neither allergic to eggs nor to mold
model += surname[1] != surnames.index("lemon")
model += allergy[1] != allergies.index("eggs")
model += allergy[1] != allergies.index("mold")

# Solve and print
if model.solve():
    # Prepare output lists for allergies and surnames per friend
    allergy_sol = [int(allergy[i].value()) for i in range(4)]
    surname_sol = [int(surname[i].value()) for i in range(4)]
    solution = {
        "eggs": allergy_sol.index(allergies.index("eggs")),
        "mold": allergy_sol.index(allergies.index("mold")),
        "nuts": allergy_sol.index(allergies.index("nuts")),
        "ragweed": allergy_sol.index(allergies.index("ragweed")),
        "baxter": surname_sol.index(surnames.index("baxter")),
        "lemon": surname_sol.index(surnames.index("lemon")),
        "malone": surname_sol.index(surnames.index("malone")),
        "fleet": surname_sol.index(surnames.index("fleet"))
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
