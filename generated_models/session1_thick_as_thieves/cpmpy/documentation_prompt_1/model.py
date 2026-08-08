
import cpmpy as cp
import json

# Suspects
suspects = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]
n = len(suspects)

# Model definition
model = cp.Model()

# Decision Variables: 1 if guilty, 0 if innocent
guilty = cp.intvar(0, 1, shape=n, name="guilty")

# At least four are innocent => at most two are guilty
model += cp.sum(guilty) <= 2

# Innocent tell the truth, guilty lie
# We encode the statements as boolean expressions and link them to truthfulness

# Helper to get index of suspect
idx = {name: i for i, name in enumerate(suspects)}

# Statements:
# ARTIE: "It wasn't me." => Artie says he is innocent
artie_stmt = (guilty[idx["artie"]] == 0)

# BILL: "Crackitt was in it up to his neck." => Bill says Crackitt is guilty
bill_stmt = (guilty[idx["crackitt"]] == 1)

# CRACKITT: "No I wasn't." => Crackitt says he is innocent
crackitt_stmt = (guilty[idx["crackitt"]] == 0)

# DODGY: "If Crackitt did it, Bill did it with him."
# If Crackitt guilty => Bill guilty
dodgy_stmt = (guilty[idx["crackitt"]] <= guilty[idx["bill"]])  # implication: Crackitt => Bill

# EDGY: "Nobody did it alone."
# No one is the only guilty person
# For each guilty person, there is at least one other guilty person
# So if guilty[i] == 1, sum of guilty >= 2
# This means: if sum(guilty) == 1 then edgy is lying, else telling truth
# But edgy statement is about the group, so edgy's statement is true if sum(guilty) != 1
edgy_stmt = (cp.sum(guilty) != 1)

# FINGERS: "That’s right: it was Artie and Dodgy together."
# Fingers confirms Edgy's statement, specifying the guilty are Artie and Dodgy together
# So Fingers says: guilty == Artie and Dodgy only
fingers_stmt = (cp.sum(guilty) == 2) & (guilty[idx["artie"]] == 1) & (guilty[idx["dodgy"]] == 1)

# Link truthfulness: innocent tell truth, guilty lie
# For each suspect i:
# if guilty[i] == 0 then statement[i] == True
# if guilty[i] == 1 then statement[i] == False
# This can be encoded as: statement[i] == (1 - guilty[i])

model += (artie_stmt == (1 - guilty[idx["artie"]]))
model += (bill_stmt == (1 - guilty[idx["bill"]]))
model += (crackitt_stmt == (1 - guilty[idx["crackitt"]]))
model += (dodgy_stmt == (1 - guilty[idx["dodgy"]]))
model += (edgy_stmt == (1 - guilty[idx["edgy"]]))
model += (fingers_stmt == (1 - guilty[idx["fingers"]]))

# Solve and print
if model.solve():
    solution = {suspects[i]: int(guilty[i].value()) for i in range(n)}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
