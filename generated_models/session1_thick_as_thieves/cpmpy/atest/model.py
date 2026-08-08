from cpmpy import *
import json

# Decision variables
artie = boolvar(name="artie")
bill = boolvar(name="bill")
crackitt = boolvar(name="crackitt")
dodgy = boolvar(name="dodgy")
edgy = boolvar(name="edgy")
fingers = boolvar(name="fingers")

# Model
model = Model()

# At least four suspects are innocent (i.e., guilty <= 2)
model += [sum([artie, bill, crackitt, dodgy, edgy, fingers]) <= 2]

# Innocent suspects tell the truth, guilty suspects lie
# ARTIE: "It wasn't me."
model += [(1 - artie) == (artie == 0)]

# BILL: "Crackitt was in it up to his neck."
model += [(1 - bill) == (crackitt == 1)]

# CRACKITT: "No I wasn't."
model += [(1 - crackitt) == (crackitt == 0)]

# DODGY: "If Crackitt did it, Bill did it with him."
model += [(1 - dodgy) == (crackitt.implies(bill))]

# EDGY: "Nobody did it alone."
model += [(1 - edgy) == (sum([artie, bill, crackitt, dodgy, edgy, fingers]) >= 2)]

# FINGERS: "That’s right: it was Artie and Dodgy together."
model += [(1 - fingers) == (artie & dodgy)]

# Solve the model
model.solve()

# Print the solution
solution = {
    "artie": int(artie.value()),
    "bill": int(bill.value()),
    "crackitt": int(crackitt.value()),
    "dodgy": int(dodgy.value()),
    "edgy": int(edgy.value()),
    "fingers": int(fingers.value())
}
print(json.dumps(solution))