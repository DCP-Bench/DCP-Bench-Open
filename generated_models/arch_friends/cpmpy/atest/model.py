from cpmpy import *
import json

# Parameters
n = 4  # Number of shoes and stores

# Decision variables
# Each shoe is assigned a position (0 to 3) in the sequence of purchases
ecruespadrilles = intvar(0, n - 1, name="ecruespadrilles")
fuchsiaflats = intvar(0, n - 1, name="fuchsiaflats")
purplepumps = intvar(0, n - 1, name="purplepumps")
suedesandals = intvar(0, n - 1, name="suedesandals")

# Each store is assigned a position (0 to 3) in the sequence of visits
footfarm = intvar(0, n - 1, name="footfarm")
heelsinahandcart = intvar(0, n - 1, name="heelsinahandcart")
theshoepalace = intvar(0, n - 1, name="theshoepalace")
tootsies = intvar(0, n - 1, name="tootsies")

# All shoes and stores must have unique positions
model = Model([
    AllDifferent([ecruespadrilles, fuchsiaflats, purplepumps, suedesandals]),
    AllDifferent([footfarm, heelsinahandcart, theshoepalace, tootsies])
])

# Clue 1: Harriet bought fuchsia flats at Heels in a Handcart.
model += [fuchsiaflats == heelsinahandcart]

# Clue 2: The store she visited just after buying her purple pumps was not Tootsies.
model += [(purplepumps + 1) != tootsies]

# Clue 3: The Foot Farm was Harriet's second stop.
model += [footfarm == 1]

# Clue 4: Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
model += [theshoepalace + 2 == suedesandals]
model += [theshoepalace <= 1]  # Ensure theshoepalace is at most 1 to avoid index out of bounds

# Solve the model
model.solve()

# Output the solution
solution = {
    "ecruespadrilles": ecruespadrilles.value(),
    "purplepumps": purplepumps.value(),
    "theshoepalace": theshoepalace.value(),
    "suedesandals": suedesandals.value(),
    "footfarm": footfarm.value(),
    "fuchsiaflats": fuchsiaflats.value(),
    "tootsies": tootsies.value(),
    "heelsinahandcart": heelsinahandcart.value()
}

print(json.dumps(solution))