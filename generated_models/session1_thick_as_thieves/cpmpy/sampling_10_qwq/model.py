
import cpmpy as cp
import json

# Variables for each suspect's guilt status (0: innocent, 1: guilty)
artie = cp.boolvar(name="artie")
bill = cp.boolvar(name="bill")
crackitt = cp.boolvar(name="crackitt")
dodgy = cp.boolvar(name="dodgy")
edgy = cp.boolvar(name="edgy")
fingers = cp.boolvar(name="fingers")

# Total guilty count
guilty_count = artie + bill + crackitt + dodgy + edgy + fingers

# Model initialization
model = cp.Model()

# Constraints on guilty count: must be between 1 and 2 (inclusive)
model += guilty_count >= 1
model += guilty_count <= 2

# Bill's statement: Crackitt is guilty iff Bill is innocent
model += crackitt == (1 - bill)

# Dodgy's statement: If Crackitt is guilty, Bill must be guilty. This is enforced via implication and Dodgy's guilt
model += (crackitt.implies(bill) == (1 - dodgy))

# Edgy's statement: Guilty count >=2 iff Edgy is innocent
model += ( (edgy == 0) == (guilty_count >= 2) )

# Fingers' statement: Artie and Dodgy are both guilty iff Fingers is innocent
model += ( artie * dodgy == (1 - fingers) )

# Solve and output
if model.solve():
    solution = {
        'artie': int(artie.value()),
        'bill': int(bill.value()),
        'crackitt': int(crackitt.value()),
        'dodgy': int(dodgy.value()),
        'edgy': int(edgy.value()),
        'fingers': int(fingers.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
