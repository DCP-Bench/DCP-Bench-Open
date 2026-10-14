"""Project Euler 2: the sum of the even Fibonacci terms that do not exceed four million."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data. The reference follows 35 terms, each in
# 0..10^7, and counts the terms below 4,000,000.
TERMS = 35
TERM_MAX = 10_000_000
LIMIT = 4_000_000
RES_MAX = 100_000_000


def build(instance):
    model = gp.Model("fibonacci_even")

    # f[i] is the i-th Fibonacci number: 0, 1, 1, then each the sum of the two before.
    f = [model.addVar(lb=0, ub=TERM_MAX, vtype=GRB.INTEGER, name=f"f[{i}]") for i in range(TERMS + 1)]
    model.addConstr(f[0] == 0, name="f0")
    model.addConstr(f[1] == 1, name="f1")
    model.addConstr(f[2] == 1, name="f2")
    for i in range(3, TERMS + 1):
        model.addConstr(f[i] == f[i - 1] + f[i - 2], name=f"fib[{i}]")

    # take[i] = 1 exactly when f[i] is even and below four million.
    total_parts = []
    for i in range(1, TERMS + 1):
        # f[i] = 2 half + odd, so odd = 1 exactly when f[i] is odd.
        half = model.addVar(lb=0, ub=TERM_MAX // 2, vtype=GRB.INTEGER, name=f"half[{i}]")
        odd = model.addVar(vtype=GRB.BINARY, name=f"odd[{i}]")
        model.addConstr(f[i] == 2 * half + odd, name=f"parity[{i}]")
        # below = 1 exactly when f[i] < 4,000,000.
        below = model.addVar(vtype=GRB.BINARY, name=f"below[{i}]")
        model.addConstr((below == 1) >> (f[i] <= LIMIT - 1), name=f"below_limit[{i}]")
        model.addConstr((below == 0) >> (f[i] >= LIMIT), name=f"at_limit[{i}]")
        take = model.addVar(vtype=GRB.BINARY, name=f"take[{i}]")
        model.addConstr(take <= below)
        model.addConstr(take <= 1 - odd)
        model.addConstr(take >= below - odd, name=f"take[{i}]")
        # part[i] is f[i] when the term is taken and 0 otherwise; indicator
        # constraints avoid a big-M of 10^7 next to a 1e-5 integrality tolerance.
        part = model.addVar(lb=0, ub=TERM_MAX, vtype=GRB.INTEGER, name=f"part[{i}]")
        model.addConstr((take == 1) >> (part == f[i]), name=f"counted[{i}]")
        model.addConstr((take == 0) >> (part == 0), name=f"skipped[{i}]")
        total_parts.append(part)

    # res is the sum of the taken terms.
    res = model.addVar(lb=0, ub=RES_MAX, vtype=GRB.INTEGER, name="res")
    model.addConstr(res == gp.quicksum(total_parts), name="sum_even_terms")

    return model, {"res": res}
