import cpmpy as cp


def build(instance):
    machines, products = instance["num_machines"], instance["num_products"]
    resources = len(instance["resources"])
    renting_cost, capacity = instance["renting_cost"], instance["capacity"]
    ceiling, profit_and_machine, use = instance["max_production"], instance["product"], instance["use"]
    rent = cp.boolvar(shape=machines, name="rent")
    produce = cp.intvar(0, ceiling, shape=products, name="produce")
    total = cp.intvar(0, 10000, name="z")
    model = cp.Model(total == (cp.sum([profit_and_machine[p][0] * produce[p] for p in range(products)])
                               - cp.sum([renting_cost[m] * rent[m] for m in range(machines)])))
    for r in range(resources):
        model += cp.sum([use[p][r] * produce[p] for p in range(products)]) <= capacity[r]
    for p in range(products):
        # The reference pairs product p with machine p.
        model += produce[p] <= ceiling * rent[p]
    model.maximize(total)
    return model, {"z": total}
