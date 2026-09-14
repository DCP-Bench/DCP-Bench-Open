import pulp


def build(instance):
    fixed_costs = instance["fixed_costs"]
    shipping = instance["shipping_costs"]
    demands = instance["demands"]
    capacity = instance["max_shipping"]
    warehouses, regions = range(len(fixed_costs)), range(len(demands))

    problem = pulp.LpProblem("facility_location", pulp.LpMinimize)
    is_open = [pulp.LpVariable(f"open_{i}", cat="Binary") for i in warehouses]
    ships = [[pulp.LpVariable(f"ships_{i}_{j}", 0, capacity, cat="Integer") for j in regions]
             for i in warehouses]
    total = pulp.LpVariable("total_cost", 0, 10000, cat="Integer")

    for i in warehouses:
        problem += pulp.lpSum(ships[i]) <= capacity * is_open[i]
    for j in regions:
        problem += pulp.lpSum(ships[i][j] for i in warehouses) >= demands[j]
    problem += total == pulp.lpSum(
        fixed_costs[i] * is_open[i] + pulp.lpSum(shipping[i][j] * ships[i][j] for j in regions)
        for i in warehouses)
    # The reference names the warehouses by position: 0 New York, 1 Los Angeles,
    # 2 Chicago, 3 Atlanta.
    problem += is_open[0] <= is_open[1]
    problem += pulp.lpSum(is_open) <= 3
    problem += is_open[3] + is_open[1] >= 1
    problem += total
    return problem, {"total_cost": total, "open_warehouse": is_open, "ships": ships}
