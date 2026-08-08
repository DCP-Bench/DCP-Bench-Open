
import cpmpy as cp
import json

# Suspects
suspects = ["artie", "bill", "crackitt", "dodgy", "edgy", "fingers"]

# Model definition
model = cp.Model()

# Decision Variables: 1 if guilty, 0 if innocent
guilty = cp.intvar(0, 1, shape=6, name="guilty")

# At least four are innocent => at most two are guilty
model += cp.sum(guilty) <= 2

# Innocent tell the truth, guilty lie
# We encode the statements as boolean expressions and link them to truthfulness

# Helper to get index
def idx(name):
    return suspects.index(name)

# ARTIE: "It wasn't me." => Artie says he is innocent
# If Artie is innocent (guilty=0), statement is true => Artie is not guilty
# If Artie is guilty (guilty=1), statement is false => Artie is guilty
# So statement: (guilty[artie] == 0)
# Truthfulness: (guilty[artie] == 0) == (statement is true)
model += (guilty[idx("artie")] == 0) == (guilty[idx("artie")] == 0)

# BILL: "Crackitt was in it up to his neck."
# Bill says Crackitt is guilty
# If Bill innocent (guilty=0), statement true => Crackitt guilty=1
# If Bill guilty (guilty=1), statement false => Crackitt guilty=0
model += (guilty[idx("bill")] == 0) == (guilty[idx("crackitt")] == 1)

# CRACKITT: "No I wasn't." (i.e. Crackitt says he is not guilty)
# If Crackitt innocent (guilty=0), statement true => Crackitt guilty=0
# If Crackitt guilty (guilty=1), statement false => Crackitt guilty=1
model += (guilty[idx("crackitt")] == 0) == (guilty[idx("crackitt")] == 0)

# DODGY: "If Crackitt did it, Bill did it with him."
# If Crackitt guilty=1 => Bill guilty=1
# So statement: (Crackitt guilty => Bill guilty)
# If Dodgy innocent (guilty=0), statement true => implication holds
# If Dodgy guilty (guilty=1), statement false => implication does not hold
implication = (guilty[idx("crackitt")] <= guilty[idx("bill")])  # Crackitt guilty implies Bill guilty
model += (guilty[idx("dodgy")] == 0) == implication

# EDGY: "Nobody did it alone."
# Nobody did it alone means no single guilty person
# So if guilty count > 0, then guilty count != 1
# Statement: guilty count != 1
# If Edgy innocent (guilty=0), statement true => guilty count != 1
# If Edgy guilty (guilty=1), statement false => guilty count == 1
guilty_count = cp.sum(guilty)
model += (guilty[idx("edgy")] == 0) == (guilty_count != 1)

# FINGERS: "That’s right: it was Artie and Dodgy together."
# Fingers confirms Edgy's statement specifying Artie and Dodgy are the guilty ones
# Statement: Artie guilty=1 and Dodgy guilty=1 and no others guilty
# So statement: (guilty[artie] == 1) & (guilty[dodgy] == 1) & (guilty_count == 2)
# If Fingers innocent (guilty=0), statement true => above holds
# If Fingers guilty (guilty=1), statement false => above does not hold
fingers_statement = (guilty[idx("artie")] == 1) & (guilty[idx("dodgy")] == 1) & (guilty_count == 2)
model += (guilty[idx("fingers")] == 0) == fingers_statement

# Solve and print
if model.solve():
    solution = {suspect: int(guilty[i].value()) for i, suspect in enumerate(suspects)}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
