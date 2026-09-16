import pulp


def build(instance):
    """Multicommodity transport: ship several products from origins to
    destinations, within per-product supply, per-pair capacity and demand, at
    minimum shipping cost.
    """
    supply = instance["supply"]
    demand = instance["demand"]
    limit = instance["limit"]
    cost = instance["cost"]
    origins = len(supply)
    destinations = len(demand)
    products = len(supply[0]) if origins else 0

    max_supply = max(max(row) for row in supply)
    supply_total = sum(sum(row) for row in supply)
    max_cost = max(value for matrix in cost for row in matrix for value in row)

    problem = pulp.LpProblem("multi", pulp.LpMinimize)
    x = pulp.LpVariable.dicts(
        "x", (range(origins), range(destinations), range(products)),
        0, max_supply, cat="Integer")

    for i in range(origins):
        for p in range(products):
            problem += pulp.lpSum(x[i][j][p] for j in range(destinations)) <= supply[i][p]
    for j in range(destinations):
        for p in range(products):
            problem += pulp.lpSum(x[i][j][p] for i in range(origins)) >= demand[j][p]
    for i in range(origins):
        for j in range(destinations):
            problem += pulp.lpSum(x[i][j][p] for p in range(products)) <= limit[i][j]

    total_cost = pulp.LpVariable("total_cost", 0, supply_total * max_cost, cat="Integer")
    problem += total_cost == pulp.lpSum(
        cost[i][j][p] * x[i][j][p]
        for i in range(origins) for j in range(destinations) for p in range(products)
    )
    problem += total_cost

    return problem, {"total_cost": total_cost}
