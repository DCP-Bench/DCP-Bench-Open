import json
from itertools import permutations
from math import gcd
from ortools.sat.python import cp_model

# ---------------------------------------------
# 1. Enumerate the 24 permutations of operations
# ---------------------------------------------
ops = ["+2", "/8", "-3", "*7"]
all_perms = list(permutations(ops))  # 24 permutations

# ------------------------------------------------------------
# 2. For every permutation compute coefficients (n,c,d) so that
#       f(x) = (n * x + c) / d
#    remains exact for integer x whenever d | (n*x+c)
# ------------------------------------------------------------

def perm_to_coeff(perm):
    n, c, d = 1, 0, 1  # represents (n*x + c) / d, initially x
    for op in perm:
        if op == "+2":
            # (n*x + c)/d  ->  (n*x + c + 2*d)/d
            c += 2 * d
        elif op == "-3":
            c -= 3 * d
        elif op == "*7":
            n *= 7
            c *= 7
        elif op == "/8":
            d *= 8
        else:
            raise ValueError("Unknown operation")
    g = gcd(gcd(abs(n), abs(c)), d)
    return n // g, c // g, d // g

coeff_cache = {perm: perm_to_coeff(perm) for perm in all_perms}

# ------------------------------------------------------------
# 3. Try every ordered pair of distinct permutations (p1,p2).
#    For each pair build a very small CP-SAT model with
#        a1*m + b1 = c1*h
#        a2*h + b2 = c2*m
#    and search for positive integer ages.
# ------------------------------------------------------------
AGE_MAX = 1000  # generous upper bound for human ages
found_m = None
found_h = None

for p1 in all_perms:
    for p2 in all_perms:
        if p1 == p2:
            continue  # sequences must be different

        a1, b1, c1 = coeff_cache[p1]  # h = (a1*m + b1)/c1
        a2, b2, c2 = coeff_cache[p2]  # m = (a2*h + b2)/c2

        model = cp_model.CpModel()
        m = model.NewIntVar(1, AGE_MAX, "m")
        h = model.NewIntVar(1, AGE_MAX, "h")

        model.Add(a1 * m + b1 == c1 * h)
        model.Add(a2 * h + b2 == c2 * m)

        solver = cp_model.CpSolver()
        status = solver.Solve(model)

        if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            found_m, found_h = solver.Value(m), solver.Value(h)
            # We have the ages – terminate both loops
            p1_used, p2_used = p1, p2  # just for potential debugging
            break
    if found_m is not None:
        break

if found_m is None:
    raise RuntimeError("No solution found – consider increasing AGE_MAX.")

# -------------------
# 4. Output as JSON
# -------------------
print(json.dumps({"m": found_m, "h": found_h}))