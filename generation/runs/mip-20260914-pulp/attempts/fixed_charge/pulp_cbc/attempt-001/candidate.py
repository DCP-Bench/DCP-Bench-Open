import pulp


def build(instance):
    machines = range(instance["num_machines"])
    products = range(instance["num_products"])
    resources = range(len(instance["resources"]))
    renting_cost = instance["renting_cost"]
    capacity, ceiling = instance["capacity"], instance["max_production"]
    profit_and_machine, use = instance["product"], instance["use"]

    problem = pulp.LpProblem("fixed_charge", pulp.LpMaximize)
    rent = [pulp.LpVariable(f"rent_{m}", cat="Binary") for m in machines]
    produce = [pulp.LpVariable(f"produce_{p}", 0, ceiling, cat="Integer") for p in products]
    total = pulp.LpVariable("z", 0, 10000, cat="Integer")

    problem += total == (pulp.lpSum(profit_and_machine[p][0] * produce[p] for p in products)
                         - pulp.lpSum(renting_cost[m] * rent[m] for m in machines))
    for r in resources:
        problem += pulp.lpSum(use[p][r] * produce[p] for p in products) <= capacity[r]
    for p in products:
        # The reference pairs product p with machine p.
        problem += produce[p] <= ceiling * rent[p]
    problem += total
    return problem, {"z": total}
