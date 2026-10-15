# Multi-commodity transportation: ship each product from origins to destinations at minimum total cost, respecting supplies, demands and lane limits.
from paramita.modelling import Bool


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    limit = instance["limit"]
    cost = instance["cost"]
    n_o, n_d, n_p = len(supply), len(demand), len(supply[0])

    # Shipped amount x[i][j][p] is one-hot: xv[v] is true when the amount equals v.
    # Exactly one value holds for each triple, so the amount is the sum of v * xv[v].
    # The largest possible value is the smallest of the supply, demand and lane limit that apply to it.
    xv = {}
    x = [[[None] * n_p for _ in range(n_d)] for _ in range(n_o)]
    cons = []
    for i in range(n_o):
        for j in range(n_d):
            for p in range(n_p):
                ub = min(supply[i][p], demand[j][p], limit[i][j])
                vals = {v: Bool(f"x_{i}_{j}_{p}_eq{v}") for v in range(ub + 1)}
                xv[(i, j, p)] = vals
                cons.append(sum(vals.values()) == 1)
                x[i][j][p] = sum(v * b for v, b in vals.items())

    # Each origin i has a certain supply of each product p, and cannot ship more than that.
    for i in range(n_o):
        for p in range(n_p):
            cons.append(sum(x[i][j][p] for j in range(n_d)) <= supply[i][p])

    # Each destination j has a certain demand for each product p, and must receive exactly that.
    for j in range(n_d):
        for p in range(n_p):
            cons.append(sum(x[i][j][p] for i in range(n_o)) == demand[j][p])

    # Lane limit: the units sent from origin i to destination j, summed over all products, stay within limit[i][j].
    for i in range(n_o):
        for j in range(n_d):
            cons.append(sum(x[i][j][p] for p in range(n_p)) <= limit[i][j])

    # Total cost of shipping all products from the origins to the destinations.
    total = sum(cost[i][j][p] * x[i][j][p] for i in range(n_o) for j in range(n_d) for p in range(n_p))

    outputs = {"total_cost": total}
    return cons, outputs, ("minimize", total)
