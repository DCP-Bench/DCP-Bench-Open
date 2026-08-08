
import cpmpy as cp
import json
import itertools

# The four operations and their effects:
# +2, /8, -3, *7

# Variables: m = my age, h = husband's age
# Both ages are positive integers, reasonable range (e.g. 1 to 120)
m = cp.intvar(1, 120, name="m")
h = cp.intvar(1, 120, name="h")

# Since division by 8 must yield integer results, intermediate computations must be integers.

# We have two sequences of applying operations to get each other:

# Operations with their function forms:
# op1: +2 (x + 2)
# op2: /8 (x // 8, integer division)
# op3: -3 (x - 3)
# op4: *7 (x * 7)

# We want to find permutations p1 and p2 of these operations:
# Applying p1 to m yields h
# Applying p2 (different order) to h yields m

ops = [
    ("+2", lambda x: x + 2),
    ("/8", lambda x: x // 8),
    ("-3", lambda x: x - 3),
    ("*7", lambda x: x * 7),
]

# We must model the sequences and intermediate variables to ensure integer constraints

model = cp.Model()

# To handle order of operations, create intermediate variables for each operation in the sequence
# For p1: starting from m, apply 4 ops in order to get h
# For p2: starting from h, apply 4 ops in order to get m

# We'll try all permutations for p1 and p2 and add constraints for one pair at a time
# because we cannot directly represent the variable order of application with cpmpy variables easily.

# So we will do a search over pairs of permutations and try to solve the system for m,h.

found_solution = False
result = {}

for p1 in itertools.permutations(ops):
    for p2 in itertools.permutations(ops):
        if p1 == p2:
            continue

        model = cp.Model()

        # Variables for m and h
        m = cp.intvar(1, 120, name="m")
        h = cp.intvar(1, 120, name="h")

        # Intermediate variables for p1 (4 intermediate steps + final)
        p1_vars = [m] + [cp.intvar(-1000, 10000) for _ in range(4)]
        # Intermediate variables for p2 (4 intermediate steps + final)
        p2_vars = [h] + [cp.intvar(-1000, 10000) for _ in range(4)]

        # Apply operations in order p1: p1_vars[i+1] = apply p1[i] on p1_vars[i]
        for i, (name, op) in enumerate(p1):
            if name == "+2":
                model += (p1_vars[i+1] == p1_vars[i] + 2)
            elif name == "/8":
                # division must be exact integer division
                model += (p1_vars[i] % 8 == 0)
                model += (p1_vars[i+1] == p1_vars[i] // 8)
            elif name == "-3":
                model += (p1_vars[i+1] == p1_vars[i] - 3)
            elif name == "*7":
                model += (p1_vars[i+1] == p1_vars[i] * 7)

        # Final result of p1 is h
        model += (p1_vars[4] == h)

        # Apply operations in order p2: p2_vars[i+1] = apply p2[i] on p2_vars[i]
        for i, (name, op) in enumerate(p2):
            if name == "+2":
                model += (p2_vars[i+1] == p2_vars[i] + 2)
            elif name == "/8":
                model += (p2_vars[i] % 8 == 0)
                model += (p2_vars[i+1] == p2_vars[i] // 8)
            elif name == "-3":
                model += (p2_vars[i+1] == p2_vars[i] - 3)
            elif name == "*7":
                model += (p2_vars[i+1] == p2_vars[i] * 7)

        # Final result of p2 is m
        model += (p2_vars[4] == m)

        # Both ages positive
        model += (m >= 1)
        model += (h >= 1)

        # Solve model
        if model.solve():
            # Collect solution
            result = {
                'm': int(m.value()),
                'h': int(h.value()),
            }
            found_solution = True
            break
    if found_solution:
        break

if found_solution:
    print(json.dumps(result, indent=4))
else:
    print("No solution found.")
