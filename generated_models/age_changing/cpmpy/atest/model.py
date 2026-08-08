from cpmpy import *
import json

# Decision variables
m = intvar(0, 100, name="m")  # My age
h = intvar(0, 100, name="h")  # Husband's age

# Define the four operations as expressions
def op1(x): return x + 2
def op2(x): return x // 8
def op3(x): return x - 3
def op4(x): return x * 7

# List of all possible operation functions
ops = [op1, op2, op3, op4]

# Model
model = Model()

# Try all possible pairs of permutations (p1 for m -> h, p2 for h -> m)
from itertools import permutations

for p1 in permutations(range(4)):
    for p2 in permutations(range(4)):
        if p1 != p2:
            # Apply p1 to m and check if it equals h
            temp_m = m
            for op_idx in p1:
                temp_m = ops[op_idx](temp_m)
            # Apply p2 to h and check if it equals m
            temp_h = h
            for op_idx in p2:
                temp_h = ops[op_idx](temp_h)
            # Add constraints for this specific pair of permutations
            model += [temp_m == h, temp_h == m]

# Solve the model
model.solve()

# Print the solution
solution = {"m": m.value(), "h": h.value()}
print(json.dumps(solution))