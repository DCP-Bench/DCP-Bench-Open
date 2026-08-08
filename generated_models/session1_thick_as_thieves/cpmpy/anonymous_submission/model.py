# Import libraries
from cpmpy import *
import json

# Decision Variables
artie = boolvar(name="artie")  # True if guilty
bill = boolvar(name="bill")    # True if guilty
crackitt = boolvar(name="crackitt")  # True if guilty
dodgy = boolvar(name="dodgy")  # True if guilty
edgy = boolvar(name="edgy")    # True if guilty
fingers = boolvar(name="fingers")  # True if guilty

# Model
model = Model()

# Constraint: at most 2 guilty (since car holds 2)
model += (artie + bill + crackitt + dodgy + edgy + fingers) <= 2

# Constraint: at least 1 guilty (since it's a robbery)
model += (artie + bill + crackitt + dodgy + edgy + fingers) >= 1

# Constraint: innocent tell truth, guilty lie
# Artie's statement: "It wasn't me."
model += (~artie).implies(~artie)  # If innocent, tells truth (not guilty)
model += artie.implies(artie)      # If guilty, lies (so would say "It wasn't me" which is false)

# Bill's statement: "Crackitt was in it up to his neck."
model += (~bill).implies(crackitt)  # If innocent, tells truth
model += bill.implies(~crackitt)    # If guilty, lies

# Crackitt's statement: "No I wasn't."
model += (~crackitt).implies(~crackitt)  # If innocent, tells truth
model += crackitt.implies(crackitt)      # If guilty, lies

# Dodgy's statement: "If Crackitt did it, Bill did it with him."
# This is equivalent to: (not crackitt) or bill
model += (~dodgy).implies((~crackitt) | bill)  # If innocent, tells truth
model += dodgy.implies((crackitt) & (~bill))   # If guilty, lies (negation of implication)

# Edgy's statement: "Nobody did it alone."
# This means either 0 or >=2 guilty
model += (~edgy).implies((artie + bill + crackitt + dodgy + edgy + fingers) != 1)
model += edgy.implies((artie + bill + crackitt + dodgy + edgy + fingers) == 1)  # If guilty, lies

# Fingers's statement: "That's right: it was Artie and Dodgy together."
model += (~fingers).implies(artie & dodgy)  # If innocent, tells truth
model += fingers.implies(~(artie & dodgy))  # If guilty, lies

# Solve
model.solve()

# Print solution
solution = {
    "artie": int(artie.value()),
    "bill": int(bill.value()),
    "crackitt": int(crackitt.value()),
    "dodgy": int(dodgy.value()),
    "edgy": int(edgy.value()),
    "fingers": int(fingers.value())
}
print(json.dumps(solution))
# End of CPMPy script