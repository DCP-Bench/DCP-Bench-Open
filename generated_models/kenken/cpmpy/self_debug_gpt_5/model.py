
import cpmpy as cp
import json
from itertools import product

# Data (optional)
n = 6

# For a better view of the problem, see
#  http://en.wikipedia.org/wiki/File:KenKenProblem.svg

# hints
#    [sum, [segments]]
# Note: 1-based
problem = [[11, [[1, 1], [2, 1]]], [2, [[1, 2], [1, 3]]],
           [20, [[1, 4], [2, 4]]], [6, [[1, 5], [1, 6], [2, 6], [3, 6]]],
           [3, [[2, 2], [2, 3]]], [3, [[2, 5], [3, 5]]],
           [240, [[3, 1], [3, 2], [4, 1], [4, 2]]], [6, [[3, 3], [3, 4]]],
           [6, [[4, 3], [5, 3]]], [7, [[4, 4], [5, 4], [5, 5]]],
           [30, [[4, 5], [4, 6]]], [6, [[5, 1], [5, 2]]],
           [9, [[5, 6], [6, 6]]], [8, [[6, 1], [6, 2], [6, 3]]],
           [2, [[6, 4], [6, 5]]]]

num_p = len(problem)
# End of data

# Helper to generate allowed tuples for a cage without specified operator
def allowed_tuples_for_cage(target, k, n):
    allowed = []
    dom = range(1, n+1)
    for tpl in product(dom, repeat=k):
        ok = False
        # addition
        if sum(tpl) == target:
            ok = True
        # multiplication
        prod_val = 1
        for v in tpl:
            prod_val *= v
        if prod_val == target:
            ok = True
        # subtraction and division only for pairs
        if k == 2:
            a, b = tpl
            if abs(a - b) == target:
                ok = True
            # exact integer division
            mx, mn = (a, b) if a >= b else (b, a)
            if mn != 0 and mx % mn == 0 and mx // mn == target:
                ok = True
        if k == 1:
            if tpl[0] == target:
                ok = True
        if ok:
            allowed.append(list(tpl))
    return allowed

# Model definition
model = cp.Model()

# Decision Variables
x = cp.intvar(1, n, shape=(n, n), name="x")

# Constraints

# Latin square constraints: rows and columns are permutations of 1..n
for i in range(n):
    model += cp.AllDifferent(x[i, :])
for j in range(n):
    model += cp.AllDifferent(x[:, j])

# Cage constraints (operator unknown: allow any of +, -, *, / as applicable)
for hint in problem:
    target, segments = hint
    cells = [x[r-1, c-1] for (r, c) in segments]
    k = len(cells)
    allowed = allowed_tuples_for_cage(target, k, n)
    # Safety: if allowed is empty, the problem is infeasible
    model += cp.Table(cells, allowed)

# Objective (optional)
# No objective for KenKen, just find a feasible solution

# Solve and print
if model.solve():
    solution = {'x': x.value().tolist()}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
