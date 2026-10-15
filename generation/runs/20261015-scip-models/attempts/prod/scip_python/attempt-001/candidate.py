# Production planning: choose how many units X[j] of each product j to make so that
# the total profit is maximised, subject to the shared time budget b.

from pyscipopt import Model, quicksum


def build(instance):
    a = instance["a"]  # time needed per unit of product j
    c = instance["c"]  # profit per unit of product j
    u = instance["u"]  # maximum number of units of product j
    b = instance["b"]  # total time available
    P = range(len(a))

    m = Model()
    X = {j: m.addVar(name=f"X_{j}", vtype="I", lb=0, ub=u[j]) for j in P}

    # the sum of (1/a[j]) * X[j] over all products must be at most b
    m.addCons(quicksum((1.0 / a[j]) * X[j] for j in P) <= b)

    # the total profit is the sum of c[j] * X[j] over all products
    total_profit = m.addVar(name="total_profit", vtype="I", lb=0, ub=None)
    m.addCons(total_profit == quicksum(c[j] * X[j] for j in P))
    m.setObjective(total_profit, "maximize")

    # the production quantities are X[j]; the total profit is total_profit
    return m, {"total_profit": total_profit, "x": [X[j] for j in P]}
