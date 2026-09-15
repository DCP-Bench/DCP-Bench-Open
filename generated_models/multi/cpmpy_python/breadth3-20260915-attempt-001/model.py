import cpmpy as cp


def build(instance):
    supply, demand = instance["supply"], instance["demand"]
    limit, cost = instance["limit"], instance["cost"]
    origins, destinations, products = len(supply), len(demand), len(supply[0])
    ceiling = max(max(row) for row in supply)
    dearest = max(max(row) for matrix in cost for row in matrix)
    most = sum(sum(row) for row in supply) * dearest
    x = cp.intvar(0, ceiling, shape=(origins, destinations, products), name="x")
    total = cp.intvar(0, most, name="total_cost")
    model = cp.Model()
    for i in range(origins):
        for p in range(products):
            model += cp.sum([x[i, j, p] for j in range(destinations)]) <= supply[i][p]
    for j in range(destinations):
        for p in range(products):
            model += cp.sum([x[i, j, p] for i in range(origins)]) >= demand[j][p]
    for i in range(origins):
        for j in range(destinations):
            model += cp.sum([x[i, j, p] for p in range(products)]) <= limit[i][j]
    model += total == cp.sum([cost[i][j][p] * x[i, j, p]
                              for i in range(origins) for j in range(destinations)
                              for p in range(products)])
    model.minimize(total)
    return model, {"total_cost": total}
