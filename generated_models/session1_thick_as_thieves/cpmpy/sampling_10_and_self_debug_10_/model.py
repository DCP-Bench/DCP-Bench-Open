
import cpmpy as cp
import json

# Decision variables: True = guilty, False = innocent
artie   = cp.boolvar(name="artie")
bill    = cp.boolvar(name="bill")
crackitt= cp.boolvar(name="crackitt")
dodgy   = cp.boolvar(name="dodgy")
edgy    = cp.boolvar(name="edgy")
fingers = cp.boolvar(name="fingers")

model = cp.Model()

# Constraint: at most two guilty (car barely big enough for two),
# and at least one guilty (there was a robbery)
guilty_list = [artie, bill, crackitt, dodgy, edgy, fingers]
model += cp.sum(guilty_list) <= 2
model += cp.sum(guilty_list) >= 1

# Statements mapped to boolean expressions (their content)
# Artie: "It wasn't me."  -> (~artie)
stmt_artie = ~artie
# Bill: "Crackitt was in it up to his neck." -> crackitt
stmt_bill = crackitt
# Crackitt: "No I wasn't." -> (~crackitt)
stmt_crackitt = ~crackitt
# Dodgy: "If Crackitt did it, Bill did it with him." -> (not crackitt) or bill
stmt_dodgy = (~crackitt) | bill
# Edgy: "Nobody did it alone." -> number of guilty != 1
stmt_edgy = (cp.sum(guilty_list) != 1)
# Fingers: "That’s right: it was Artie and Dodgy together." -> exactly Artie and Dodgy guilty
stmt_fingers = artie & dodgy & (~bill) & (~crackitt) & (~edgy) & (~fingers)

# Innocent tell the truth, guilty lie:
# So statement_content == (not guilty)
model += (stmt_artie    == (~artie))
model += (stmt_bill     == (~bill))
model += (stmt_crackitt == (~crackitt))
model += (stmt_dodgy    == (~dodgy))
model += (stmt_edgy     == (~edgy))
model += (stmt_fingers  == (~fingers))

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
