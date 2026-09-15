import z3


def build(instance):
    supply, demand = instance["supply"], instance["demand"]
    limit, cost = instance["limit"], instance["cost"]
    origins, destinations, products = len(supply), len(demand), len(supply[0])
    ceiling = max(max(row) for row in supply)
    dearest = max(max(row) for matrix in cost for row in matrix)
    most = sum(sum(row) for row in supply) * dearest
    x = [[[z3.Int(f"x_{i}_{j}_{p}") for p in range(products)]
          for j in range(destinations)] for i in range(origins)]
    flat = [x[i][j][p] for i in range(origins) for j in range(destinations) for p in range(products)]
    total = z3.Int("total_cost")
    constraints = [v >= 0 for v in flat] + [v <= ceiling for v in flat]
    constraints += [total >= 0, total <= most]
    for i in range(origins):
        for p in range(products):
            constraints.append(z3.Sum([x[i][j][p] for j in range(destinations)]) <= supply[i][p])
    for j in range(destinations):
        for p in range(products):
            constraints.append(z3.Sum([x[i][j][p] for i in range(origins)]) >= demand[j][p])
    for i in range(origins):
        for j in range(destinations):
            constraints.append(z3.Sum(x[i][j]) <= limit[i][j])
    constraints.append(total == z3.Sum([cost[i][j][p] * x[i][j][p]
                                        for i in range(origins) for j in range(destinations)
                                        for p in range(products)]))
    return constraints, {"total_cost": total}, ("minimize", total)
