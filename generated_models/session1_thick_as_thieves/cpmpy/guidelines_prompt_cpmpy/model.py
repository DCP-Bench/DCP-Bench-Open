
import cpmpy as cp
import json

# Decision variables: 1 means guilty, 0 means innocent
artie    = cp.intvar(0, 1, name="artie")
bill     = cp.intvar(0, 1, name="bill")
crackitt = cp.intvar(0, 1, name="crackitt")
dodgy    = cp.intvar(0, 1, name="dodgy")
edgy     = cp.intvar(0, 1, name="edgy")
fingers  = cp.intvar(0, 1, name="fingers")
people = [artie, bill, crackitt, dodgy, edgy, fingers]

model = cp.Model()

# 1) At most two criminals (getaway car barely big enough for two).
model += cp.sum(people) <= 2

# Statement constraints with truth-tellers (0) and liars (1).
# Artie: "It wasn't me."  --> (not artie) == truth-value
#    but that gives no new info, it's always satisfied if we reify it.
# Crackitt: "No I wasn't." --> same as Artie, no extra info.

# Bill: "Crackitt was in it up to his neck."
#   content s2 is (crackitt == 1). If Bill innocent (bill=0), s2 must be true.
#   If Bill guilty (bill=1), s2 must be false.
model += (crackitt == 1) == (1 - bill)

# Dodgy: "If Crackitt did it, Bill did it with him."
#   content s4 is (not crackitt) or bill, i.e. (1 - crackitt + bill >= 1)
model += ((1 - crackitt + bill) >= 1) == (1 - dodgy)

# Edgy: "Nobody did it alone." i.e. number of criminals != 1
model += (cp.sum(people) != 1) == (1 - edgy)

# Fingers: "That's right: it was Artie and Dodgy together."
#   content s6 is (artie==1 and dodgy==1 and bill==0 and crackitt==0 and edgy==0 and fingers==0)
fingers_statement = (artie == 1) & (dodgy == 1) & (bill == 0) & (crackitt == 0) & (edgy == 0) & (fingers == 0)
model += fingers_statement == (1 - fingers)

# Solve and print
if model.solve():
    solution = {
        'artie'   : int(artie.value()),
        'bill'    : int(bill.value()),
        'crackitt': int(crackitt.value()),
        'dodgy'   : int(dodgy.value()),
        'edgy'    : int(edgy.value()),
        'fingers' : int(fingers.value())
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
