from ortools.sat.python import cp_model
import json

# Model definition
model = cp_model.CpModel()

# Decision variables: 1 if guilty, 0 if innocent
artie = model.NewBoolVar('artie')
bill = model.NewBoolVar('bill')
crackitt = model.NewBoolVar('crackitt')
dodgy = model.NewBoolVar('dodgy')
edgy = model.NewBoolVar('edgy')
fingers = model.NewBoolVar('fingers')

suspects = [artie, bill, crackitt, dodgy, edgy, fingers]

# At least four are innocent => at most two are guilty
model.Add(sum(suspects) <= 2)

# The innocent tell the truth, the guilty lie
# We encode each statement as a boolean expression and enforce that
# if a suspect is innocent (0), their statement is true (1)
# if a suspect is guilty (1), their statement is false (0)
# So: innocent => statement true, guilty => statement false
# This can be encoded as: statement == (1 - guilty)

# Statements:
# ARTIE: "It wasn't me." => artie == 0
artie_statement = model.NewBoolVar('artie_statement')
model.Add(artie == 0).OnlyEnforceIf(artie_statement)
model.Add(artie != 0).OnlyEnforceIf(artie_statement.Not())

# BILL: "Crackitt was in it up to his neck." => crackitt == 1
bill_statement = model.NewBoolVar('bill_statement')
model.Add(crackitt == 1).OnlyEnforceIf(bill_statement)
model.Add(crackitt != 1).OnlyEnforceIf(bill_statement.Not())

# CRACKITT: "No I wasn't." => crackitt == 0
crackitt_statement = model.NewBoolVar('crackitt_statement')
model.Add(crackitt == 0).OnlyEnforceIf(crackitt_statement)
model.Add(crackitt != 0).OnlyEnforceIf(crackitt_statement.Not())

# DODGY: "If Crackitt did it, Bill did it with him."
# Logical: crackitt == 1 => bill == 1
# Equivalent to: not crackitt or bill
dodgy_statement = model.NewBoolVar('dodgy_statement')
model.AddBoolOr([crackitt.Not(), bill]).OnlyEnforceIf(dodgy_statement)
model.AddBoolAnd([crackitt, bill.Not()]).OnlyEnforceIf(dodgy_statement.Not())

# EDGY: "Nobody did it alone."
# Meaning: no one is guilty alone, so if someone is guilty, at least one other is guilty
# So for each guilty suspect, sum of guilty suspects >= 2
# Equivalently: if sum(suspects) >= 1 then sum(suspects) >= 2
# So sum(suspects) != 1
# Edgy's statement is true if sum(suspects) != 1
edgy_statement = model.NewBoolVar('edgy_statement')
# sum(suspects) == 1 => edgy_statement == False
# sum(suspects) != 1 => edgy_statement == True
model.Add(sum(suspects) == 1).OnlyEnforceIf(edgy_statement.Not())
model.Add(sum(suspects) != 1).OnlyEnforceIf(edgy_statement)

# FINGERS: "That’s right: it was Artie and Dodgy together."
# Meaning: artie == 1 and dodgy == 1
fingers_statement = model.NewBoolVar('fingers_statement')
model.AddBoolAnd([artie, dodgy]).OnlyEnforceIf(fingers_statement)
model.AddBoolOr([artie.Not(), dodgy.Not()]).OnlyEnforceIf(fingers_statement.Not())

# Now link statements truth to innocence/guilt
# statement == (1 - guilty)
model.Add(artie_statement == (1 - artie))
model.Add(bill_statement == (1 - bill))
model.Add(crackitt_statement == (1 - crackitt))
model.Add(dodgy_statement == (1 - dodgy))
model.Add(edgy_statement == (1 - edgy))
model.Add(fingers_statement == (1 - fingers))

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