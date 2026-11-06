#!/usr/bin/python3
# Category: aplai_course
# Source: http://www.hakank.org/minizinc/thick_as_thieves.mzn

# Import libraries
from cpmpy import *
import json

# Decision Variables for each suspect representing if they are guilty
artie = boolvar(name="Artie")
bill = boolvar(name="Bill")
crackitt = boolvar(name="Crackitt")
dodgy = boolvar(name="Dodgy")
edgy = boolvar(name="Edgy")
fingers = boolvar(name="Fingers")
suspects = [artie, bill, crackitt, dodgy, edgy, fingers]

# Constraints
model = Model()

# At most two are guilty because the getaway car was small
model += sum(suspects) <= 2

# Statement Constraints; if the suspect is guilty, they are lying, so their statement is false

# Artie: "It wasn't me."
artie_statement = ~artie
model += artie == ~artie_statement

# Bill: "Crackitt was in it up to his neck."
bill_statement = crackitt
model += bill == ~bill_statement

# Crackitt: "No I wasn't."
crackitt_statement = ~crackitt
model += crackitt == ~crackitt_statement

# Dodgy: "If Crackitt did it, Bill did it with him."
dodgy_statement = crackitt.implies(bill)
model += dodgy == ~dodgy_statement

# Edgy: "Nobody did it alone."
edgy_statement = sum(suspects) > 1
model += edgy == ~edgy_statement

# Fingers: "That’s right: it was Artie and Dodgy together."
fingers_statement = artie & dodgy
model += fingers == ~fingers_statement

# Solve
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
# End of CPMPy script
