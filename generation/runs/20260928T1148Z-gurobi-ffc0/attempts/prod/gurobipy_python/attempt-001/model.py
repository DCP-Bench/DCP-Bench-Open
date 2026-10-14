"""Production planning: choose production quantities within their limits and the time budget to maximise profit."""
import math

import gurobipy as gp
from gurobipy import GRB


def build(instance):
    a, c, u = instance["a"], instance["c"], instance["u"]
    products = range(len(a))

    model = gp.Model("prod")

    # x[j] is the quantity of product j, between 0 and u[j].
    x = model.addVars(products, lb=0, vtype=GRB.INTEGER, name="x")
    for j in products:
        x[j].UB = u[j]

    # Producing x[j] takes x[j] / a[j] of the budget b. Scaling both sides by the
    # least common multiple of the a[j] keeps every coefficient an integer, so the
    # check is exact rather than subject to floating-point tolerance.
    lcm_a = math.lcm(*a)
    model.addConstr(gp.quicksum((lcm_a // a[j]) * x[j] for j in products) <= instance["b"] * lcm_a,
                    name="budget")

    # Maximise the total profit.
    total_profit = gp.quicksum(c[j] * x[j] for j in products)
    model.setObjective(total_profit, GRB.MAXIMIZE)

    return model, {"x": [x[j] for j in products], "total_profit": total_profit}
