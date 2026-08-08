
import cpmpy as cp
import json

# We have 4 shoes and 4 stores, and 4 purchase order positions (1 to 4)
# Shoes: ecruespadrilles, fuchsiaflats, purplepumps, suedesandals
# Stores: footfarm, heelsinahandcart, theshoepalace, tootsies

# Model definition
model = cp.Model()

# Decision variables: position of each shoe and store in the purchase order (1 to 4)
ecruespadrilles = cp.intvar(1,4, name="ecruespadrilles")
fuchsiaflats = cp.intvar(1,4, name="fuchsiaflats")
purplepumps = cp.intvar(1,4, name="purplepumps")
suedesandals = cp.intvar(1,4, name="suedesandals")

footfarm = cp.intvar(1,4, name="footfarm")
heelsinahandcart = cp.intvar(1,4, name="heelsinahandcart")
theshoepalace = cp.intvar(1,4, name="theshoepalace")
tootsies = cp.intvar(1,4, name="tootsies")

# All shoes must be bought at different positions
model += cp.AllDifferent([ecruespadrilles, fuchsiaflats, purplepumps, suedesandals])

# All stores must be visited at different positions
model += cp.AllDifferent([footfarm, heelsinahandcart, theshoepalace, tootsies])

# Constraint 1: Harriet bought fuchsia flats at Heels in a Handcart.
model += (fuchsiaflats == heelsinahandcart)

# Constraint 2: The store she visited just after buying her purple pumps was not Tootsies.
# So the position of the store visited after purple pumps is not tootsies
# That means: if purplepumps = p, then the store at position p+1 != tootsies
# We can express this as: tootsies != purplepumps + 1
model += (tootsies != purplepumps + 1)

# Constraint 3: The Foot Farm was Harriet's second stop.
model += (footfarm == 2)

# Constraint 4: Two stops after leaving The Shoe Place, Harriet bought her suede sandals.
# If theshoepalace = s, then suedesandals = s + 2
model += (suedesandals == theshoepalace + 2)

# Solve and print
if model.solve():
    solution = {
        'ecruespadrilles': int(ecruespadrilles.value()),
        'fuchsiaflats': int(fuchsiaflats.value()),
        'purplepumps': int(purplepumps.value()),
        'suedesandals': int(suedesandals.value()),
        'footfarm': int(footfarm.value()),
        'heelsinahandcart': int(heelsinahandcart.value()),
        'theshoepalace': int(theshoepalace.value()),
        'tootsies': int(tootsies.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
