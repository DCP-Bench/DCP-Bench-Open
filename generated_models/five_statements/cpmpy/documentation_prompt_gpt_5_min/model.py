
import cpmpy as cp
import json

# Model definition
model = cp.Model()

# Decision Variables: one boolean per statement (True=1 means the statement is true)
statements = cp.boolvar(shape=5, name="statements")

# Number of false statements
num_false = cp.sum([1 - statements[i] for i in range(5)])

# Constraints: statement i asserts that exactly (i+1) statements are false
for i in range(5):
    model += (statements[i] == (num_false == (i + 1)))

# Solve and print
if model.solve():
    # convert booleans to 0/1 integers
    solution = {'statements': list(map(int, statements.value().tolist()))}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
