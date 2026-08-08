
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables
statements = cp.boolvar(shape=5, name="statements")  # 0/1 truth values for the 5 statements
nfalse = cp.intvar(0, 5, name="nfalse")  # number of false statements

# Constraints
# Count of false statements
model += (nfalse == cp.sum([1 - statements[i] for i in range(5)]))

# Each statement i claims: "Exactly (i+1) statements are false"
for i in range(5):
    model += (statements[i] == (nfalse == (i+1)))

# Solve and print
if model.solve():
    solution = {'statements': list(map(int, statements.value().tolist()))}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
