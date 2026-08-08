
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables (1 = guilty, 0 = innocent)
artie = cp.boolvar(name="artie")
bill = cp.boolvar(name="bill")
crackitt = cp.boolvar(name="crackitt")
dodgy = cp.boolvar(name="dodgy")
edgy = cp.boolvar(name="edgy")
fingers = cp.boolvar(name="fingers")

guilty = [artie, bill, crackitt, dodgy, edgy, fingers]
total = cp.sum(guilty)

# Constraints
# At least one guilty and at most two (car fits two, crime happened)
model += (total >= 1)
model += (total <= 2)

# Truth/lie constraints:
# Innocent tells truth, guilty lies: (~suspect) == statement_truth

# ARTIE: "It wasn't me."  -> statement: ~artie
# This is tautological with the truth/lie rule, no need to add.

# BILL: "Crackitt was in it up to his neck." -> statement: crackitt
model += ((~bill) == crackitt)

# CRACKITT: "No I wasn't." -> statement: ~crackitt
# Also tautological, no need to add.

# DODGY: "If Crackitt did it, Bill did it with him." -> statement: (~crackitt) | bill
model += ((~dodgy) == ((~crackitt) | bill))

# EDGY: "Nobody did it alone." -> statement: total != 1
model += ((~edgy) == (total != 1))

# FINGERS: "That's right: it was Artie and Dodgy together."
# Encode as: artie and dodgy are guilty and exactly two guilty overall
model += ((~fingers) == (artie & dodgy & (total == 2)))

# Solve and print
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
