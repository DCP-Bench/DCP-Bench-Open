
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables (positions 1..4)
ecruespadrilles = cp.intvar(1, 4, name="ecruespadrilles")
fuchsiaflats = cp.intvar(1, 4, name="fuchsiaflats")
purplepumps = cp.intvar(1, 4, name="purplepumps")
suedesandals = cp.intvar(1, 4, name="suedesandals")

footfarm = cp.intvar(1, 4, name="footfarm")
heelsinahandcart = cp.intvar(1, 4, name="heelsinahandcart")
theshoepalace = cp.intvar(1, 4, name="theshoepalace")
tootsies = cp.intvar(1, 4, name="tootsies")

# Constraints
# Each shoe bought at a different time
model += cp.AllDifferent([ecruespadrilles, fuchsiaflats, purplepumps, suedesandals])
# Each store visited at a different time
model += cp.AllDifferent([footfarm, heelsinahandcart, theshoepalace, tootsies])

# 1. Harriet bought fuchsia flats at Heels in a Handcart.
model += (fuchsiaflats == heelsinahandcart)

# 2. The store she visited just after buying her purple pumps was not Tootsies.
#    Ensure the "just after" exists
model += (purplepumps <= 3)
model += (tootsies != purplepumps + 1)

# 3. The Foot Farm was Harriet's second stop.
model += (footfarm == 2)

# 4. Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
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
