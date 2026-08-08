
import cpmpy as cp
import json

# Data
n = 6
problem = [[11, [[1, 1], [2, 1]]], [2, [[1, 2], [1, 3]]],
           [20, [[1, 4], [2, 4]]], [6, [[1, 5], [1, 6], [2, 6], [3, 6]]],
           [3, [[2, 2], [2, 3]]], [3, [[2, 5], [3, 5]]],
           [240, [[3, 1], [3, 2], [4, 1], [4, 2]]], [6, [[3, 3], [3, 4]]],
           [6, [[4, 3], [5, 3]]], [7, [[4, 4], [5, 4], [5, 5]]],
           [30, [[4, 5], [4, 6]]], [6, [[5, 1], [5, 2]]],
           [9, [[5, 6], [6, 6]]], [8, [[6, 1], [6, 2], [6, 3]]],
           [2, [[6, 4], [6, 5]]]]

# Model definition
model = cp.Model()

# Decision Variables: grid x (1-based values 1..n)
x = cp.intvar(1, n, shape=(n, n), name="x")

# Row and column all-different constraints
for i in range(n):
    model += cp.AllDifferent(*[x[i, j] for j in range(n)])  # row i
for j in range(n):
    model += cp.AllDifferent(*[x[i, j] for i in range(n)])  # column j

# Cage constraints
for tgt, cells in problem:
    # Convert to 0-based indices and gather variables
    vars_in_cage = [x[r-1, c-1] for r, c in cells]
    k = len(vars_in_cage)

    if k == 1:
        # Single cell must equal target
        model += (vars_in_cage[0] == tgt)
        continue

    # We'll allow addition and multiplication for any cage size.
    # Subtraction and division only for 2-cell cages (typical KenKen rules).
    ops_bools = []

    # Addition option: sum equals target
    add_b = cp.boolvar()
    ops_bools.append(add_b)
    model += add_b.implies(cp.sum(vars_in_cage) == tgt)

    # Multiplication option: product equals target
    mul_b = cp.boolvar()
    ops_bools.append(mul_b)
    # build product expression
    prod_expr = vars_in_cage[0]
    for v in vars_in_cage[1:]:
        prod_expr = prod_expr * v
    model += mul_b.implies(prod_expr == tgt)

    if k == 2:
        a, b = vars_in_cage
        # Subtraction option: absolute difference equals target
        sub_b = cp.boolvar()
        ops_bools.append(sub_b)
        model += sub_b.implies(cp.Abs(a - b) == tgt)

        # Division option: one divided by the other equals target (integer division)
        div_b = cp.boolvar()
        ops_bools.append(div_b)
        # a == b * tgt  or  b == a * tgt
        model += div_b.implies((a == b * tgt) | (b == a * tgt))

    # Exactly one operation must hold for this cage
    model += cp.sum(ops_bools) == 1

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
