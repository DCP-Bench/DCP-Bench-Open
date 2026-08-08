
from ortools.sat.python import cp_model
import json

# Create the model
model = cp_model.CpModel()

# Decision variables: 1 if guilty, 0 if innocent
artie    = model.NewBoolVar('artie')
bill     = model.NewBoolVar('bill')
crackitt = model.NewBoolVar('crackitt')
dodgy    = model.NewBoolVar('dodgy')
edgy     = model.NewBoolVar('edgy')
fingers  = model.NewBoolVar('fingers')

# Auxiliary boolean variables for each statement's truth value
stmt_artie    = model.NewBoolVar('stmt_artie')
stmt_bill     = model.NewBoolVar('stmt_bill')
stmt_crackitt = model.NewBoolVar('stmt_crackitt')
stmt_dodgy    = model.NewBoolVar('stmt_dodgy')
stmt_edgy     = model.NewBoolVar('stmt_edgy')
stmt_fingers  = model.NewBoolVar('stmt_fingers')

# Total number of guilty suspects
total_guilty = model.NewIntVar(0, 6, 'total_guilty')
model.Add(total_guilty == artie + bill + crackitt + dodgy + edgy + fingers)

# 1) Artie: "It wasn't me."  <=> stmt_artie = (not artie)
model.Add(stmt_artie + artie == 1)

# 2) Bill: "Crackitt was in it up to his neck."  <=> stmt_bill = crackitt
model.Add(stmt_bill - crackitt == 0)

# 3) Crackitt: "No I wasn't."  <=> stmt_crackitt = (not crackitt)
model.Add(stmt_crackitt + crackitt == 1)

# 4) Dodgy: "If Crackitt did it, Bill did it with him."
#    stmt_dodgy = (not crackitt) OR bill
model.Add(stmt_dodgy >= (1 - crackitt))
model.Add(stmt_dodgy >= bill)
model.Add(stmt_dodgy <= (1 - crackitt) + bill)

# 5) Edgy: "Nobody did it alone."  <=> stmt_edgy = (total_guilty >= 2)
model.Add(total_guilty >= 2).OnlyEnforceIf(stmt_edgy)
model.Add(total_guilty < 2).OnlyEnforceIf(stmt_edgy.Not())

# 6) Fingers: "It was Artie and Dodgy together."
#    stmt_fingers = (artie and dodgy and not bill and not crackitt and not edgy and not fingers)
model.AddBoolAnd([
    artie, dodgy,
    bill.Not(), crackitt.Not(), edgy.Not(), fingers.Not()
]).OnlyEnforceIf(stmt_fingers)
model.AddBoolOr([
    artie.Not(), dodgy.Not(),
    bill, crackitt, edgy, fingers
]).OnlyEnforceIf(stmt_fingers.Not())

# Truth-telling: innocent => statement true; guilty => statement false
for person, stmt in [
    (artie, stmt_artie),
    (bill, stmt_bill),
    (crackitt, stmt_crackitt),
    (dodgy, stmt_dodgy),
    (edgy, stmt_edgy),
    (fingers, stmt_fingers),
]:
    # If innocent (person=0) then stmt must be true
    model.Add(stmt == 1).OnlyEnforceIf(person.Not())
    # If guilty (person=1) then stmt must be false
    model.Add(stmt == 0).OnlyEnforceIf(person)

# Exactly two guilty
model.Add(artie + bill + crackitt + dodgy + edgy + fingers == 2)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'artie': solver.Value(artie),
        'bill': solver.Value(bill),
        'crackitt': solver.Value(crackitt),
        'dodgy': solver.Value(dodgy),
        'edgy': solver.Value(edgy),
        'fingers': solver.Value(fingers)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
