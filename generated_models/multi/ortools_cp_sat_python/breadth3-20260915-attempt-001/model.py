from ortools.sat.python import cp_model


def build(instance):
    supply, demand = instance["supply"], instance["demand"]
    limit, cost = instance["limit"], instance["cost"]
    origins, destinations, products = len(supply), len(demand), len(supply[0])
    ceiling = max(max(row) for row in supply)
    dearest = max(max(row) for matrix in cost for row in matrix)
    most = sum(sum(row) for row in supply) * dearest
    model = cp_model.CpModel()
    x = [[[model.new_int_var(0, ceiling, f"x_{i}_{j}_{p}") for p in range(products)]
          for j in range(destinations)] for i in range(origins)]
    total = model.new_int_var(0, most, "total_cost")
    for i in range(origins):
        for p in range(products):
            model.add(sum(x[i][j][p] for j in range(destinations)) <= supply[i][p])
    for j in range(destinations):
        for p in range(products):
            model.add(sum(x[i][j][p] for i in range(origins)) >= demand[j][p])
    for i in range(origins):
        for j in range(destinations):
            model.add(sum(x[i][j]) <= limit[i][j])
    model.add(total == sum(cost[i][j][p] * x[i][j][p]
                           for i in range(origins) for j in range(destinations)
                           for p in range(products)))
    model.minimize(total)
    return model, {"total_cost": total}
